
import argparse
import json
import pandas as pd
from app import score_batch_records

def main():
    parser = argparse.ArgumentParser(
        description="Campaign Intelligence CSV batch scorer"
    )
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", default="predictions.csv")
    parser.add_argument("--errors", default="validation_errors.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    records = df.astype(object).where(pd.notna(df), None).to_dict("records")

    response = score_batch_records(records)

    pd.DataFrame(response["results"]).to_csv(args.output, index=False)
    pd.DataFrame(response["errors"]).to_csv(args.errors, index=False)

    print(json.dumps({
        "input_rows": len(df),
        "valid_rows": response.get("valid_count", 0),
        "rejected_rows": response["rejected_count"],
        "selected_rows": response["selected_count"],
        "predictions_file": args.output,
        "errors_file": args.errors
    }, indent=4))

if __name__ == "__main__":
    main()
