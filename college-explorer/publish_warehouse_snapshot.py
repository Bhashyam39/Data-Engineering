import argparse
import json
import re
from datetime import datetime, timezone
from uuid import uuid4

from google.cloud import bigquery

from settings import (
    PROJECT_ID,
    LOCATION,
    PROJECT_ROOT,
    HISTORY_DATASET_ID,
    MARTS_DATASET_ID,
)


TABLES = [
    "institutions",
    "programs",
    "cip_fields",
    "credential_levels",
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-id", required=True)
    args = parser.parse_args()

    snapshot_id = args.snapshot_id

    if not re.fullmatch(r"s[0-9]{8}T[0-9]{6}_[0-9a-f]{8}", snapshot_id):
        raise SystemExit("Invalid snapshot ID.")

    snapshot_report_path = (
        PROJECT_ROOT
        / "reports"
        / "snapshots"
        / f"{snapshot_id}.json"
    )

    snapshot_report = json.loads(
        snapshot_report_path.read_text(encoding="utf-8")
    )

    if (
        snapshot_report.get("status") != "completed"
        or snapshot_report.get("snapshot_id") != snapshot_id
        or snapshot_report.get("history_dataset") != HISTORY_DATASET_ID
    ):
        raise SystemExit("Snapshot report is not eligible for publication.")

    expected_counts = snapshot_report["snapshot_counts"]

    sources = {
        name: f"{HISTORY_DATASET_ID}.{name}_{snapshot_id}"
        for name in TABLES
    }

    # Pin every catalog join directly to this snapshot version.
    catalog_sql = f"""
    SELECT
      p.unitid,
      i.name AS institution_name,
      i.city,
      i.state,
      i.ownership,
      p.cipcode,
      f.title AS field_of_study,
      p.credlev,
      c.title AS credential,
      p.debt_all_stgp_any_mdn,
      p.debt_all_stgp_any_mdn_status,
      p.earn_mdn_1yr,
      p.earn_mdn_1yr_status,
      p.earn_mdn_4yr,
      p.earn_mdn_4yr_status,
      p.earn_mdn_5yr,
      p.earn_mdn_5yr_status,
      i.source_run_id AS institution_source_run_id,
      p.source_zip AS program_source_zip,
      p.source_record,
      '{snapshot_id}' AS published_version
    FROM `{sources["programs"]}` p
    JOIN `{sources["institutions"]}` i
      ON p.unitid = i.unitid
    JOIN `{sources["cip_fields"]}` f
      ON p.cipcode = f.cipcode
    JOIN `{sources["credential_levels"]}` c
      ON p.credlev = c.credlev
    """

    report_folder = PROJECT_ROOT / "reports" / "publications"
    report_folder.mkdir(parents=True, exist_ok=True)

    publication_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        + "_"
        + uuid4().hex[:8]
    )
    report_path = report_folder / f"{publication_id}.json"

    report = {
        "snapshot_id": snapshot_id,
        "snapshot_report": str(
            snapshot_report_path.relative_to(PROJECT_ROOT)
        ),
        "marts_dataset": MARTS_DATASET_ID,
        "started_at_utc": utc_now(),
        "status": "running",
        "views": [],
    }

    try:
        client = bigquery.Client(
            project=PROJECT_ID,
            location=LOCATION,
        )

        # Check the preserved tables before changing any views.
        counts_sql = "\nUNION ALL\n".join(
            f"""
            SELECT '{name}' AS table_name, COUNT(*) AS row_count
            FROM `{sources[name]}`
            """
            for name in TABLES
        )

        actual_counts = {
            row["table_name"]: int(row["row_count"])
            for row in client.query(
                counts_sql, location=LOCATION
            ).result()
        }
        report["snapshot_counts"] = actual_counts

        if actual_counts != expected_counts:
            raise RuntimeError("Snapshot counts differ from its report.")

        candidate_sql = f"""
        WITH catalog AS ({catalog_sql})
        SELECT
          COUNT(*) AS program_rows,
          COUNT(DISTINCT unitid) AS institutions_with_programs,
          COUNT(DISTINCT TO_JSON_STRING(
            STRUCT(unitid, cipcode, credlev)
          )) AS unique_program_keys
        FROM catalog
        """

        candidate = dict(
            next(iter(client.query(
                candidate_sql, location=LOCATION
            ).result())).items()
        )
        report["candidate_catalog_checks"] = candidate

        if (
            candidate["program_rows"] != expected_counts["programs"]
            or candidate["unique_program_keys"] != expected_counts["programs"]
        ):
            raise RuntimeError("Candidate catalog validation failed.")

        dataset = bigquery.Dataset(MARTS_DATASET_ID)
        dataset.location = LOCATION
        client.create_dataset(dataset, exists_ok=True)

        actual_location = client.get_dataset(MARTS_DATASET_ID).location
        if actual_location.lower() != LOCATION.lower():
            raise RuntimeError("Marts dataset location mismatch.")

        definitions = {
            name: f"SELECT * FROM `{sources[name]}`"
            for name in TABLES
        }
        definitions["program_catalog"] = catalog_sql

        # Preserve the previous definitions in the publication report.
        from google.api_core.exceptions import NotFound

        report["previous_view_definitions"] = {}

        for name in definitions:
            view_id = f"{MARTS_DATASET_ID}.{name}"
            try:
                existing = client.get_table(view_id)
            except NotFound:
                report["previous_view_definitions"][name] = None
            else:
                if existing.table_type != "VIEW":
                    raise RuntimeError(f"Destination is not a view: {view_id}")
                report["previous_view_definitions"][name] = existing.view_query

        # Save the prior definitions before the first view update.
        report_path.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )

        for name, query in definitions.items():
            view_id = f"{MARTS_DATASET_ID}.{name}"
            sql = f"CREATE OR REPLACE VIEW `{view_id}` AS {query}"

            job = client.query(sql, location=LOCATION)
            entry = {
                "view_id": view_id,
                "job_id": job.job_id,
                "status": "running",
            }
            report["views"].append(entry)

            job.result()
            entry["status"] = "completed"
            print(f"Published: {view_id}")

        # Confirm the live catalog returns the validated version.
        verification_sql = f"""
        SELECT
          COUNT(*) AS program_rows,
          COUNT(DISTINCT unitid) AS institutions_with_programs,
          COUNTIF(published_version != '{snapshot_id}'
                  OR published_version IS NULL) AS wrong_version_rows
        FROM `{MARTS_DATASET_ID}.program_catalog`
        """

        published = dict(
            next(iter(client.query(
                verification_sql, location=LOCATION
            ).result())).items()
        )
        report["published_catalog_checks"] = published

        if (
            published["program_rows"] != candidate["program_rows"]
            or published["institutions_with_programs"]
            != candidate["institutions_with_programs"]
            or published["wrong_version_rows"] != 0
        ):
            raise RuntimeError("Published catalog validation failed.")
        
        source_config = snapshot_report["configuration"]
        status_updated_at = utc_now()

        # Encode source identifiers as SQL string literals.
        institution_run = json.dumps(
            source_config["institution_run_id"]
        )
        program_release = json.dumps(
            source_config["program_release"]
        )

        status_sql = f"""
        CREATE OR REPLACE VIEW `{MARTS_DATASET_ID}.data_status` AS
        SELECT
          '{snapshot_id}' AS published_version,
          TIMESTAMP('{status_updated_at}') AS status_updated_at_utc,
          {institution_run} AS institution_source_run_id,
          {program_release} AS program_source_release,
          {expected_counts["institutions"]} AS institution_rows,
          {expected_counts["programs"]} AS program_rows,
          {expected_counts["cip_fields"]} AS field_count,
          {expected_counts["credential_levels"]} AS credential_count,
          {published["institutions_with_programs"]}
            AS institutions_with_programs
        """

        status_job = client.query(status_sql, location=LOCATION)
        status_job.result()
        report["data_status_job_id"] = status_job.job_id

        status_row = dict(
            next(iter(client.query(
                f"SELECT * FROM `{MARTS_DATASET_ID}.data_status`",
                location=LOCATION,
            ).result())).items()
        )

        if status_row["published_version"] != snapshot_id:
            raise RuntimeError("Data-status version mismatch.")

        print(f"Updated: {MARTS_DATASET_ID}.data_status")

        report["status"] = "completed"
        print(json.dumps(published, indent=2))
        print("Publication validation: PASSED")

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

        print(f"\nPublished version: {snapshot_id}")
        print(f"Status: {report['status']}")
        print(f"Report: {report_path}")


if __name__ == "__main__":
    main()