from pathlib import Path
from zipfile import ZipFile

import pandas as pd
from settings import PROGRAM_BRONZE


FOLDER = PROGRAM_BRONZE
CSV_NAME = "Most-Recent-Cohorts-Field-of-Study.csv"

KEY_COLUMNS = ["UNITID", "CIPCODE", "CREDLEV"]

SELECTED_COLUMNS = [
    "UNITID",
    "OPEID6",
    "INSTNM",
    "CONTROL",
    "MAIN",
    "CIPCODE",
    "CIPDESC",
    "CREDLEV",
    "CREDDESC",
    "DEBT_ALL_STGP_ANY_MDN",
    "EARN_MDN_1YR",
    "EARN_MDN_4YR",
    "EARN_MDN_5YR",
]

MISSING_TOKENS = {"", "NULL", "PrivacySuppressed"}


def main():
    zip_files = list(FOLDER.glob("*.zip"))

    if len(zip_files) != 1:
        raise SystemExit(
            f"Expected one ZIP in {FOLDER}; found {len(zip_files)}."
        )

    with ZipFile(zip_files[0]) as archive:
        # Match the CSV even if it is inside an archive subfolder.
        matches = [
            name
            for name in archive.namelist()
            if Path(name).name == CSV_NAME
            and not name.startswith("__MACOSX/")
        ]

        if len(matches) != 1:
            raise SystemExit("Could not identify exactly one program CSV.")

        with archive.open(matches[0]) as file:
            df = pd.read_csv(
                file,
                usecols=SELECTED_COLUMNS,
                dtype="string",
                keep_default_na=False,
                encoding="utf-8-sig",
            )

    print(f"Source ZIP: {zip_files[0].name}")
    print(f"Total CSV rows: {len(df):,}")

    # Use trimmed copies for inspection; leave the raw file unchanged.
    inspected = df.apply(lambda column: column.str.strip())

    print("\n--- DIAGNOSTIC CHECKS ---")

    outcome_columns = [
        "DEBT_ALL_STGP_ANY_MDN",
        "EARN_MDN_1YR",
        "EARN_MDN_4YR",
        "EARN_MDN_5YR",
    ]

    for column in outcome_columns:
        values = inspected[column]

        print(f"\nMost common values in {column}:")
        print(values.value_counts(dropna=False).head(10).to_string())

        # Conversion is only a diagnostic; raw strings remain unchanged.
        numeric = pd.to_numeric(values, errors="coerce")
        nonnumeric = values[numeric.isna()]

        print(f"Values that cannot be parsed as numbers: {len(nonnumeric):,}")
        print(
            nonnumeric.value_counts(dropna=False)
            .head(10)
            .to_string()
        )

    print("\nInstitution IDs that are not positive whole numbers:")
    ids = inspected["UNITID"]
    numeric_ids = pd.to_numeric(ids, errors="coerce")

    valid_ids = (
        numeric_ids.notna()
        & numeric_ids.gt(0)
        & numeric_ids.mod(1).eq(0)
    )

    print(f"Rows failing this check: {(~valid_ids).sum():,}")
    print(
        ids[~valid_ids]
        .value_counts(dropna=False)
        .head(10)
        .to_string()
    )

    print("\nRepeated-key examples:")
    repeated = inspected[
        inspected.duplicated(KEY_COLUMNS, keep=False)
    ]

    if repeated.empty:
        print("None.")
    else:
        # Show complete groups for the first three repeated keys.
        example_keys = repeated[KEY_COLUMNS].drop_duplicates().head(3)
        examples = repeated.merge(
            example_keys,
            on=KEY_COLUMNS,
            how="inner",
        )

        display_columns = [
            "UNITID",
            "OPEID6",
            "INSTNM",
            "CIPCODE",
            "CREDLEV",
            "DEBT_ALL_STGP_ANY_MDN",
            "EARN_MDN_1YR",
        ]

        print(examples[display_columns].head(30).to_string(index=False))

    print("\n--- END DIAGNOSTIC CHECKS ---")

    print("\nMissing-value counts:")
    for column in SELECTED_COLUMNS:
        values = inspected[column]
        blank = values.eq("").sum()
        null = values.eq("NULL").sum()
        suppressed = values.eq("PrivacySuppressed").sum()

        print(
            f"{column}: blank={blank:,}, "
            f"NULL={null:,}, PrivacySuppressed={suppressed:,}"
        )

    missing_key = inspected[KEY_COLUMNS].isin(MISSING_TOKENS).any(axis=1)
    usable_keys = inspected.loc[~missing_key]

    print(f"\nRows missing a core identifier: {missing_key.sum():,}")
    print(f"Rows with all core identifiers: {len(usable_keys):,}")

    duplicate_groups = (
        usable_keys.groupby(KEY_COLUMNS, dropna=False)
        .size()
    )
    duplicate_groups = duplicate_groups[duplicate_groups > 1]

    print(f"Repeated key combinations: {len(duplicate_groups):,}")
    print(
        "Rows in repeated key combinations: "
        f"{int(duplicate_groups.sum()):,}"
    )

    print("\nCredential codes and descriptions:")
    print(
        inspected[["CREDLEV", "CREDDESC"]]
        .drop_duplicates()
        .sort_values(["CREDLEV", "CREDDESC"])
        .to_string(index=False)
    )

    print("\nFirst five rows:")
    print(inspected[SELECTED_COLUMNS[:9]].head().to_string(index=False))


if __name__ == "__main__":
    main()