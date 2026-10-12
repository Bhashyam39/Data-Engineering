import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from google.cloud import storage


from settings import (
    PROJECT_ID,
    BUCKET_NAME,
    DATA_ROOT,
    INSTITUTION_BRONZE,
    PROGRAM_BRONZE,
    INSTITUTION_SILVER,
    PROGRAM_SILVER,
    RELATIONSHIP_SILVER,
)


SELECTED_FOLDERS = [
    INSTITUTION_BRONZE,
    PROGRAM_BRONZE,
    INSTITUTION_SILVER,
    PROGRAM_SILVER,
    RELATIONSHIP_SILVER,
]

ALLOWED_SUFFIXES = {".json", ".parquet", ".zip"}


def sha256_file(path):
    checksum = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            checksum.update(chunk)

    return checksum.hexdigest()


def main():
    # Confirm we are using the completed institution extraction.
    manifest_path = SELECTED_FOLDERS[0] / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if manifest.get("status") != "completed":
        raise SystemExit("Institution extraction is not completed.")

    files = []

    for folder in SELECTED_FOLDERS:
        if not folder.is_dir():
            raise SystemExit(f"Required folder not found: {folder}")

        folder_files = [
            path for path in folder.rglob("*")
            if path.is_file()
            and path.suffix.lower() in ALLOWED_SUFFIXES
        ]

        if not folder_files:
            raise SystemExit(f"No supported files found in: {folder}")

        files.extend(folder_files)

    files = sorted(set(files))

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)

    report = {
        "project_id": PROJECT_ID,
        "bucket": BUCKET_NAME,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "expected_files": len(files),
        "files": [],
    }

    try:
        with TemporaryDirectory() as temporary_folder:
            downloaded_path = Path(temporary_folder) / "cloud_copy"

            for index, local_path in enumerate(files, start=1):
                # Forward slashes preserve the intended cloud paths.
                object_name = local_path.relative_to(DATA_ROOT).as_posix()
                local_hash = sha256_file(local_path)
                blob = bucket.blob(object_name)

                if blob.exists():
                    blob.reload()
                    action = "verified_existing"
                else:
                    blob.upload_from_filename(
                        str(local_path),
                        if_generation_match=0,
                    )
                    action = "uploaded"

                # Verify the exact cloud version observed above.
                blob.download_to_filename(
                    str(downloaded_path),
                    if_generation_match=int(blob.generation),
                )
                cloud_hash = sha256_file(downloaded_path)

                if cloud_hash != local_hash:
                    raise RuntimeError(
                        f"Contents differ for cloud object: {object_name}"
                    )

                report["files"].append({
                    "object_name": object_name,
                    "action": action,
                    "sha256": local_hash,
                    "generation": str(blob.generation),
                    "size_bytes": local_path.stat().st_size,
                })

                print(
                    f"[{index}/{len(files)}] "
                    f"{action}: {object_name}"
                )

        report["status"] = "completed"

    except Exception as exc:
        report["status"] = "failed"
        report["error_type"] = type(exc).__name__
        raise

    finally:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        report["verified_files"] = len(report["files"])

        report_folder = Path("reports")
        report_folder.mkdir(exist_ok=True)

        report_name = (
            datetime.now(timezone.utc).strftime("upload_%Y%m%dT%H%M%S")
            + "_" + uuid4().hex[:8] + ".json"
        )
        report_path = report_folder / report_name

        report_path.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )

        print(f"\nStatus: {report['status']}")
        print(
            f"Verified files: {report['verified_files']}"
            f"/{report['expected_files']}"
        )
        print(f"Report: {report_path}")


if __name__ == "__main__":
    main()