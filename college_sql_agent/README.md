# College Explorer Agentic SQL Assistant (MVP)

A local, read-only, human-approved natural-language-to-BigQuery SQL agent for the existing College & Program Explorer data engineering project.

## What it does

1. Reads the actual schemas of five `college_marts` tables.
2. Uses Gemini on Vertex AI to write GoogleSQL for a natural-language question.
3. Parses generated SQL to reject multiple statements, obvious modifications, and off-scope table references.
4. Uses BigQuery's **dry run** to validate syntax and estimate bytes processed.
5. Sends SQL errors back to Gemini for up to 3 repair attempts.
6. Displays generated SQL and requires you to type **YES** before executing.
7. Prints at most 20 result rows, without modifying the database.

This is an educational MVP. SQL parsing is not a complete security sandbox. **Use a separate least-privilege account**: `roles/bigquery.jobUser` on the project; `roles/bigquery.dataViewer` on the required dataset, plus appropriate Vertex AI access. Do not give the agent dataset write permissions or access to confidential data.

## Prerequisites

- Python 3.10+
- A GCP project with BigQuery dataset `college_marts` published
- Google Cloud CLI (`gcloud`)
- BigQuery API and Vertex AI API enabled
- Billing enabled, permissions to use the selected Gemini model in `us-central1`

### In PowerShell

Open your College Explorer environment or a new folder:

```powershell
cd path\to\college_sql_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Authenticate locally:

```powershell
gcloud config set project college-510602
gcloud auth application-default login
```

Enable APIs once (if not already enabled and if you have permission):

```powershell
gcloud services enable aiplatform.googleapis.com bigquery.googleapis.com --project=college-510602
```

Start the agent:

```powershell
python sql_agent.py
```

If model availability has changed, set an available Vertex AI Gemini model:

```powershell
$env:GEMINI_MODEL = "gemini-2.5-flash"
python sql_agent.py
```

## Starter questions

- "Show the 10 institutions with the largest student size, including their state."
- "Which institutions have the most program entries? Show the top 10."
- "For Texas, show institutions with in-state tuition and admission rate; exclude missing tuition."
- "Which credential levels appear in the published program catalog, and how many program rows correspond to each?"

**Use questions that the live schema can answer.** The agent discovers actual field names; this guide deliberately does not assume their names.

## Safety limits

- SQL is **not executed automatically**. Review queries before typing `YES`.
- Query execution has a maximum billed bytes limit of 1 GiB (`MAX_BYTES_BILLED`), and the query job has a timeout hint.
- Dry-run bytes estimate is approximate and **does not guarantee zero-cost execution**; BigQuery and Gemini usage can both incur charges.
- A preview with at most 20 displayed rows is not the same as adding SQL LIMIT and does not reduce scan cost.
- A valid SQL query can still be logically wrong, and generated answers need human verification.
- A separate, read-only GCP identity is essential; SQLGlot does not guarantee query safety.
- Some allowed tables could be views referencing underlying data. Validate their grants and definitions.

## Recommended next steps

- Add a business glossary for tuition, earnings, institution identifiers, and suppressed values.
- Write a test suite of 20 example questions with expected SQL behaviors.
- Save accepted SQL and execution metadata in a logging table (outside the agent's read-only identity).
- Wrap the agent in FastAPI, then add a Streamlit chat UI.
- Build a controlled tool-calling workflow with schema selection and query explanation.
- Deploy to Cloud Run with a dedicated service account only after tests and guardrails pass.

## Reference documentation

- Google Gen AI SDK: https://googleapis.github.io/python-genai/
- Google Cloud BigQuery Python query dry run: https://docs.cloud.google.com/bigquery/docs/running-queries
- BigQuery IAM: https://docs.cloud.google.com/bigquery/docs/access-control
- SQLGlot: https://sqlglot.com/
