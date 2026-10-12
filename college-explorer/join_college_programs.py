import json
from pathlib import Path

import pandas as pd

from settings import PROJECT_ROOT

from settings import (
    INSTITUTION_SILVER,
    PROGRAM_SILVER,
    RELATIONSHIP_SILVER,
)


INSTITUTION_FILE = (
    INSTITUTION_SILVER / "institutions_cleaned.parquet"
)

PROGRAM_FILE = (
    PROGRAM_SILVER
    / "outcome_cleaning_v1"
    / "programs_cleaned.parquet"
)

OUTPUT_FOLDER = RELATIONSHIP_SILVER


def main():
    institutions = pd.read_parquet(INSTITUTION_FILE)
    programs = pd.read_parquet(PROGRAM_FILE)

    # Standardize the join-column name.
    programs = programs.rename(columns={"UNITID": "unitid"})

    if institutions["unitid"].isna().any():
        raise SystemExit("Institution IDs contain nulls.")

    if institutions["unitid"].duplicated().any():
        raise SystemExit("Institution IDs are not unique.")

    program_keys = ["unitid", "CIPCODE", "CREDLEV"]

    if programs[program_keys].isna().any().any():
        raise SystemExit("Program identifiers contain nulls.")

    if programs.duplicated(program_keys).any():
        raise SystemExit("Program keys are not unique.")

    # Left join keeps every program, including unmatched records.
    linked = programs.merge(
        institutions[["unitid", "name", "state"]],
        on="unitid",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    if len(linked) != len(programs):
        raise SystemExit("The join changed the program row count.")

    matched_mask = linked["_merge"].eq("both")

    # Keep the program table separate from the institution table.
    matched = linked.loc[matched_mask, programs.columns].copy()
    unmatched = linked.loc[~matched_mask, programs.columns].copy()

    unmatched["exclusion_reason"] = (
        "unitid_not_in_operating_institution_extract"
    )

    institutions_with_programs = int(matched["unitid"].nunique())

    report = {
        "institution_input": str(INSTITUTION_FILE.relative_to(PROJECT_ROOT)),
        "program_input": str(PROGRAM_FILE.relative_to(PROJECT_ROOT)),
        "institutions": len(institutions),
        "program_input_rows": len(programs),
        "matched_program_rows": len(matched),
        "unmatched_program_rows": len(unmatched),
        "institutions_with_matching_programs": institutions_with_programs,
        "institutions_without_matching_programs": (
            len(institutions) - institutions_with_programs
        ),
        "unmatched_institution_ids": int(unmatched["unitid"].nunique()),
        "row_reconciliation_passed": (
            len(programs) == len(matched) + len(unmatched)
        ),
    }

    if not report["row_reconciliation_passed"]:
        raise SystemExit("Program row reconciliation failed.")

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    matched.to_parquet(
        OUTPUT_FOLDER / "programs_in_scope.parquet",
        index=False,
    )
    unmatched.to_parquet(
        OUTPUT_FOLDER / "programs_unmatched.parquet",
        index=False,
    )

    (OUTPUT_FOLDER / "quality_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    print(f"\nFiles saved to: {OUTPUT_FOLDER}")

    print("\nExample matched records:")
    print(
        linked.loc[
            matched_mask,
            ["unitid", "name", "state", "CIPDESC", "CREDDESC"],
        ].head(10).to_string(index=False)
    )

    if not unmatched.empty:
        print("\nExample unmatched institutions:")
        print(
            unmatched[["unitid", "INSTNM"]]
            .drop_duplicates()
            .head(10)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()