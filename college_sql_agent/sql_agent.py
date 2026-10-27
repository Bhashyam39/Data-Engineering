"""Read-only, approval-gated SQL agent for the GCP College & Program Explorer.

Install dependencies from requirements.txt and authenticate with Application
Default Credentials before running. This example is a learning MVP, not a
production security boundary. Use a least-privilege GCP identity.
"""

import json
import os
from typing import Tuple

from google import genai
from google.genai import types
from google.cloud import bigquery
import sqlglot
from sqlglot import exp


PROJECT_ID = os.getenv("GCP_PROJECT", "college-510602")
REGION = os.getenv("GCP_REGION", "us-central1")
DATASET_ID = os.getenv("BQ_DATASET", "college_marts")
MODEL_REGION = os.getenv("GEMINI_REGION", "global")
MODEL_ID = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Only tables already published to the curated serving/mart layer.
ALLOWED_TABLES = (
    "institutions",
    "programs",
    "program_catalog",
    "cip_fields",
    "credential_levels",
)
MAX_ATTEMPTS = 3
MAX_BYTES_BILLED = 1 * 1024**3  # 1 GiB per submitted query.
MAX_DISPLAY_ROWS = 20

SYSTEM_INSTRUCTIONS = """You write ONE GoogleSQL (BigQuery Standard SQL) SELECT query.
The user's database is a curated US college and program catalog.
Rules:
- Use only the exact tables and columns documented in the supplied live schema.
- Use fully qualified table references: `project.dataset.table`.
- SELECT and WITH ... SELECT (including read-only set operations) only.
- Never generate data modification, DDL, transactions, scripts, or remote queries.
- Do not query outside the published mart tables listed in the schema.
- Do not invent columns, values, or business definitions.
- Null tuition, admission rates, or outcomes mean missing, not zero.
- When a user asks for the 'top N', provide an explicit ORDER BY and LIMIT.
- For large detail listings, add LIMIT 20 unless the user specifies a smaller count.
- Respond with SQL text only: no Markdown fences, headings, or explanations.
"""


def load_schema(bq: bigquery.Client) -> str:
    """Read the ACTUAL schema, rather than trusting assumed field names."""
    descriptions = []
    for table_name in ALLOWED_TABLES:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        table = bq.get_table(table_id)
        fields = ", ".join(
            f"{col.name} {col.field_type}" for col in table.schema
        )
        descriptions.append(f"TABLE `{table_id}`\nCOLUMNS: {fields}")
    return "\n\n".join(descriptions)


def strip_code_fence(answer: str) -> str:
    """Tolerate SQL returned inside a Markdown code fence."""
    sql = (answer or "").strip()
    if sql.startswith("```"):
        lines = sql.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            sql = "\n".join(lines[1:-1]).strip()
    return sql.rstrip(";").strip()


def validate_read_only_sql(sql: str) -> str:
    """Reject obvious unsafe SQL and references to unapproved tables.

    Parser checks are defense-in-depth, NOT a sandbox. BigQuery IAM roles
    must also prohibit edits and reading unrelated datasets.
    """
    statements = sqlglot.parse(sql, read="bigquery")
    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Expected exactly one SQL statement.")

    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Union, exp.Except, exp.Intersect)):
        raise ValueError("Only SELECT queries and SELECT set operations are allowed.")

    forbidden = {
        "Insert", "Update", "Delete", "Merge", "Create", "Drop", "Alter",
        "TruncateTable", "Command", "Transaction", "Grant", "Revoke",
        "Execute", "Use", "Set", "Copy", "Export", "LoadData",
    }
    for node in tree.walk():
        if type(node).__name__ in forbidden:
            raise ValueError(f"Forbidden SQL operation: {type(node).__name__}.")
        # Reject cross-engine, cross-system calls. This list is intentionally
        # conservative and can be expanded with a stronger policy engine.
        if isinstance(node, exp.Anonymous) and node.name.upper() in {
            "EXTERNAL_QUERY", "REMOTE_QUERY", "EXPORT_DATA"
        }:
            raise ValueError(f"Forbidden SQL function: {node.name}.")

    cte_aliases = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    allowed = {name.lower() for name in ALLOWED_TABLES}
    for table in tree.find_all(exp.Table):
        name = table.name.lower()
        # A local CTE name is not a physical table reference.
        if name in cte_aliases and not table.db and not table.catalog:
            continue
        if (
            name not in allowed
            or (table.db and table.db.lower() != DATASET_ID.lower())
            or (table.catalog and table.catalog.lower() != PROJECT_ID.lower())
        ):
            raise ValueError(f"Unapproved table reference: {table.sql(dialect='bigquery')}")
    return sql


def draft_sql(ai: genai.Client, question: str, schema: str,
              last_error: str = "", previous_sql: str = "") -> str:
    prompt = f"DATABASE SCHEMA:\n{schema}\n\nUSER QUESTION:\n{question}"
    if last_error:
        prompt += (
            f"\n\nPREVIOUS SQL:\n{previous_sql}"
            f"\n\nVALIDATION ERROR:\n{last_error}"
            "\nFix the SQL using only the shown schema."
        )

    response = ai.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            temperature=0.1,
            max_output_tokens=3000,
        ),
    )
    if not response.text:
        raise RuntimeError("The model did not return SQL text.")
    return strip_code_fence(response.text)


def dry_run(bq: bigquery.Client, sql: str) -> int:
    """Ask BigQuery to parse/plan the query without running it."""
    config = bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
        maximum_bytes_billed=MAX_BYTES_BILLED,
    )
    job = bq.query(sql, job_config=config, location=REGION)
    return int(job.total_bytes_processed or 0)


def build_query(bq: bigquery.Client, ai: genai.Client,
                schema: str, question: str) -> Tuple[str, int]:
    last_error, previous_sql = "", ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\nGenerating SQL: attempt {attempt}/{MAX_ATTEMPTS}")
        sql = draft_sql(ai, question, schema, last_error, previous_sql)
        try:
            validate_read_only_sql(sql)
            bytes_processed = dry_run(bq, sql)
            if bytes_processed > MAX_BYTES_BILLED:
                raise ValueError("Dry-run estimate exceeded the query byte limit.")
            return sql, bytes_processed
        except Exception as error:
            # Feed only the error text and prior SQL back to the model.
            last_error, previous_sql = str(error)[:1200], sql
            print(f"Validation failed: {last_error}")
    raise RuntimeError("Unable to produce a validated SQL query after 3 tries.")


def run_approved_query(bq: bigquery.Client, sql: str) -> list[dict]:
    # IAM restrictions and maximum_bytes_billed are the main safeguards.
    config = bigquery.QueryJobConfig(
        use_legacy_sql=False,
        maximum_bytes_billed=MAX_BYTES_BILLED,
        job_timeout_ms=30000,
        labels={"app": "college-sql-agent"},
    )
    job = bq.query(sql, job_config=config, location=REGION)
    return [dict(row.items()) for row in job.result(max_results=MAX_DISPLAY_ROWS)]


def main() -> None:
    print("College Explorer SQL Agent (read-only MVP)")
    print(f"Project: {PROJECT_ID} | Dataset: {DATASET_ID} | Model: {MODEL_ID}")
    print("Loading live BigQuery table schemas...")

    bq = bigquery.Client(project=PROJECT_ID, location=REGION)
    ai = genai.Client(enterprise=True, project=PROJECT_ID, location=MODEL_REGION)
    schema = load_schema(bq)
    print("Loaded schema successfully. Type 'exit' to stop.")

    while True:
        question = input("\nAsk about colleges/programs: ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue
        try:
            sql, estimate = build_query(bq, ai, schema, question)
            print("\n=== GENERATED SQL (review before approval) ===")
            print(sql)
            print(f"\nBigQuery dry-run estimate: {estimate:,} bytes")
            print(f"Configured max bytes billed: {MAX_BYTES_BILLED:,}")
            approval = input("Run this SQL against BigQuery? Type YES: ").strip()
            if approval != "YES":
                print("Skipped. No query was executed.")
                continue

            rows = run_approved_query(bq, sql)
            print(f"\n=== RESULTS (first {MAX_DISPLAY_ROWS} rows maximum) ===")
            print(json.dumps(rows, indent=2, default=str))
            print("\nNote: rows shown are only a preview of the full query result.")
        except Exception as error:
            print(f"Agent error: {error}")
            print("Verify API access, permissions, live table names, and model availability.")


if __name__ == "__main__":
    main()
