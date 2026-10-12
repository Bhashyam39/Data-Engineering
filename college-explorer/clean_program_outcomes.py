import json
from pathlib import Path

import pandas as pd

from settings import PROGRAM_SILVER, PROJECT_ROOT


INPUT_FOLDER = PROGRAM_SILVER / "key_validation_v1"
OUTPUT_FOLDER = PROGRAM_SILVER / "outcome_cleaning_v1"

# Keep names close to the source until metric definitions are verified.
METRICS = {
    "DEBT_ALL_STGP_ANY_MDN": "debt_all_stgp_any_mdn",
    "EARN_MDN_1YR": "earn_mdn_1yr",
    "EARN_MDN_4YR": "earn_mdn_4yr",
    "EARN_MDN_5YR": "earn_mdn_5yr",
}

MISSING_STATUSES = {
    "PS": "privacy_suppressed",
    "PrivacySuppressed": "privacy_suppressed",
    "NA": "not_available",
    "NULL": "not_available",
    "": "blank",
}


def main():
    input_path = INPUT_FOLDER / "programs_candidate.parquet"

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    df = pd.read_parquet(input_path)

    keys = ["UNITID", "CIPCODE", "CREDLEV"]

    if df[keys].isna().any().any():
        raise SystemExit("Input contains null program identifiers.")

    if df.duplicated(keys).any():
        raise SystemExit("Input contains repeated program keys.")

    report = {
        "transformation_version": "outcome_cleaning_v1",
        "input_file": str(input_path.relative_to(PROJECT_ROOT)),
        "input_rows": len(df),
        "metrics": {},
    }

    for source_column, target_column in METRICS.items():
        raw = df[source_column].astype("string").str.strip()

        missing_status = raw.map(MISSING_STATUSES)
        recognized_missing = missing_status.notna()

        # Mask known missing markers before converting to numbers.
        numeric = pd.to_numeric(
            raw.mask(recognized_missing),
            errors="coerce",
        ).astype("Float64")

        # Unexpected text, negative values, or infinity require review.
        invalid = (
            (~recognized_missing & numeric.isna())
            | numeric.lt(0).fillna(False)
            | numeric.isin([float("inf"), float("-inf")])
        )

        if invalid.any():
            examples = raw.loc[invalid].value_counts().head(10)
            raise SystemExit(
                f"Unexpected values in {source_column}:\n"
                f"{examples.to_string()}\n"
                "No cleaned files were written by this execution."
            )

        status = missing_status.fillna("reported").astype("string")

                # Give the original text a distinct name.
        df = df.rename(
            columns={source_column: f"raw_{target_column}"}
        )

        df[target_column] = numeric
        df[f"{target_column}_status"] = status

        report["metrics"][target_column] = {
            "source_column": source_column,
            "status_counts": {
                str(label): int(count)
                for label, count in status.value_counts().items()
            },
            "null_count": int(numeric.isna().sum()),
        }

    report["output_rows"] = len(df)

    if report["input_rows"] != report["output_rows"]:
        raise RuntimeError("Outcome cleaning changed the row count.")

    
    normalized_names = pd.Index(
        [column.casefold() for column in df.columns]
    )

    if normalized_names.has_duplicates:
        raise SystemExit(
            "Column names conflict when capitalization is ignored."
        )


    # Write only after every selected metric passes validation.
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        OUTPUT_FOLDER / "programs_cleaned.parquet",
        index=False,
    )

    (OUTPUT_FOLDER / "quality_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    print(f"\nFiles saved to: {OUTPUT_FOLDER}")

    preview_columns = [
        "UNITID",
        "CIPCODE",
        "CREDLEV",
        "earn_mdn_1yr",
        "earn_mdn_1yr_status",
    ]

    print("\nExample cleaned records:")
    print(df[preview_columns].head(10).to_string(index=False))


if __name__ == "__main__":
    main()