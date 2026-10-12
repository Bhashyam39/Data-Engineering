import json
from pathlib import Path


# Locate the project from this file, independent of the terminal location.
PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_ROOT / "config" / "project.json"

CONFIG = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

REQUIRED_SETTINGS = [
    "project_id",
    "bucket_name",
    "location",
    "institution_run_id",
    "program_release",
    "program_download_folder",
    "relationship_version",
    "staging_dataset",
    "warehouse_dataset",
    "history_dataset",
    "marts_dataset",
]

for name in REQUIRED_SETTINGS:
    value = CONFIG.get(name)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing or invalid configuration setting: {name}")


PROJECT_ID = CONFIG["project_id"]
BUCKET_NAME = CONFIG["bucket_name"]
LOCATION = CONFIG["location"]

DATA_ROOT = PROJECT_ROOT / "data"

INSTITUTION_BRONZE = (
    DATA_ROOT / "bronze/institutions" / CONFIG["institution_run_id"]
)

PROGRAM_BRONZE = (
    DATA_ROOT / "bronze/programs" / CONFIG["program_download_folder"]
)

INSTITUTION_SILVER = (
    DATA_ROOT
    / "silver/institutions"
    / CONFIG["institution_run_id"]
    / "cleaning_v1"
)

PROGRAM_SILVER = (
    DATA_ROOT / "silver/programs" / CONFIG["program_release"]
)

RELATIONSHIP_SILVER = (
    DATA_ROOT
    / "silver/relationships"
    / CONFIG["relationship_version"]
)


STAGING_DATASET_ID = f"{PROJECT_ID}.{CONFIG['staging_dataset']}"
WAREHOUSE_DATASET_ID = f"{PROJECT_ID}.{CONFIG['warehouse_dataset']}"
HISTORY_DATASET_ID = f"{PROJECT_ID}.{CONFIG['history_dataset']}"
MARTS_DATASET_ID = f"{PROJECT_ID}.{CONFIG['marts_dataset']}"