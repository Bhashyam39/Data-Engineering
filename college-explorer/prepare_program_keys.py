import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
from settings import PROGRAM_SILVER

from profile_programs import (
    FOLDER,
    CSV_NAME,
    SELECTED_COLUMNS,
    KEY_COLUMNS,
)


def main():
    zip_files = list(FOLDER.glob("*.zip"))

    if len(zip_files) != 1:
        raise SystemExit("Expected exactly one source ZIP.")

    zip_path = zip_files[0]

    with ZipFile(zip_path) as archive:
        matches = [
            name for name in archive.namelist()
            if Path(name).name == CSV_NAME
            and not name.startswith("__MACOSX/")
        ]

        if len(matches) != 1:
            raise SystemExit("Expected exactly one matching CSV.")

        with archive.open(matches[0]) as file:
            df = pd.read_csv(
                file,
                usecols=SELECTED_COLUMNS,
                dtype="string",
                keep_default_na=False,
                encoding="utf-8-sig",
            )

    df = df.apply(lambda column: column.str.strip())

    # Number data records from 1, excluding the header.
    df["source_record"] = range(1, len(df) + 1)
    df["source_zip"] = zip_path.name
    df["rejection_reason"] = ""

    checks = {
        "invalid_unitid": df["UNITID"].str.fullmatch(r"[0-9]+"),
        "invalid_cipcode": df["CIPCODE"].str.fullmatch(r"[0-9]{4}"),
        "invalid_credlev": df["CREDLEV"].isin(
            ["1", "2", "3", "4", "5", "6", "7", "8", "99"]
        ),
    }

    # UNITID must also be positive.
    checks["invalid_unitid"] = (
        checks["invalid_unitid"]
        & pd.to_numeric(df["UNITID"], errors="coerce").gt(0)
    )

    # A record can have more than one rejection reason.
    for reason, valid in checks.items():
        invalid = ~valid.fillna(False)
        df.loc[invalid, "rejection_reason"] += reason + ";"

    rejected = df.loc[df["rejection_reason"].ne("")].copy()
    candidate = df.loc[df["rejection_reason"].eq("")].copy()

    candidate = candidate.drop(columns="rejection_reason")

    # Convert only after validating identifiers.
    candidate["UNITID"] = candidate["UNITID"].astype("int64")
    candidate["CREDLEV"] = candidate["CREDLEV"].astype("int64")

    # Keep CIPCODE as text to preserve codes such as 0109.
    repeated = candidate.duplicated(KEY_COLUMNS, keep=False)
    repeated_groups = (
        candidate.loc[repeated, KEY_COLUMNS]
        .drop_duplicates()
    )

    report = {
        "source_zip": zip_path.name,
        "raw_rows": len(df),
        "key_eligible_rows": len(candidate),
        "quarantined_rows": len(rejected),
        "repeated_key_groups_after_validation": len(repeated_groups),
        "rows_in_repeated_key_groups": int(repeated.sum()),
    }

    if len(df) != len(candidate) + len(rejected):
        raise RuntimeError("Row reconciliation failed.")

    if zip_path.stem != PROGRAM_SILVER.name:
        raise SystemExit(
            "Source ZIP does not match the configured program release: "
            f"{zip_path.stem} != {PROGRAM_SILVER.name}"
        )

    output = PROGRAM_SILVER / "key_validation_v1"

    output.mkdir(parents=True, exist_ok=True)

    candidate.to_parquet(
        output / "programs_candidate.parquet",
        index=False,
    )
    rejected.to_parquet(
        output / "programs_quarantine.parquet",
        index=False,
    )

    (output / "quality_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    print(f"\nFiles saved to: {output}")

    if repeated.any():
        print("Repeated valid keys still need investigation.")
    else:
        print("No repeated keys remain among key-eligible records.")


if __name__ == "__main__":
    main()