# Campaign Intelligence ML Service

## Purpose
Predict subscription probability, estimate call duration, and rank campaign
records under a 20% capacity policy.

## Project files
- api.py: FastAPI endpoints
- cli.py: CSV batch scoring
- artifacts/: trained models, schema, policy and hashes
- requirements.txt: Python dependencies

## Setup
```bash
pip install -r requirements.txt
```

## Start API
```bash
uvicorn api:app --host 127.0.0.1 --port 8000
```

## Endpoints
- GET /health
- POST /predict
- POST /predict-batch

Batch request format:
```json
{"records": [{"age": 35}]}
```
The example is abbreviated; all required feature fields must be supplied.

## CLI
```bash
python cli.py --input input.csv --output predictions.csv --errors errors.csv
```

## Important limitations
- Business value and call cost are teaching assumptions.
- Predictions are not treatment-effect estimates.
- Capacity selection is performed only for batches.
- Final-test performance has a documented leakage-demonstration limitation.
- Only load trusted model artifacts.
