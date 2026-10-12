import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from google.cloud import bigquery


from settings import (
    PROJECT_ID,
    LOCATION,
    PROJECT_ROOT,
    INSTITUTION_SILVER,
    RELATIONSHIP_SILVER,
    STAGING_DATASET_ID,
    WAREHOUSE_DATASET_ID,
)


SQL_FILE = PROJECT_ROOT / "sql" / "build_warehouse.sql"

INSTITUTION_REPORT = (
    INSTITUTION_SILVER / "quality_report.json"
)

RELATIONSHIP_REPORT = (
    RELATIONSHIP_SILVER / "quality_report.json"
)


def main():
    sql_bytes = SQL_FILE.read_bytes()
    sql = sql_bytes.decode("utf-8")

    replacements = {
        "{{STAGING_DATASET_ID}}": STAGING_DATASET_ID,
        "{{WAREHOUSE_DATASET_ID}}": WAREHOUSE_DATASET_ID,
        "{{LOCATION}}": LOCATION,
    }

    for placeholder, value in replacements.items():
        sql = sql.replace(placeholder, value)

    if "{{" in sql or "}}" in sql:
        raise ValueError("Warehouse SQL contains unresolved placeholders.")

    institutions = json.loads(
        INSTITUTION_REPORT.read_text(encoding="utf-8")
    )
    relationships = json.loads(
        RELATIONSHIP_REPORT.read_text(encoding="utf-8")
    )

    report = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "sql_file": str(SQL_FILE),
        "sql_sha256": hashlib.sha256(sql_bytes).hexdigest(),
        "expected_institutions": institutions["output_rows"],
        "expected_programs": relationships["matched_program_rows"],
        "project_id": PROJECT_ID,
        "staging_dataset_id": STAGING_DATASET_ID,
        "warehouse_dataset_id": WAREHOUSE_DATASET_ID,
        "rendered_sql_sha256": hashlib.sha256(sql.encode("utf-8")).hexdigest(),
    }

    try:
        client = bigquery.Client(
            project=PROJECT_ID,
            location=LOCATION,
        )

        config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(
                    "expected_institutions",
                    "INT64",
                    report["expected_institutions"],
                ),
                bigquery.ScalarQueryParameter(
                    "expected_programs",
                    "INT64",
                    report["expected_programs"],
                ),
            ]
        )

        job = client.query(
            sql,
            job_config=config,
            location=LOCATION,
        )
        report["job_id"] = job.job_id

        counts = {
            row["table_name"]: int(row["row_count"])
            for row in job.result()
        }
        report["table_counts"] = counts

        if counts["institutions"] != report["expected_institutions"]:
            raise RuntimeError("Warehouse institution count mismatch.")

        if counts["programs"] != report["expected_programs"]:
            raise RuntimeError("Warehouse program count mismatch.")

        report["status"] = "completed"
        print(json.dumps(counts, indent=2))

    except Exception as exc:
        report["status"] = "failed"
        report["error_type"] = type(exc).__name__
        raise

    finally:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()

        folder = PROJECT_ROOT / "reports"
        folder.mkdir(parents=True, exist_ok=True)

        filename = (
            datetime.now(timezone.utc).strftime("warehouse_build_%Y%m%dT%H%M%S")
            + "_" + uuid4().hex[:8] + ".json"
        )
        report_path = folder / filename

        report_path.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )

        print(f"\nStatus: {report['status']}")
        print(f"Report: {report_path}")


if __name__ == "__main__":
    main()