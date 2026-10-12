import os
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import hashlib

from settings import CONFIG, CONFIG_FILE


PROJECT_ROOT = Path(__file__).resolve().parent

STEPS = [
    "prepare_program_keys.py",
    "clean_program_outcomes.py",
    "clean_institutions.py",
    "join_college_programs.py",
    "upload_pipeline_data.py",
    "load_bigquery_staging.py",
    "build_warehouse.py",
    "create_warehouse_snapshot.py",
    "publish_warehouse_snapshot.py"
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def save_report(path, report):
    path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )


def main():

    config_bytes = CONFIG_FILE.read_bytes()

    if json.loads(config_bytes.decode("utf-8")) != CONFIG:
        raise RuntimeError(
            "Configuration changed after settings were loaded. "
            "Restart the pipeline."
        )

    config_sha256 = hashlib.sha256(config_bytes).hexdigest()

    # Check every script exists before starting any work.
    missing = [
        name for name in STEPS
        if not (PROJECT_ROOT / name).is_file()
    ]

    if missing:
        raise SystemExit(f"Missing scripts: {missing}")

    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        + "_" + uuid4().hex[:8]
    )
    snapshot_id = f"s{run_id}"

    run_folder = PROJECT_ROOT / "reports" / "pipeline" / run_id
    run_folder.mkdir(parents=True, exist_ok=False)
    report_path = run_folder / "run_report.json"

    config_copy_path = run_folder / "project_config.json"
    config_copy_path.write_bytes(config_bytes)

    report = {
        "run_id": run_id,
        "mode": "replay_saved_sources",
        "started_at_utc": utc_now(),
        "status": "running",
        "steps": [],
        "snapshot_id": snapshot_id,
        "configuration": {
            "file": config_copy_path.name,
            "sha256": config_sha256,
            "settings": json.loads(config_bytes.decode("utf-8")),
        },

        "snapshot_id": snapshot_id,
    }

    save_report(report_path, report)
    pipeline_started = time.perf_counter()

    try:
        for number, script_name in enumerate(STEPS, start=1):
            current_sha256 = hashlib.sha256(
                CONFIG_FILE.read_bytes()
            ).hexdigest()

            if current_sha256 != config_sha256:
                raise RuntimeError(
                    "Configuration changed during execution. "
                    "Pipeline stopped before the next step."
                )

            print(f"\nStep {number}/{len(STEPS)}: {script_name}")

            log_path = run_folder / f"{number:02d}_{script_name}.log"
            step = {
                "script": script_name,
                "status": "running",
                "started_at_utc": utc_now(),
                "log_file": log_path.name,
            }

            report["steps"].append(step)
            save_report(report_path, report)
            step_started = time.perf_counter()
            command = [sys.executable, "-u", script_name]

            if script_name in {
                "create_warehouse_snapshot.py",
                "publish_warehouse_snapshot.py",
            }:
                command.extend(["--snapshot-id", snapshot_id])

            step["command"] = command

            with log_path.open("w", encoding="utf-8") as log_file:
                process = subprocess.Popen(
                    command,
                    cwd=PROJECT_ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env={
                        **os.environ,
                        "PYTHONIOENCODING": "utf-8",
                    },
                )

                try:
                    for line in process.stdout:
                        print(line, end="")
                        log_file.write(line)

                    return_code = process.wait()

                finally:
                    if process.poll() is None:
                        process.terminate()
                        process.wait()

            step["finished_at_utc"] = utc_now()
            step["duration_seconds"] = round(
                time.perf_counter() - step_started, 2
            )
            step["return_code"] = return_code
            step["status"] = (
                "completed" if return_code == 0 else "failed"
            )
            save_report(report_path, report)

            if return_code != 0:
                raise RuntimeError(
                    f"{script_name} failed. See {log_path}"
                )

        report["status"] = "completed"

    except KeyboardInterrupt:
        report["status"] = "interrupted"
        if report["steps"][-1]["status"] == "running":
            report["steps"][-1]["status"] = "interrupted"
        raise

    except Exception as exc:
        report["status"] = "failed"
        report["error_type"] = type(exc).__name__

        if report["steps"][-1]["status"] == "running":
            report["steps"][-1]["status"] = "failed"

        raise

    finally:
        report["finished_at_utc"] = utc_now()
        report["duration_seconds"] = round(
            time.perf_counter() - pipeline_started, 2
        )
        report["completed_steps"] = sum(
            step["status"] == "completed"
            for step in report["steps"]
        )

        save_report(report_path, report)

        print(f"\nPipeline status: {report['status']}")
        print(
            f"Completed steps: "
            f"{report['completed_steps']}/{len(STEPS)}"
        )
        print(f"Run report: {report_path}")


if __name__ == "__main__":
    main()