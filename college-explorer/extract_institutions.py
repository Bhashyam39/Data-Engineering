import hashlib
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ENDPOINT = (
    "https://api.data.gov/ed/collegescorecard/v1/schools.json"
)
PER_PAGE = 100

FIELDS = [
    "id",
    "school.name",
    "school.city",
    "school.state",
    "school.school_url",
    "school.ownership",
    "latest.student.size",
    "latest.admissions.admission_rate.overall",
    "latest.cost.tuition.in_state",
    "latest.cost.tuition.out_of_state",
]

def save_manifest(path, manifest):
    """Save safely, retrying temporary Windows file locks."""
    temporary_path = path.with_suffix(".tmp")
    content = json.dumps(manifest, indent=2)

    for attempt in range(8):
        try:
            temporary_path.write_text(content, encoding="utf-8")
            temporary_path.replace(path)
            return
        except PermissionError:
            if attempt == 7:
                raise

            time.sleep(min(0.25 * (2 ** attempt), 2))


def fetch_page(session, page):
    params = {
        "school.operating": 1,
        "fields": ",".join(FIELDS),
        "page": page,
        "per_page": PER_PAGE,
        "sort": "id:asc",
    }

    response = session.get(
        ENDPOINT,
        params=params,
        timeout=(10, 60),
    )
    response.raise_for_status()

    payload = response.json()
    records = payload.get("results")
    metadata = payload.get("metadata")

    if not isinstance(records, list):
        raise ValueError(f"Page {page}: invalid results.")

    if not isinstance(metadata, dict):
        raise ValueError(f"Page {page}: missing metadata.")

    return response.content, records, metadata


def main():
    load_dotenv()
    api_key = os.getenv("SCORECARD_API_KEY")

    if not api_key:
        raise SystemExit("Add SCORECARD_API_KEY to your .env file.")

    started_at = datetime.now(timezone.utc)
    run_id = (
        started_at.strftime("%Y%m%dT%H%M%S")
        + "_"
        + uuid4().hex[:8]
    )

    output_dir = Path("data/bronze/institutions") / run_id
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest_path = output_dir / "manifest.json"

    manifest = {
        "run_id": run_id,
        "scope": "all_operating_institutions_core_fields",
        "status": "running",
        "source_url": ENDPOINT,
        "started_at_utc": started_at.isoformat(),
        "request_parameters": {
            "school.operating": 1,
            "fields": "id,school.name,school.city,school.state",
            "per_page": PER_PAGE,
            "sort": "id:asc",
        },
        "pages": [],
        "records_downloaded": 0,
    }
    save_manifest(manifest_path, manifest)

    # Retry temporary failures, but do not retry invalid credentials.
    retry_policy = Retry(
        total=4,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )

    seen_ids = set()

    try:
        with requests.Session() as session:
            session.headers.update({"X-Api-Key": api_key})
            session.mount(
                "https://",
                HTTPAdapter(max_retries=retry_policy),
            )

            page = 0
            expected_total = None
            page_count = None

            while page_count is None or page < page_count:
                if page > 0:
                    time.sleep(1)

                raw_bytes, records, metadata = fetch_page(session, page)

                # Keep each downloaded response for inspection.
                filename = f"page_{page:04d}.json"
                (output_dir / filename).write_bytes(raw_bytes)

                manifest["pages"].append({
                    "page": page,
                    "file": filename,
                    "record_count": len(records),
                    "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                })
                manifest["records_downloaded"] += len(records)
                save_manifest(manifest_path, manifest)

                source_total = metadata.get("total")
                if type(source_total) is not int or source_total <= 0:
                    raise ValueError("Invalid or empty source total.")

                if expected_total is None:
                    expected_total = source_total
                    page_count = math.ceil(expected_total / PER_PAGE)
                    manifest["source_total"] = expected_total
                    manifest["expected_pages"] = page_count

                if source_total != expected_total:
                    raise ValueError(
                        "Source total changed during extraction. "
                        "Start a fresh run."
                    )

                if metadata.get("page") != page:
                    raise ValueError("Returned page does not match request.")

                expected_rows = min(
                    PER_PAGE,
                    expected_total - page * PER_PAGE,
                )
                if len(records) != expected_rows:
                    raise ValueError(
                        f"Page {page}: expected {expected_rows} rows, "
                        f"received {len(records)}."
                    )

                for record in records:
                    unitid = record.get("id")

                    if type(unitid) is not int:
                        raise ValueError("Missing or invalid institution ID.")

                    if unitid in seen_ids:
                        raise ValueError(
                            f"Duplicate institution ID: {unitid}"
                        )

                    seen_ids.add(unitid)

                save_manifest(manifest_path, manifest)
                print(
                    f"Page {page + 1}/{page_count}: "
                    f"{len(records)} records saved"
                )
                page += 1

        if len(seen_ids) != expected_total:
            raise ValueError("Unique institution count does not match total.")

        manifest["status"] = "completed"
        manifest["unique_institutions"] = len(seen_ids)

    except Exception as exc:
        manifest["status"] = "failed"
        # Store the error category without potentially sensitive request details.
        manifest["error_type"] = type(exc).__name__
        print(f"\nExtraction failed: {exc}")
        raise

    finally:
        manifest["finished_at_utc"] = (
            datetime.now(timezone.utc).isoformat()
        )
        save_manifest(manifest_path, manifest)

    print(f"\nCompleted: {len(seen_ids)} unique institutions.")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()