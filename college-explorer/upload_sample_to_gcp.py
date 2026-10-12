import hashlib
from pathlib import Path

from google.cloud import storage


PROJECT_ID = "college-510602"
BUCKET_NAME = "sravan-college-lake-20261011"

LOCAL_FILE = Path(
    "data/bronze/institutions/"
    "20261011T053624_6b654257/manifest.json"
)

OBJECT_NAME = "verification/python/manifest.json"


def main():
    if not LOCAL_FILE.exists():
        raise SystemExit(f"Local file not found: {LOCAL_FILE}")

    local_bytes = LOCAL_FILE.read_bytes()
    local_hash = hashlib.sha256(local_bytes).hexdigest()

    # The library discovers your local application credentials.
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(OBJECT_NAME)

    if blob.exists():
        blob.reload()
        print("Object already exists; checking its contents.")
    else:
        # Create only if no live object exists at this address.
        blob.upload_from_string(
            local_bytes,
            content_type="application/json",
            if_generation_match=0,
        )
        print("Uploaded manifest.")

    # Read the specific object version we just observed or uploaded.
    downloaded_bytes = blob.download_as_bytes(
        if_generation_match=int(blob.generation)
    )
    downloaded_hash = hashlib.sha256(downloaded_bytes).hexdigest()

    if downloaded_hash != local_hash:
        raise SystemExit(
            "Verification failed: cloud and local contents differ."
        )

    print("SHA-256 verification: PASSED")
    print(f"Cloud object: gs://{BUCKET_NAME}/{OBJECT_NAME}")


if __name__ == "__main__":
    main()