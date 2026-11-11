
from pathlib import Path
import json
import math
import numpy as np
import pandas as pd
import joblib

from fastapi import FastAPI, HTTPException

ROOT = Path(__file__).parent
ARTIFACTS = ROOT / "artifacts"

app = FastAPI(title="Campaign Intelligence API", version="1.0")

# Load trusted artifacts once when the service starts
try:
    subscription_model = joblib.load(
        ARTIFACTS / "subscription_model.joblib"
    )
    duration_model = joblib.load(
        ARTIFACTS / "duration_model.joblib"
    )
    schema = json.loads((ARTIFACTS / "schema.json").read_text())
    policy = json.loads((ARTIFACTS / "policy.json").read_text())
    ARTIFACT_STATUS = "loaded"
except Exception as exc:
    subscription_model = None
    duration_model = None
    schema = {}
    policy = {}
    ARTIFACT_STATUS = f"failed: {type(exc).__name__}"

FEATURES = schema.get("feature_columns", [])
NUMERIC = set(schema.get("numeric_columns", []))
CATEGORICAL = set(schema.get("categorical_columns", []))

def validate_record(record):
    errors = []
    warnings = []

    if not isinstance(record, dict):
        return None, ["record must be a JSON object"], warnings

    supplied = set(record.keys()) - {"record_id"}
    expected = set(FEATURES)

    missing = expected - supplied
    extra = supplied - expected

    if missing:
        errors.append(f"Missing fields: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected/forbidden fields: {sorted(extra)}")

    if errors:
        return None, errors, warnings

    clean = {}

    for col in FEATURES:
        value = record.get(col)

        if value is None:
            clean[col] = np.nan
            continue

        if col in NUMERIC:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(f"{col}: expected a numeric value or null")
                continue
            if not math.isfinite(float(value)):
                errors.append(f"{col}: NaN/Infinity is not accepted")
                continue
            clean[col] = float(value)

        elif col in CATEGORICAL:
            if not isinstance(value, str):
                errors.append(f"{col}: expected text or null")
                continue
            clean[col] = value

        else:
            clean[col] = value

    if "age" in clean and not pd.isna(clean["age"]):
        if clean["age"] <= 0:
            errors.append("age must be greater than zero")

    if "previously_contacted" in clean and not pd.isna(
        clean["previously_contacted"]
    ):
        if clean["previously_contacted"] not in (0, 1):
            errors.append("previously_contacted must be 0 or 1")

    if errors:
        return None, errors, warnings

    return clean, errors, warnings


def score_batch_records(records):
    if not isinstance(records, list):
        raise ValueError("records must be a list")

    if len(records) > 1000:
        raise ValueError("Maximum batch size is 1000")

    if not records:
        return {
            "results": [],
            "errors": [],
            "selected_count": 0,
            "capacity": 0,
            "rejected_count": 0,
            "policy_version": policy["policy_version"]
        }

    # Reject every row involved in a duplicate supplied ID
    ids = [
        str(r.get("record_id"))
        for r in records
        if isinstance(r, dict) and r.get("record_id") is not None
    ]
    duplicate_ids = {x for x in ids if ids.count(x) > 1}

    valid_rows = []
    errors = []

    for index, record in enumerate(records):
        row_id = (
            str(record.get("record_id"))
            if isinstance(record, dict) and record.get("record_id") is not None
            else f"request_row_{index + 1}"
        )

        if row_id in duplicate_ids:
            errors.append({
                "row": index,
                "record_id": row_id,
                "errors": ["Duplicate record_id in batch"]
            })
            continue

        clean, row_errors, warnings = validate_record(record)

        if row_errors:
            errors.append({
                "row": index,
                "record_id": row_id,
                "errors": row_errors
            })
        else:
            valid_rows.append({
                "row": index,
                "record_id": row_id,
                "features": clean,
                "warnings": warnings
            })

    results = []

    if valid_rows:
        X = pd.DataFrame(
            [r["features"] for r in valid_rows],
            columns=FEATURES
        )

        probabilities = subscription_model.predict_proba(X)[:, 1]
        durations = np.maximum(duration_model.predict(X), 0)

        # Stable ranking: probability descending, original order for ties
        order = np.lexsort((np.arange(len(probabilities)), -probabilities))
        ranks = np.empty(len(order), dtype=int)
        ranks[order] = np.arange(1, len(order) + 1)

        capacity = int(len(valid_rows) * policy["capacity"])
        selected_indices = set()

        for i in order[:capacity]:
            expected_value = (
                policy["positive_value"] * probabilities[i]
                - policy["call_cost"]
            )
            if expected_value > 0:
                selected_indices.add(int(i))

        for i, row in enumerate(valid_rows):
            results.append({
                "row": row["row"],
                "record_id": row["record_id"],
                "subscription_probability": float(probabilities[i]),
                "threshold_positive": bool(
                    probabilities[i] >= policy["threshold"]
                ),
                "predicted_duration_seconds": float(durations[i]),
                "rank": int(ranks[i]),
                "selected": i in selected_indices,
                "policy_version": policy["policy_version"],
                "warnings": row["warnings"]
            })

        results.sort(key=lambda x: x["row"])
    else:
        capacity = 0

    return {
        "results": results,
        "errors": errors,
        "valid_count": len(valid_rows),
        "rejected_count": len(errors),
        "selected_count": sum(r["selected"] for r in results),
        "capacity": capacity,
        "policy_version": policy["policy_version"]
    }


@app.get("/health")
def health():
    ready = (
        ARTIFACT_STATUS == "loaded"
        and subscription_model is not None
        and duration_model is not None
    )
    return {
        "ready": ready,
        "model_version": schema.get("model_version"),
        "schema_version": schema.get("schema_version"),
        "artifact_status": ARTIFACT_STATUS
    }


@app.post("/predict")
def predict(record: dict):
    if ARTIFACT_STATUS != "loaded":
        raise HTTPException(status_code=503, detail="Models are not ready")

    clean, errors, warnings = validate_record(record)

    if errors:
        raise HTTPException(status_code=422, detail=errors)

    X = pd.DataFrame([clean], columns=FEATURES)

    probability = float(subscription_model.predict_proba(X)[0, 1])
    duration = float(max(0, duration_model.predict(X)[0]))

    return {
        "subscription_probability": probability,
        "threshold_positive": probability >= policy["threshold"],
        "predicted_duration_seconds": duration,
        "model_version": schema["model_version"],
        "schema_version": schema["schema_version"],
        "policy_version": policy["policy_version"],
        "warnings": warnings,
        "note": "Capacity selection is available only for batch requests."
    }


@app.post("/predict-batch")
def predict_batch(payload: dict):
    if ARTIFACT_STATUS != "loaded":
        raise HTTPException(status_code=503, detail="Models are not ready")

    records = payload.get("records")

    if not isinstance(records, list):
        raise HTTPException(
            status_code=422,
            detail="Request must contain a records list"
        )

    if len(records) > 1000:
        raise HTTPException(status_code=413, detail="Maximum batch size is 1000")

    return score_batch_records(records)
