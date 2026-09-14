# 16-Week Data Engineering Roadmap
## September 7 – December 27, 2026

**Stack:** Recipe A — Industry Standard  
**Commitment:** 25 hours/week  
**Goal:** Job-ready Data Engineer by December 31, 2026

---

## Table of Contents

- [Week 1: SQL Foundations + Python API Script](#week-1)
- [Week 2: Snowflake + Advanced SQL](#week-2)
- [Week 3: Docker + Git + Project Polish](#week-3)
- [Week 4: Apache Iceberg + Data Modeling](#week-4)
- [Week 5: Airbyte — Ingestion Engineering](#week-5)
- [Week 6: dbt Core — Transformation](#week-6)
- [Week 7: dbt Advanced + Airbyte Integration](#week-7)
- [Week 8: Great Expectations — Data Quality](#week-8)
- [Week 9: Apache Airflow — Orchestration](#week-9)
- [Week 10: Airflow Production + Cosmos](#week-10)
- [Week 11: Terraform — Infrastructure as Code](#week-11)
- [Week 12: Streaming + CI/CD](#week-12)
- [Week 13: Capstone Design](#week-13)
- [Week 14: Capstone Build](#week-14)
- [Week 15: Capstone Polish + Blog](#week-15)
- [Week 16: Portfolio + Job Applications](#week-16)

---

## <a id="week-1"></a>Week 1: SQL Foundations + Python API Script
**Dates:** September 7 – 13  
**Theme:** Close the SQL gap. Build your first data script.

### Monday – Wednesday: SQL Crash Course
| Day | Topics | Hours |
|-----|--------|-------|
| Mon | SELECT, WHERE, AND/OR, IN, BETWEEN, ORDER BY, LIMIT | 4 |
| Tue | INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, NULL handling | 4 |
| Wed | Aggregation (COUNT, SUM, AVG, GROUP BY, HAVING), Subqueries | 4 |

**Deliverable:** `week-01/sql_notes.md` with 7 topics + 3 memory queries + problem log

### Thursday – Friday: Python Weather Script
| Day | Task | Hours |
|-----|------|-------|
| Thu | Build `fetch_weather()` with requests, logging, error handling | 4 |
| Fri | Add `save_to_csv()` with pathlib, csv.DictWriter, argparse | 4 |

**Deliverable:** `week-01/weather.py` — fetches 3 cities, saves to dated CSV

### Saturday – Sunday: Docker + Tests
| Day | Task | Hours |
|-----|------|-------|
| Sat | Write Dockerfile, requirements.txt, build and run container | 4 |
| Sun | Write `test_weather.py` with pytest + unittest.mock, format with black | 4 |

**Deliverable:** Dockerized script + passing tests + handwritten notes pushed

### Week 1 Repo Structure
```
week-01/
├── README.md
├── sql_notes.md
├── sql_notes_page*.jpg
├── weather.py
├── test_weather.py
├── Dockerfile
└── requirements.txt
```

---

## <a id="week-2"></a>Week 2: Snowflake + Advanced SQL
**Dates:** September 14 – 20  
**Theme:** Learn the warehouse. Write analytical SQL at scale.

### Monday: Snowflake Setup
- Sign up for Snowflake free trial
- Load TPC-H sample dataset (`SNOWFLAKE_SAMPLE_DATA.TPCH_SF1`)
- Explore tables: CUSTOMER, ORDERS, LINEITEM, PART, NATION, REGION
- **Deliverable:** Screenshot of first query results

### Tuesday: Window Functions
- `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`
- `RANK()`, `DENSE_RANK()`
- `LEAD()`, `LAG()`
- **Deliverable:** 3 window function queries in Snowflake worksheet

### Wednesday: CTEs (Common Table Expressions)
- `WITH` clause for multi-step queries
- Recursive CTEs (basics)
- **Deliverable:** Complex analytical query using CTEs

### Thursday: Query Optimization
- `EXPLAIN` and execution plans
- Micro-partitions, clustering keys
- Result caching, search optimization
- **Deliverable:** Cost audit report on a week's query spend

### Friday: Snowflake Badge Prep
- Snowflake Data Engineer badge practice exam
- Review architecture: warehouses, stages, pipes, streams, tasks
- **Deliverable:** Practice exam completed

### Saturday – Sunday: Polish + Push
- Document all queries in `week-02/sql_snowflake.md`
- Push to GitHub
- **Deliverable:** `week-02/` folder with notes + query screenshots

---

## <a id="week-3"></a>Week 3: Docker + Git + Project Polish
**Dates:** September 21 – 27  
**Theme:** Containerize everything. Professional Git workflow.

### Monday: Docker Deep Dive
- Multi-stage builds, layer caching
- `.dockerignore`
- Docker networking basics
- **Deliverable:** Optimized Dockerfile for weather script

### Tuesday: docker-compose
- Multi-service local stacks
- Postgres + your app running together
- **Deliverable:** `docker-compose.yml` with Postgres and weather-app

### Wednesday: Git Advanced
- Branching strategy (feature branches)
- Rebasing, resolving merge conflicts
- Conventional commits
- **Deliverable:** Clean commit history on GitHub

### Thursday: Python Data Libraries
- `polars` (modern pandas replacement)
- `pydantic` for data validation
- `pyarrow` for Parquet I/O
- **Deliverable:** Script that reads CSV → validates with Pydantic → writes Parquet

### Friday: Error Handling + Logging
- Structured logging with `logging` module
- Retry logic with `tenacity`
- Idempotency patterns
- **Deliverable:** Production-hardened weather script

### Saturday – Sunday: Project Polish
- READMEs for every folder
- Architecture diagrams (draw.io / Excalidraw)
- Pre-commit hooks (`black`, `isort`)
- **Deliverable:** Professional-looking GitHub profile

---

## <a id="week-4"></a>Week 4: Apache Iceberg + Data Modeling
**Dates:** September 28 – October 4  
**Theme:** Master the modern table format. Design schemas.

### Monday: Iceberg Architecture
- Manifest files, manifest lists, metadata files
- Snapshot isolation, time travel
- **Deliverable:** Diagram of Iceberg metadata layer

### Tuesday: Iceberg Catalogs
- REST Catalog (Apache Polaris, Nessie)
- Hive Metastore vs. Glue vs. REST
- **Deliverable:** Spin up local Iceberg with DuckDB or Tabular free tier

### Wednesday: Hidden Partitioning + Evolution
- Partition evolution without rewrite
- Schema evolution (add, drop, rename columns)
- **Deliverable:** Demo of partition evolution

### Thursday: Data Modeling
- Dimensional modeling: stars, snowflakes
- SCD Types 1, 2, 3
- Data Vault vs. Kimball vs. OBT
- **Deliverable:** Design schema for e-commerce analytics

### Friday: Snowflake + Iceberg Integration
- Iceberg tables in Snowflake
- External tables, hybrid tables
- **Deliverable:** Create Iceberg table, perform time-travel query

### Saturday – Sunday: Documentation
- `week-04/iceberg_notes.md`
- Architecture decision record (ADR)
- Push to GitHub

---

## <a id="week-5"></a>Week 5: Airbyte — Ingestion Engineering
**Dates:** October 5 – 11  
**Theme:** Move data without writing custom code.

### Monday: Airbyte Architecture
- Sources, destinations, connectors
- Sync modes: Full Refresh vs. Incremental
- Append vs. Deduped
- **Deliverable:** Deploy Airbyte OSS locally via Docker Compose

### Tuesday: Build First Connection
- PostgreSQL (source) → Snowflake (destination)
- Full refresh sync
- **Deliverable:** Working connection in Airbyte UI

### Wednesday: Incremental Sync + CDC
- Cursor fields, incremental append
- Debezium CDC connector
- **Deliverable:** Incremental sync configured

### Thursday: Custom Connectors
- Airbyte CDK (Python)
- Build connector for niche API
- **Deliverable:** Custom source connector pushed to repo

### Friday: dlt (data load tool)
- Lightweight Python-first alternative
- When to use dlt vs. Airbyte
- **Deliverable:** Same pipeline built with dlt for comparison

### Saturday – Sunday: Documentation
- `week-05/ingestion_notes.md`
- Architecture diagram
- Push to GitHub

---

## <a id="week-6"></a>Week 6: dbt Core — Transformation
**Dates:** October 12 – 18  
**Theme:** SQL-based data modeling. The industry standard.

### Monday: dbt Project Setup
- `dbt init`, `profiles.yml`, `dbt_project.yml`
- Connect dbt to Snowflake
- **Deliverable:** `dbt debug` passes

### Tuesday: Models
- Staging models (1:1 with raw)
- Intermediate models (business logic)
- Mart models (aggregated, dimensional)
- **Deliverable:** 5 staging + 3 intermediate + 2 mart models

### Wednesday: Sources, Refs, Macros
- `sources.yml`, `{{ ref() }}`, `{{ source() }}`
- Jinja macros for reusable logic
- **Deliverable:** 2 reusable macros

### Thursday: Tests + Docs
- Generic tests: `unique`, `not_null`, `relationships`
- Custom tests, `dbt-expectations`
- `dbt docs generate`, `dbt docs serve`
- **Deliverable:** 100% test coverage on mart models + hosted docs

### Friday: Snapshots
- SCD Type 2 with dbt snapshots
- `dbt snapshot` command
- **Deliverable:** Snapshot for slowly changing dimension

### Saturday – Sunday: Polish
- `week-06/dbt_project/` pushed to GitHub
- README with model diagram
- `dbt docs` screenshot

---

## <a id="week-7"></a>Week 7: dbt Advanced + Airbyte Integration
**Dates:** October 19 – 25  
**Theme:** Scale dbt. Connect ingestion to transformation.

### Monday: dbt Mesh
- Cross-project references
- Contracts, versions
- **Deliverable:** Split project into 2 linked projects

### Tuesday: Slim CI
- State comparison, deferral
- Only run changed models
- **Deliverable:** CI configured to run `dbt build --select state:modified+`

### Wednesday: Environments
- dev / staging / prod setup
- `profiles.yml` for multiple environments
- **Deliverable:** Deploy to dbt Cloud free tier

### Thursday: Airbyte → dbt Pipeline
- Airbyte syncs raw data
- dbt transforms raw → staging → mart
- **Deliverable:** End-to-end pipeline: source → warehouse → model

### Friday: Pre-commit + Linting
- `sqlfluff` for SQL linting
- `black`, `isort` for Python
- GitHub Actions for CI
- **Deliverable:** Pre-commit hooks running on every commit

### Saturday – Sunday: Documentation
- `week-07/` with architecture diagram
- Blog draft: "Building a dbt pipeline from scratch"

---

## <a id="week-8"></a>Week 8: Great Expectations — Data Quality
**Dates:** October 26 – November 1  
**Theme:** Trust your data. Validate at every stage.

### Monday: GX Architecture
- Expectations, Validators, Checkpoints, Data Docs
- Install GX, connect to Snowflake
- **Deliverable:** First expectation suite

### Tuesday: Built-in + Custom Expectations
- `expect_column_values_to_not_be_null`
- Custom expectations for business rules
- **Deliverable:** 10 expectations for your mart table

### Wednesday: GX + dbt Integration
- Run GX after dbt models
- `dbt test` vs. GX checkpoints
- **Deliverable:** Pipeline: dbt run → GX checkpoint

### Thursday: Checkpoint Actions
- Slack/email alerts on failure
- Validation operators
- **Deliverable:** Alert on data quality failure

### Friday: Data Profiling
- `OnboardingDataAssistant`
- Auto-generated data docs
- **Deliverable:** Profile of raw data

### Saturday – Sunday: Quality-Gated Pipeline
- Airbyte → dbt → GX → alert
- `week-08/` documentation
- Push to GitHub

---

## <a id="week-9"></a>Week 9: Apache Airflow — Orchestration
**Dates:** November 2 – 8  
**Theme:** Schedule and manage pipelines.

### Monday: Airflow Architecture
- Scheduler, webserver, worker, metadata DB
- Deploy with Docker Compose
- **Deliverable:** Airflow UI running locally

### Tuesday: First DAGs
- `PythonOperator`, `BashOperator`
- TaskFlow API
- **Deliverable:** 3 simple DAGs

### Wednesday: Sensors + Dependencies
- File sensors, external task sensors
- Task groups, dynamic task mapping
- **Deliverable:** DAG with sensor + dynamic tasks

### Thursday: Airflow + dbt
- `BashOperator` for dbt commands
- dbt Cosmos integration
- **Deliverable:** DAG that runs dbt models

### Friday: Retries + SLAs
- Retry logic, timeouts
- Email/Slack notifications
- **Deliverable:** Production-hardened DAG

### Saturday – Sunday: Documentation
- `week-09/dags/` pushed to GitHub
- DAG diagram
- README with run instructions

---

## <a id="week-10"></a>Week 10: Airflow Production + Cosmos
**Dates:** November 9 – 15  
**Theme:** Enterprise-grade orchestration.

### Monday: Variables + Connections
- Airflow variables, connections UI
- Secrets backend (AWS SSM, HashiCorp Vault)
- **Deliverable:** Secure connection management

### Tuesday: Cosmos Deep Dive
- dbt models as individual Airflow tasks
- Model-level observability
- **Deliverable:** Cosmos DAG with per-model retries

### Wednesday: Monitoring
- Grafana, StatsD, Prometheus basics
- DAG metrics dashboard
- **Deliverable:** Dashboard showing DAG metrics

### Thursday: Backfills + External Triggers
- Backfill a month of data
- External triggers, catchup
- **Deliverable:** Backfill DAG

### Friday: Airflow Comparison
- Airflow vs. Dagster vs. Prefect vs. Kestra
- Architecture decision record
- **Deliverable:** ADR document

### Saturday – Sunday: Production Airflow
- 3 DAGs with monitoring, alerts, backfill
- `week-10/` documentation
- Push to GitHub

---

## <a id="week-11"></a>Week 11: Terraform — Infrastructure as Code
**Dates:** November 16 – 22  
**Theme:** Provision cloud resources reproducibly.

### Monday: Terraform Basics
- HCL syntax, providers, resources
- Variables, outputs, state
- **Deliverable:** Local Terraform install, basic AWS resources

### Tuesday: Modules + Remote State
- Modular project structure
- S3 backend for state
- **Deliverable:** Modular Terraform project

### Wednesday: Snowflake Provider
- Warehouses, databases, roles, users
- Terraform your Snowflake setup
- **Deliverable:** Snowflake infrastructure as code

### Thursday: AWS Provider
- S3, IAM, VPC basics
- S3 bucket + IAM role for Airflow
- **Deliverable:** AWS infrastructure as code

### Friday: CI/CD for Infrastructure
- GitHub Actions: `terraform plan` on PR, `terraform apply` on merge
- **Deliverable:** CI/CD for infrastructure

### Saturday – Sunday: Infra Repo
- `week-11/terraform/` pushed to GitHub
- README with architecture diagram

---

## <a id="week-12"></a>Week 12: Streaming + CI/CD Polish
**Dates:** November 23 – 29  
**Theme:** Real-time data. Automate everything.

### Monday: Kafka Fundamentals
- Topics, partitions, brokers, consumers
- Local Kafka via Docker
- **Deliverable:** Kafka running locally

### Tuesday: Producers + Consumers
- Python producer/consumer with `confluent-kafka`
- Consumer groups
- **Deliverable:** Working producer/consumer pair

### Wednesday: Kafka Connect + CDC
- Debezium CDC source
- S3 sink connector
- **Deliverable:** CDC from Postgres to Kafka to S3

### Thursday: Stream Processing
- Flink SQL basics or RisingWave
- Simple aggregation on streaming data
- **Deliverable:** Streaming aggregation query

### Friday: CI/CD Polish
- GitHub Actions for dbt + Terraform
- Pre-commit hooks across all repos
- **Deliverable:** Automated CI/CD pipeline

### Saturday – Sunday: Hybrid Pipeline
- Batch ELT + streaming component
- `week-12/` documentation
- Push to GitHub

---

## <a id="week-13"></a>Week 13: Capstone Design
**Dates:** November 30 – December 6  
**Theme:** Design the flagship project.

### Monday: Requirements + Architecture
- Define data sources, transformations, outputs
- Draw architecture diagram
- **Deliverable:** Architecture diagram in draw.io

### Tuesday: Schema Design
- Raw, staging, intermediate, mart layers
- dbt model structure
- **Deliverable:** Complete schema design

### Wednesday: Terraform All Infrastructure
- Snowflake warehouse, database, roles
- S3 buckets, IAM roles
- **Deliverable:** All infra provisioned via Terraform

### Thursday: Airbyte Connections
- Postgres CDC → Snowflake
- API → Snowflake
- CSV → Snowflake
- **Deliverable:** All connections configured

### Friday: dbt Project Skeleton
- Initialize dbt project
- Create all model files (empty or stubbed)
- **Deliverable:** dbt project structure ready

### Saturday – Sunday: Documentation
- `week-13/` with full capstone design
- README with architecture, schema, runbook

---

## <a id="week-14"></a>Week 14: Capstone Build
**Dates:** December 7 – 13  
**Theme:** Build the end-to-end pipeline.

### Monday: Build Ingestion Layer
- Airbyte syncs running
- Verify data landing in Snowflake raw tables
- **Deliverable:** Raw data confirmed in warehouse

### Tuesday: Build dbt Models
- Staging models (all passing tests)
- Intermediate models
- **Deliverable:** Staging + intermediate complete

### Wednesday: Build Mart Models
- Final aggregated tables
- All tests passing
- **Deliverable:** Mart models with 100% test coverage

### Thursday: Integrate Airflow
- DAG orchestrating: Airbyte → dbt → GX
- Retries, alerts, SLAs configured
- **Deliverable:** Full DAG running end-to-end

### Friday: Add Great Expectations
- Checkpoints at raw and mart layers
- Alerts on failure
- **Deliverable:** Quality-gated pipeline

### Saturday – Sunday: Testing + Debugging
- Run full pipeline 5+ times
- Fix edge cases, idempotency issues
- **Deliverable:** Stable, repeatable pipeline

---

## <a id="week-15"></a>Week 15: Capstone Polish + Blog
**Dates:** December 14 – 20  
**Theme:** Make it shine. Tell the world.

### Monday: Add Iceberg Features
- Configure Iceberg tables
- Time-travel queries
- Schema evolution demo
- **Deliverable:** Iceberg features documented

### Tuesday: Build Dashboard
- Streamlit or Hex dashboard on mart tables
- KPIs: revenue, orders, customers
- **Deliverable:** Live dashboard

### Wednesday: Documentation
- Architecture diagrams
- Runbooks (how to debug, how to backfill)
- Data dictionary
- **Deliverable:** Complete project docs

### Thursday: Demo Video
- 3-minute Loom walking through the pipeline
- Show: source → warehouse → model → dashboard
- **Deliverable:** Video uploaded (unlisted YouTube or Loom)

### Friday: Write Blog Post
- "Building a Modern Data Stack from Scratch"
- Technical deep-dive on one component
- **Deliverable:** Blog post published (Medium, Dev.to, or personal site)

### Saturday – Sunday: Final Polish
- All repos cleaned up
- READMEs professional
- GitHub profile updated

---

## <a id="week-16"></a>Week 16: Portfolio + Job Applications
**Dates:** December 21 – 27  
**Theme:** Get hired.

### Monday: Resume
- 1 page, metrics-focused
- Use these bullets:
  - "Built end-to-end ELT pipeline ingesting 1M+ rows/day from PostgreSQL and REST APIs into Snowflake using Airbyte, orchestrated with Apache Airflow"
  - "Implemented dbt models with 95%+ test coverage and Great Expectations data quality checks"
  - "Provisioned cloud infrastructure (S3, Snowflake) using Terraform, enabling environment parity across dev/staging/prod"
- **Deliverable:** Resume in PDF + Markdown

### Tuesday: LinkedIn
- Headline: "Aspiring Data Engineer | Snowflake · dbt · Airflow · Iceberg"
- About section with project summary
- Featured section with repo links + blog
- **Deliverable:** Updated LinkedIn profile

### Wednesday: GitHub Profile
- Pin 3 best repos
- Profile README (optional but impressive)
- **Deliverable:** Professional GitHub profile

### Thursday – Friday: Apply
- 5 applications/day
- Target: Junior Data Engineer, Analytics Engineer, Data Analyst (pipeline focus)
- Job boards: LinkedIn, Indeed, Data Engineering Jobs
- **Deliverable:** 10+ applications sent

### Saturday: Interview Prep
- SQL: 5 problems on DataLemur
- System design: Draw your capstone architecture from memory
- Behavioral: Practice "Tell me about your capstone project"
- **Deliverable:** Confidence in whiteboarding

### Sunday: Rest + Plan
- Review what you built
- Identify weak spots for January follow-up
- **Deliverable:** Personal retrospectives document

---

## Weekly Time Commitment

| Day | Hours | Typical Schedule |
|-----|-------|-----------------|
| Monday–Friday | 3.5–4 hrs/day | 6:00–10:00 PM |
| Saturday | 5–6 hrs | Morning block |
| Sunday | 3–4 hrs | Morning/afternoon |
| **Weekly Total** | **25 hrs** | |

---

## Job-Ready Checklist (By December 31)

- [ ] GitHub: 3+ repos with clean code, architecture diagrams, READMEs
- [ ] Capstone: End-to-end ELT pipeline with documentation
- [ ] Blog: 1 technical write-up about your architecture
- [ ] SQL: 50+ problems solved (LeetCode / DataLemur)
- [ ] Certification: Snowflake Data Engineer badge (recommended)
- [ ] LinkedIn: Updated headline, project posts
- [ ] Resume: 1 page, metrics-focused bullets
- [ ] Demo: 2–3 minute video walking through your pipeline
- [ ] Applications: 50+ jobs applied

---

*Roadmap generated September 2026. Stack reflects current industry standards.*
