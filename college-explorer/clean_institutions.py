import hashlib
import json
from pathlib import Path
import pandas as pd
from settings import INSTITUTION_BRONZE, INSTITUTION_SILVER


INPUT_FOLDER = INSTITUTION_BRONZE
OUTPUT_FOLDER = INSTITUTION_SILVER

COLUMN_MAP = {
    "id": "unitid",
    "school.name": "name",
    "school.city": "city",
    "school.state": "state",
    "school.school_url": "url",
    "school.ownership": "ownership",
    "latest.student.size": "student_size",
    "latest.admissions.admission_rate.overall": "admission_rate",
    "latest.cost.tuition.in_state": "tuition_in_state",
    "latest.cost.tuition.out_of_state": "tuition_out_of_state",
}

NUMERIC_COLUMNS = [
    "unitid",
    "ownership",
    "student_size",
    "admission_rate",
    "tuition_in_state",
    "tuition_out_of_state",
]

INTEGER_COLUMNS = [
    "unitid",
    "ownership",
    "student_size",
]


def main():
    manifest = json.loads(
        (INPUT_FOLDER / "manifest.json").read_text(encoding="utf-8")
    )

    if manifest.get("status") != "completed":
        raise SystemExit("Only completed extractions can be processed.")

    pages = manifest["pages"]

    if len(pages) != manifest["expected_pages"]:
        raise SystemExit("Manifest page count does not match expectations.")

    page_numbers = [entry["page"] for entry in pages]

    if sorted(page_numbers) != list(range(manifest["expected_pages"])):
        raise SystemExit("Manifest contains missing or repeated pages.")

    records = []

    for entry in sorted(pages, key=lambda item: item["page"]):
        page_path = INPUT_FOLDER / entry["file"]
        raw_bytes = page_path.read_bytes()

        actual_checksum = hashlib.sha256(raw_bytes).hexdigest()

        if actual_checksum != entry["sha256"]:
            raise SystemExit(f"Checksum mismatch: {page_path.name}")

        payload = json.loads(raw_bytes)
        page_records = payload["results"]

        if len(page_records) != entry["record_count"]:
            raise SystemExit(f"Record-count mismatch: {page_path.name}")

        for record in page_records:
            missing_fields = set(COLUMN_MAP) - set(record)

            if missing_fields:
                raise SystemExit(
                    f"Missing fields in {page_path.name}: "
                    f"{sorted(missing_fields)}"
                )

            row = {
                target: record[source]
                for source, target in COLUMN_MAP.items()
            }
            row["source_page"] = page_path.name
            records.append(row)

    df = pd.DataFrame(records)

    expected_total = manifest["source_total"]

    if not (
        len(df)
        == manifest["records_downloaded"]
        == manifest["unique_institutions"]
        == expected_total
    ):
        raise SystemExit("Institution counts do not reconcile.")

    # Standardize text while preserving missing values.
    for column in ["name", "city", "state", "url"]:
        df[column] = (
            df[column].astype("string").str.strip().replace("", pd.NA)
        )

    # Convert numbers, stopping on unexpected source values.
    for column in NUMERIC_COLUMNS:
        original = df[column]
        numeric = pd.to_numeric(original, errors="coerce")

        unexpected = original.notna() & numeric.isna()

        if unexpected.any():
            raise SystemExit(f"Unexpected nonnumeric values in {column}.")

        if numeric.isin([float("inf"), float("-inf")]).any():
            raise SystemExit(f"Infinite values found in {column}.")

        df[column] = numeric.astype("Float64")

    for column in INTEGER_COLUMNS:
        if df[column].dropna().mod(1).ne(0).any():
            raise SystemExit(f"Fractional values found in {column}.")

        df[column] = df[column].astype("Int64")

    if df["unitid"].isna().any() or df["unitid"].le(0).any():
        raise SystemExit("Invalid institution IDs.")

    if df["unitid"].duplicated().any():
        raise SystemExit("Repeated institution IDs.")

    if df["name"].isna().any():
        raise SystemExit("Missing institution names.")

    if not df["ownership"].dropna().isin([1, 2, 3]).all():
        raise SystemExit("Unexpected ownership codes.")

    if not df["admission_rate"].dropna().between(0, 1).all():
        raise SystemExit("Admission rates outside the range 0–1.")

    for column in [
        "student_size",
        "tuition_in_state",
        "tuition_out_of_state",
    ]:
        if df[column].dropna().lt(0).any():
            raise SystemExit(f"Negative values found in {column}.")

    df["source_run_id"] = manifest["run_id"]

    report = {
        "transformation_version": "institution_cleaning_v1",
        "source_run_id": manifest["run_id"],
        "input_rows": len(records),
        "output_rows": len(df),
        "unique_institutions": int(df["unitid"].nunique()),
        "checksums_verified": len(pages),
        "null_counts": {
            column: int(df[column].isna().sum())
            for column in COLUMN_MAP.values()
        },
    }

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        OUTPUT_FOLDER / "institutions_cleaned.parquet",
        index=False,
    )

    (OUTPUT_FOLDER / "quality_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    print(f"\nFiles saved to: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()