import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4
import argparse, re

from google.cloud import bigquery

from settings import (
    PROJECT_ID,
    LOCATION,
    PROJECT_ROOT,
    CONFIG_FILE,
    CONFIG,
    WAREHOUSE_DATASET_ID,
    HISTORY_DATASET_ID,
    INSTITUTION_SILVER,
    RELATIONSHIP_SILVER,
)


TABLES = [
    "institutions",
    "programs",
    "cip_fields",
    "credential_levels",
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def get_counts(client, dataset_id, suffix=""):
    sql = "\nUNION ALL\n".join(
        f"""
        SELECT '{name}' AS table_name, COUNT(*) AS row_count
        FROM `{dataset_id}.{name}{suffix}`
        """
        for name in TABLES
    )

    return {
        row["table_name"]: int(row["row_count"])
        for row in client.query(sql, location=LOCATION).result()
    }


def main():
    config_bytes = CONFIG_FILE.read_bytes()

    if json.loads(config_bytes.decode("utf-8")) != CONFIG:
        raise RuntimeError("Configuration changed. Restart the script.")

    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-id")
    args = parser.parse_args()

    snapshot_id = args.snapshot_id or (
        "s"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        + "_"
        + uuid4().hex[:8]
    )

    if not re.fullmatch(r"s[0-9]{8}T[0-9]{6}_[0-9a-f]{8}", snapshot_id):
        raise SystemExit("Invalid snapshot ID.")

    report_folder = PROJECT_ROOT / "reports" / "snapshots"
    report_folder.mkdir(parents=True, exist_ok=True)
    report_path = report_folder / f"{snapshot_id}.json"

    report = {
        "snapshot_id": snapshot_id,
        "started_at_utc": utc_now(),
        "status": "running",
        "source_dataset": WAREHOUSE_DATASET_ID,
        "history_dataset": HISTORY_DATASET_ID,
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "configuration": CONFIG,
        "tables": [],
    }

    try:
        institutions = read_json(
            INSTITUTION_SILVER / "quality_report.json"
        )
        relationships = read_json(
            RELATIONSHIP_SILVER / "quality_report.json"
        )

        if not relationships.get("row_reconciliation_passed"):
            raise RuntimeError("Relationship reconciliation did not pass.")

        client = bigquery.Client(
            project=PROJECT_ID,
            location=LOCATION,
        )

        source_counts = get_counts(client, WAREHOUSE_DATASET_ID)
        report["source_counts"] = source_counts

        expected_counts = {
            "institutions": institutions["output_rows"],
            "programs": relationships["matched_program_rows"],
        }

        for name, expected in expected_counts.items():
            if source_counts[name] != expected:
                raise RuntimeError(f"Source count mismatch: {name}")

        for name in ["cip_fields", "credential_levels"]:
            if source_counts[name] == 0:
                raise RuntimeError(f"Empty reference table: {name}")

        dataset = bigquery.Dataset(HISTORY_DATASET_ID)
        dataset.location = LOCATION
        client.create_dataset(dataset, exists_ok=True)

        actual_location = client.get_dataset(
            HISTORY_DATASET_ID
        ).location

        if actual_location.lower() != LOCATION.lower():
            raise RuntimeError("History dataset location mismatch.")

        for name in TABLES:
            source_table = f"{WAREHOUSE_DATASET_ID}.{name}"
            snapshot_table = (
                f"{HISTORY_DATASET_ID}.{name}_{snapshot_id}"
            )

            sql = f"""
            CREATE SNAPSHOT TABLE `{snapshot_table}`
            CLONE `{source_table}`
            """

            job = client.query(sql, location=LOCATION)

            entry = {
                "source_table": source_table,
                "snapshot_table": snapshot_table,
                "job_id": job.job_id,
                "status": "running",
            }
            report["tables"].append(entry)

            job.result()
            entry["status"] = "completed"
            print(f"Created: {snapshot_table}")

        snapshot_counts = get_counts(
            client,
            HISTORY_DATASET_ID,
            suffix=f"_{snapshot_id}",
        )
        report["snapshot_counts"] = snapshot_counts

        if snapshot_counts != source_counts:
            raise RuntimeError("Snapshot counts do not match the warehouse.")

        report["status"] = "completed"
        print(json.dumps(snapshot_counts, indent=2))
        print("Snapshot validation: PASSED")

    except Exception as exc:
        report["status"] = "failed"
        report["error_type"] = type(exc).__name__
        report["error"] = str(exc)
        raise

    finally:
        report["finished_at_utc"] = utc_now()
        report_path.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )

        print(f"\nSnapshot ID: {snapshot_id}")
        print(f"Status: {report['status']}")
        print(f"Report: {report_path}")


if __name__ == "__main__":
    main()