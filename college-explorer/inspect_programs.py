import csv
import hashlib
import io
from pathlib import Path
from zipfile import ZipFile


def main():
    folder = Path("data/bronze/programs/20261011")
    zip_files = list(folder.glob("*.zip"))

    if len(zip_files) != 1:
        raise SystemExit(
            f"Expected exactly one ZIP in {folder}, "
            f"but found {len(zip_files)}."
        )

    zip_path = zip_files[0]

    # Calculate a fingerprint without loading the entire ZIP into memory.
    checksum = hashlib.sha256()

    with zip_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            checksum.update(chunk)

    print(f"ZIP filename: {zip_path.name}")
    print(f"Size: {zip_path.stat().st_size:,} bytes")
    print(f"SHA-256: {checksum.hexdigest()}")

    # Read files inside the ZIP without extracting or changing them.
    with ZipFile(zip_path) as archive:
        csv_names = [
            name
            for name in archive.namelist()
            if name.lower().endswith(".csv")
            and not name.startswith("__MACOSX/")
        ]

        if not csv_names:
            raise SystemExit("No CSV files found inside the ZIP.")

        print(f"\nCSV files found: {len(csv_names)}")

        for name in csv_names:
            print(f"\nCSV: {name}")

            with archive.open(name) as binary_file:
                with io.TextIOWrapper(
                    binary_file,
                    encoding="utf-8-sig",
                    newline="",
                ) as text_file:
                    reader = csv.reader(text_file)
                    headers = next(reader, None)

                    if headers is None:
                        print("This CSV is empty.")
                        continue

                    print(f"Column count: {len(headers)}")
                    print("Columns:")

                    for column in headers:
                        print(f"  {column}")

                    required = {"UNITID", "CIPCODE", "CREDLEV"}
                    missing = required - set(headers)

                    print(
                        "Core identifier columns: "
                        + (
                            f"missing {sorted(missing)}"
                            if missing
                            else "all present"
                        )
                    )


if __name__ == "__main__":
    main()