import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from google.cloud import bigquery

from settings import (
    PROJECT_ID,
    BUCKET_NAME,
    LOCATION,
    DATA_ROOT,
    PROJECT_ROOT,
    INSTITUTION_SILVER,
    RELATIONSHIP_SILVER,
    STAGING_DATASET_ID
)


DATASET_ID = STAGING_DATASET_ID

INSTITUTION_PATH = (
    INSTITUTION_SILVER / "institutions_cleaned.parquet"
)

PROGRAM_PATH = (
    RELATIONSHIP_SILVER / "programs_in_scope.parquet"
)



def read_report(data_path):
    report_path = data_path.parent / "quality_report.json"
    return json.loads(report_path.read_text(encoding="utf-8"))


def cloud_uri(local_path):
    object_name = local_path.relative_to(DATA_ROOT).as_posix()
    return f"gs://{BUCKET_NAME}/{object_name}"


def main():
    # Use the local quality reports as our expected counts.
    institution_report = read_report(INSTITUTION_PATH)
    relationship_report = read_report(PROGRAM_PATH)

    expected = {
        "institution_rows": institution_report["output_rows"],
        "program_rows": relationship_report["matched_program_rows"],
        "null_institution_keys": 0,
        "null_program_keys": 0,
        "duplicate_institution_groups": 0,
        "duplicate_program_groups": 0,
        "unmatched_program_rows": 0,
    }

    if not relationship_report.get("row_reconciliation_passed"):
        raise SystemExit("Local relationship reconciliation did not pass.")

    report = {
        "project_id": PROJECT_ID,
        "dataset_id": DATASET_ID,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "loads": [],
        "expected_checks": expected,
    }

    try:
        client = bigquery.Client(
            project=PROJECT_ID,
            location=LOCATION,
        )

        dataset = bigquery.Dataset(DATASET_ID)
        dataset.location = LOCATION
        client.create_dataset(dataset, exists_ok=True)

        actual_dataset = client.get_dataset(DATASET_ID)

        if actual_dataset.location.lower() != LOCATION:
            raise RuntimeError("Staging dataset is in the wrong location.")

        sources = [
            ("institutions", INSTITUTION_PATH),
            ("programs", PROGRAM_PATH),
        ]

        for table_name, source_path in sources:
            uri = cloud_uri(source_path)
            table_id = f"{DATASET_ID}.{table_name}"

            config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.PARQUET,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )

            job = client.load_table_from_uri(
                uri,
                table_id,
                job_config=config,
                location=LOCATION,
            )

            report["loads"].append({
                "table_id": table_id,
                "source_uri": uri,
                "job_id": job.job_id,
                "status": "running",
            })

            job.result()
            report["loads"][-1]["status"] = "completed"

            print(f"Loaded: {table_id}")

        sql = f"""
        SELECT
          (SELECT COUNT(*) FROM `{DATASET_ID}.institutions`)
            AS institution_rows,

          (SELECT COUNT(*) FROM `{DATASET_ID}.programs`)
            AS program_rows,

          (SELECT COUNTIF(unitid IS NULL)
           FROM `{DATASET_ID}.institutions`)
            AS null_institution_keys,

          (SELECT COUNTIF(
             unitid IS NULL OR CIPCODE IS NULL OR CREDLEV IS NULL
           ) FROM `{DATASET_ID}.programs`)
            AS null_program_keys,

          (SELECT COUNT(*) FROM (
             SELECT unitid
             FROM `{DATASET_ID}.institutions`
             GROUP BY unitid
             HAVING COUNT(*) > 1
           )) AS duplicate_institution_groups,

          (SELECT COUNT(*) FROM (
             SELECT unitid, CIPCODE, CREDLEV
             FROM `{DATASET_ID}.programs`
             GROUP BY unitid, CIPCODE, CREDLEV
             HAVING COUNT(*) > 1
           )) AS duplicate_program_groups,

          (SELECT COUNT(*)
           FROM `{DATASET_ID}.programs` p
           LEFT JOIN `{DATASET_ID}.institutions` i
             ON p.unitid = i.unitid
           WHERE i.unitid IS NULL)
            AS unmatched_program_rows
        """

        query_job = client.query(sql, location=LOCATION)
        report["validation_job_id"] = query_job.job_id

        row = next(iter(query_job.result()))
        actual = {key: int(value) for key, value in row.items()}
        report["actual_checks"] = actual

        failures = {
            key: {"expected": value, "actual": actual[key]}
            for key, value in expected.items()
            if actual[key] != value
        }

        if failures:
            report["failed_checks"] = failures
            raise RuntimeError("BigQuery staging validation failed.")

        report["status"] = "completed"
        print(json.dumps(actual, indent=2))
        print("Validation: PASSED")

    except Exception as exc:
        report["status"] = "failed"
        report["error_type"] = type(exc).__name__
        raise

    finally:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()

        folder = PROJECT_ROOT / "reports"
        folder.mkdir(parents=True, exist_ok=True)

        filename = (
            datetime.now(timezone.utc).strftime("bigquery_load_%Y%m%dT%H%M%S")
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