import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import requests
from dotenv import load_dotenv


def main():
    # Load local configuration.
    load_dotenv()

    api_key = os.getenv("SCORECARD_API_KEY")
    if not api_key:
        raise SystemExit("Add SCORECARD_API_KEY to your .env file.")

    endpoint = (
        "https://api.data.gov/ed/collegescorecard/v1/schools.json"
    )

    # Start with a few easy-to-inspect institution fields.
    params = {
        "school.operating": 1,
        "fields": "id,school.name,school.city,school.state",
        "page": 0,
        "per_page": 100,
        "sort": "id:asc",
    }

    # Send the key in a header, keeping it out of the request URL.
    try:
        response = requests.get(
            endpoint,
            headers={"X-Api-Key": api_key},
            params=params,
            timeout=(10, 60),
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit(f"API request failed: {exc}") from None

    try:
        payload = response.json()
    except ValueError:
        raise SystemExit("The API did not return valid JSON.") from None

    # Check the response before treating it as usable input.
    records = payload.get("results")
    metadata = payload.get("metadata")

    if not isinstance(records, list):
        raise SystemExit("Unexpected response: results is not a list.")

    if not isinstance(metadata, dict):
        raise SystemExit("Unexpected response: metadata is missing.")

    if not records:
        raise SystemExit("No institution records were returned.")

    # Give this extraction its own directory.
    extracted_at = datetime.now(timezone.utc)
    run_id = (
        extracted_at.strftime("%Y%m%dT%H%M%S")
        + "_"
        + uuid4().hex[:8]
    )

    output_dir = (
        Path("data") / "bronze" / "institutions" / run_id
    )
    output_dir.mkdir(parents=True, exist_ok=False)

    # Preserve the original response bytes.
    raw_path = output_dir / "page_0000.json"
    raw_path.write_bytes(response.content)

    # Save provenance without recording the API key.
    manifest = {
        "run_id": run_id,
        "scope": "sample_page",
        "source_url": endpoint,
        "request_parameters": params,
        "extracted_at_utc": extracted_at.isoformat(),
        "record_count": len(records),
        "source_total": metadata.get("total"),
        "sha256": hashlib.sha256(response.content).hexdigest(),
        "raw_file": raw_path.name,
    }

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print(f"Saved {len(records)} institution records.")
    print(f"Source reports {metadata.get('total')} matching institutions.")
    print(f"Raw file: {raw_path}")
    print(f"Manifest: {manifest_path}")

    print("\nFirst institution:")
    print(json.dumps(records[0], indent=2))


if __name__ == "__main__":
    main()