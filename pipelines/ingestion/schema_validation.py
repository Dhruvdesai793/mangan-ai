"""
Validates an incoming dataframe against a JSON Schema contract
(schemas/ingestion_contracts/team1_parquet_schema.json or team2_verified_schema.json).

Usage:
    from pipelines.ingestion.schema_validation import validate_dataframe
    good_df, bad_rows = validate_dataframe(df, "team1_parquet_schema.json")
"""
import json
import pathlib
import pandas as pd

SCHEMA_DIR = pathlib.Path(__file__).resolve().parents[2] / "schemas" / "ingestion_contracts"


def _load_schema(schema_name: str) -> dict:
    path = SCHEMA_DIR / schema_name
    with open(path) as f:
        return json.load(f)


def _row_errors(row: dict, required: list, properties: dict) -> list:
    errors = []
    for col in required:
        if col not in row or pd.isna(row[col]):
            errors.append(f"missing required field: {col}")
    for col, spec in properties.items():
        if col not in row or pd.isna(row.get(col)):
            continue
        val = row[col]
        t = spec.get("type")
        if t == "number" and not isinstance(val, (int, float)):
            errors.append(f"{col} should be numeric")
        if "minimum" in spec and isinstance(val, (int, float)) and val < spec["minimum"]:
            errors.append(f"{col}={val} below minimum {spec['minimum']}")
        if "maximum" in spec and isinstance(val, (int, float)) and val > spec["maximum"]:
            errors.append(f"{col}={val} above maximum {spec['maximum']}")
        if "enum" in spec and val not in spec["enum"]:
            errors.append(f"{col}={val} not in allowed values {spec['enum']}")
    return errors


def validate_dataframe(df: pd.DataFrame, schema_name: str = "team1_parquet_schema.json"):
    """Returns (valid_df, quarantined_rows_with_reasons)."""
    schema = _load_schema(schema_name)
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    valid_idx, bad_rows = [], []
    for idx, row in df.iterrows():
        errs = _row_errors(row.to_dict(), required, properties)
        if errs:
            bad_rows.append({"index": idx, "errors": errs})
        else:
            valid_idx.append(idx)

    valid_df = df.loc[valid_idx].reset_index(drop=True)
    return valid_df, bad_rows


if __name__ == "__main__":
    print("schema_validation.py: import and call validate_dataframe(df, schema_name)")
