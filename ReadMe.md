# 18-Week Combined Data Engineering Roadmap
## Snowflake + Databricks/PySpark — Based on 22,000 Real Job Ads
### September 14, 2026 – January 17, 2027

**Source:** Data with Baraa — *Data Engineer Roadmap: Built From 22,000 Real Job Ads*  
**Insight:** Job ads demand BOTH Snowflake AND Databricks skills. Don't choose — learn both.  
**Commitment:** 25 hours/week  
**Goal:** Job-ready Data Engineer by January 31, 2027

---

## Why Combined?

The video analyzed **22,000 real job ads** across 4,000+ companies. The data shows:

| Finding | What It Means for You |
|---------|----------------------|
| **Both Snowflake AND Databricks appear** in job postings | Learning only one limits your applications by 40–50% |
| **PySpark is the #1 big data skill** requested | You need it for Databricks, EMR, and any large-scale processing |
| **dbt is the standard transformation tool** | Works on Snowflake AND Databricks — learn once, use everywhere |
| **Two "tech stacks" dominate** | Stack A: Snowflake + dbt. Stack B: Databricks + PySpark. You need both. |
| **SQL is non-negotiable** | 90%+ of job ads mention SQL. It's the foundation of everything. |

**This roadmap combines both dominant stacks into one learning path.**

---

## Table of Contents

- [Phase 1: Python + SQL Foundations (Weeks 1–2)](#phase-1)
- [Phase 2: PySpark Foundations (Weeks 3–4)](#phase-2)
- [Phase 3: Snowflake + Databricks Side-by-Side (Weeks 5–7)](#phase-3)
- [Phase 4: dbt — The Universal Transformer (Weeks 8–9)](#phase-4)
- [Phase 5: Ingestion + Orchestration (Weeks 10–11)](#phase-5)
- [Phase 6: Infrastructure + Data Quality (Weeks 12–13)](#phase-6)
- [Phase 7: Streaming (Weeks 14–15)](#phase-7)
- [Phase 8: Capstone + Job Hunt (Weeks 16–18)](#phase-8)

---

## <a id="phase-1"></a>Phase 1: Python + SQL Foundations
### Weeks 1–2: September 14 – 27

**Theme:** You can't build pipelines without speaking the language.

### Week 1: Python for Data Engineering

| Day | Task | Hours |
|-----|------|-------|
| Mon | `polars` crash course: DataFrames, filters, joins, groupby | 4 |
| Tue | `pydantic` for data validation + `requests` for APIs | 4 |
| Wed | Build weather fetcher: API → clean → CSV/Parquet | 4 |
| Thu | Error handling, logging, `pathlib`, `csv.DictWriter` | 4 |
| Fri | Dockerize the script: `Dockerfile`, `docker-compose` | 4 |
| Sat | Write `pytest` tests with `unittest.mock` | 5 |
| Sun | Push `week-01/` to GitHub | 4 |

**Deliverable:** Containerized Python script with tests

### Week 2: SQL Mastery

| Day | Task | Hours |
|-----|------|-------|
| Mon | SELECT, WHERE, JOINs, NULL handling | 4 |
| Tue | Aggregation: GROUP BY, HAVING, window functions | 4 |
| Wed | CTEs, subqueries, LATERAL joins | 4 |
| Thu | Practice: 15 problems on DataLemur / HackerRank | 4 |
| Fri | Query optimization: `EXPLAIN`, indexes, execution plans | 4 |
| Sat | Build ShopStream dataset, write 10 analytical queries | 5 |
| Sun | Push `week-02/sql_notes.md` | 4 |

**Deliverable:** SQL notes with 10+ solved problems + memory queries

---

## <a id="phase-2"></a>Phase 2: PySpark Foundations
### Weeks 3–4: September 28 – October 11

**Theme:** PySpark is the #1 big data skill in job ads. Master it before touching cloud platforms.

### Week 3: PySpark Basics

| Day | Task | Hours |
|-----|------|-------|
| Mon | Install PySpark, `SparkSession`, RDDs vs DataFrames | 4 |
| Tue | DataFrame ops: `select`, `filter`, `withColumn`, `drop` | 4 |
| Wed | Joins: inner, left, broadcast joins | 4 |
| Thu | Aggregations: `groupBy`, `agg`, `pivot` | 4 |
| Fri | Window functions in PySpark: `Window.partitionBy` | 4 |
| Sat | Practice: Load 1M-row dataset, transform, write Parquet | 5 |
| Sun | Push `week-03/pyspark_intro.py` | 4 |

**Deliverable:** PySpark script that reads, transforms, writes Parquet

### Week 4: PySpark Advanced + Optimization

| Day | Task | Hours |
|-----|------|-------|
| Mon | Spark SQL: `createOrReplaceTempView`, `spark.sql()` | 4 |
| Tue | Partitioning: `repartition`, `coalesce`, partition pruning | 4 |
| Wed | Caching: `persist`, `cache`, storage levels | 4 |
| Thu | Catalyst optimizer, Spark UI, AQE basics | 4 |
| Fri | Complex types: arrays, structs, `explode` | 4 |
| Sat | Build ETL: 3 CSVs → join → aggregate → partitioned Parquet | 5 |
| Sun | Push `week-04/` with optimized Spark job | 4 |

**Deliverable:** Multi-source PySpark ETL with optimization notes

---

## <a id="phase-3"></a>Phase 3: Snowflake + Databricks Side-by-Side
### Weeks 5–7: October 12 – November 1

**Theme:** Job ads ask for BOTH. Learn both on the same dataset.

### Week 5: Snowflake Deep Dive

| Day | Task | Hours |
|-----|------|-------|
| Mon | Snowflake setup: warehouse, database, TPC-H sample data | 4 |
| Tue | Advanced SQL in Snowflake: window functions, CTEs | 4 |
| Wed | Time travel, cloning, zero-copy cloning | 4 |
| Thu | Query profiling, cost optimization, micro-partitions | 4 |
| Fri | Iceberg tables in Snowflake | 4 |
| Sat | Build analytical queries on TPC-H data | 5 |
| Sun | Push `week-05/snowflake_notes.md` | 4 |

**Deliverable:** 5 complex analytical queries in Snowflake worksheet

### Week 6: Databricks + Delta Lake

| Day | Task | Hours |
|-----|------|-------|
| Mon | Databricks Community Edition: clusters, notebooks, DBFS | 4 |
| Tue | Migrate PySpark job to Databricks notebook | 4 |
| Wed | Delta Lake: create tables, time travel, `MERGE INTO` | 4 |
| Thu | Schema evolution, `OPTIMIZE`, `VACUUM` | 4 |
| Fri | Unity Catalog: managed vs external tables | 4 |
| Sat | Build medallion architecture: bronze → silver → gold | 5 |
| Sun | Push `week-06/databricks_notes.md` + notebooks | 4 |

**Deliverable:** Bronze + silver + gold Delta tables in Databricks

### Week 7: Compare + Contrast

| Day | Task | Hours |
|-----|------|-------|
| Mon | Run SAME query on Snowflake vs Databricks SQL | 4 |
| Tue | Compare: Iceberg (Snowflake) vs Delta Lake (Databricks) | 4 |
| Wed | Data modeling: star schema in BOTH platforms | 4 |
| Thu | Cost comparison: Snowflake credits vs Databricks DBUs | 4 |
| Fri | Write ADR: "When to use Snowflake vs Databricks" | 4 |
| Sat | Build hybrid pipeline: Snowflake for warehouse, Databricks for Spark | 5 |
| Sun | Push `week-07/comparison.md` | 4 |

**Deliverable:** Architecture decision record + hybrid pipeline concept

---

## <a id="phase-4"></a>Phase 4: dbt — The Universal Transformer
### Weeks 8–9: November 2 – 15

**Theme:** dbt works on Snowflake AND Databricks. Learn it once, apply everywhere.

### Week 8: dbt Core on Snowflake

| Day | Task | Hours |
|-----|------|-------|
| Mon | `dbt init`, `profiles.yml`, connect to Snowflake | 4 |
| Tue | Staging models, sources, refs | 4 |
| Wed | Intermediate + mart models | 4 |
| Thu | Tests: `unique`, `not_null`, `relationships` | 4 |
| Fri | Jinja macros, `dbt-utils` | 4 |
| Sat | Snapshots, documentation, `dbt docs` | 5 |
| Sun | Push `week-08/dbt_snowflake/` | 4 |

**Deliverable:** dbt project on Snowflake with tests + docs

### Week 9: dbt on Databricks + Advanced

| Day | Task | Hours |
|-----|------|-------|
| Mon | Same dbt project, switch profile to Databricks | 4 |
| Tue | Compare: dbt on Snowflake vs dbt on Databricks | 4 |
| Wed | dbt Mesh: cross-project references | 4 |
| Thu | Slim CI, pre-commit hooks | 4 |
| Fri | dbt Cloud vs Core | 4 |
| Sat | Build unified dbt project that runs on BOTH | 5 |
| Sun | Push `week-09/dbt_unified/` | 4 |

**Deliverable:** Single dbt project deployable to Snowflake OR Databricks

---

## <a id="phase-5"></a>Phase 5: Ingestion + Orchestration
### Weeks 10–11: November 16 – 29

**Theme:** Move data. Schedule pipelines. The operational layer.

### Week 10: Airbyte + Ingestion

| Day | Task | Hours |
|-----|------|-------|
| Mon | Deploy Airbyte locally, architecture overview | 4 |
| Tue | Postgres → Snowflake connection | 4 |
| Wed | CDC with Debezium | 4 |
| Thu | API ingestion, custom connectors | 4 |
| Fri | dlt (data load tool) comparison | 4 |
| Sat | Build ingestion layer for capstone dataset | 5 |
| Sun | Push `week-10/ingestion/` | 4 |

**Deliverable:** 3 sources syncing to Snowflake via Airbyte

### Week 11: Apache Airflow

| Day | Task | Hours |
|-----|------|-------|
| Mon | Deploy Airflow, first DAGs | 4 |
| Tue | TaskFlow API, sensors, task groups | 4 |
| Wed | Airflow + dbt (Cosmos) | 4 |
| Thu | Retries, SLAs, Slack alerts | 4 |
| Fri | Backfills, catchup | 4 |
| Sat | Build DAG: Airbyte → dbt → email alert | 5 |
| Sun | Push `week-11/dags/` | 4 |

**Deliverable:** Production DAG orchestrating ingestion → transformation

---

## <a id="phase-6"></a>Phase 6: Infrastructure + Data Quality
### Weeks 12–13: November 30 – December 13

**Theme:** Provision as code. Trust your data.

### Week 12: Terraform + Cloud

| Day | Task | Hours |
|-----|------|-------|
| Mon | Terraform basics: HCL, providers, state | 4 |
| Tue | AWS: S3, IAM roles | 4 |
| Wed | Snowflake provider: warehouse, database, roles | 4 |
| Thu | Databricks provider: clusters, jobs | 4 |
| Fri | GitHub Actions + Terraform CI/CD | 4 |
| Sat | Provision full stack: S3 + IAM + Snowflake + Databricks config | 5 |
| Sun | Push `week-12/terraform/` | 4 |

**Deliverable:** Terraform modules for both platforms

### Week 13: Great Expectations + Observability

| Day | Task | Hours |
|-----|------|-------|
| Mon | GX: expectations, validators, checkpoints | 4 |
| Tue | GX + dbt integration | 4 |
| Wed | GX on Snowflake tables | 4 |
| Thu | GX on Delta Lake tables | 4 |
| Fri | DataHub / OpenMetadata for lineage | 4 |
| Sat | Quality-gated pipeline: dbt → GX → alert | 5 |
| Sun | Push `week-13/quality/` | 4 |

**Deliverable:** Data quality checks on BOTH Snowflake and Databricks

---

## <a id="phase-7"></a>Phase 7: Streaming
### Weeks 14–15: December 14 – 27

**Theme:** Real-time data. The skill that separates mid-level from senior.

### Week 14: Kafka + Spark Streaming

| Day | Task | Hours |
|-----|------|-------|
| Mon | Kafka: topics, partitions, producers, consumers | 4 |
| Tue | Python producer/consumer with `confluent-kafka` | 4 |
| Wed | Kafka Connect: Debezium CDC | 4 |
| Thu | Spark Structured Streaming: `readStream`, `writeStream` | 4 |
| Fri | Delta Live Tables: declarative streaming | 4 |
| Sat | Build streaming pipeline: Postgres → Kafka → Spark → Delta | 5 |
| Sun | Push `week-14/streaming/` | 4 |

**Deliverable:** Hybrid batch + streaming pipeline

### Week 15: CI/CD + Polish

| Day | Task | Hours |
|-----|------|-------|
| Mon | GitHub Actions for dbt + Terraform | 4 |
| Tue | Pre-commit hooks across all repos | 4 |
| Wed | Monitoring: Spark UI, Airflow metrics | 4 |
| Thu | Cost optimization: Snowflake + Databricks | 4 |
| Fri | Security: Unity Catalog / Lake Formation basics | 4 |
| Sat | Final repo cleanup, READMEs, architecture diagrams | 5 |
| Sun | Push everything | 4 |

**Deliverable:** Production-ready CI/CD across all projects

---

## <a id="phase-8"></a>Phase 8: Capstone + Job Hunt
### Weeks 16–18: December 28 – January 17, 2027

**Theme:** Build the flagship. Get hired.

### Week 16: Capstone Design + Build

| Day | Task | Hours |
|-----|------|-------|
| Mon | Architecture: Airbyte → Snowflake + Databricks → dbt → Airflow | 4 |
| Tue | Terraform all infrastructure | 4 |
| Wed | Build ingestion (Airbyte + API + CDC) | 4 |
| Thu | Build dbt models (staging → intermediate → mart) | 4 |
| Fri | Integrate Airflow DAG | 4 |
| Sat | Add GX + alerts | 5 |
| Sun | Test end-to-end 5+ times | 4 |

**Deliverable:** Working end-to-end pipeline on BOTH platforms

### Week 17: Polish + Content

| Day | Task | Hours |
|-----|------|-------|
| Mon | Add streaming component | 4 |
| Tue | Build Streamlit dashboard | 4 |
| Wed | Write blog: "Snowflake vs Databricks: A Data Engineer's Guide" | 4 |
| Thu | Record 3-minute demo video | 4 |
| Fri | Documentation: architecture, runbook, data dictionary | 4 |
| Sat | Update LinkedIn, GitHub profile | 5 |
| Sun | Resume: 1 page, metrics-focused | 4 |

**Deliverable:** Professional portfolio + blog + video

### Week 18: Apply

| Day | Task | Hours |
|-----|------|-------|
| Mon | Apply to 10 jobs | 4 |
| Tue | Apply to 10 jobs + follow-ups | 4 |
| Wed | Interview prep: SQL (5 problems) | 4 |
| Thu | System design: whiteboard your capstone | 4 |
| Fri | Behavioral practice | 4 |
| Sat | Apply to 10 jobs + networking | 5 |
| Sun | Rest + plan January follow-ups | 4 |

**Deliverable:** 30+ applications sent

---

## The Two Tech Stacks (From the Video)

| Stack A: Analytics-First | Stack B: Big Data-First | You Learn Both |
|-------------------------|------------------------|---------------|
| Snowflake | Databricks | ✅ Week 5–7 |
| dbt | PySpark | ✅ Week 3–4, 8–9 |
| SQL-first | Python-first | ✅ Week 1–2 |
| Airflow | Airflow | ✅ Week 11 |
| Iceberg | Delta Lake | ✅ Week 5–7 |
| Great Expectations | Great Expectations | ✅ Week 13 |

---

## Weekly Time Commitment

| Day | Hours | Focus |
|-----|-------|-------|
| Monday–Friday | 3.5–4 hrs/day | New concepts + coding |
| Saturday | 5–6 hrs | Deep work, projects |
| Sunday | 3–4 hrs | Review, polish, push |
| **Weekly Total** | **25 hrs** | |

---

## Job-Ready Checklist (By January 31, 2027)

- [ ] GitHub: 5+ repos (Python, PySpark, Snowflake, Databricks, dbt, Terraform)
- [ ] Capstone: End-to-end pipeline on BOTH Snowflake and Databricks
- [ ] Blog: "Snowflake vs Databricks: A Data Engineer's Perspective"
- [ ] SQL: 50+ problems solved
- [ ] PySpark: Can write complex DataFrame operations from memory
- [ ] Snowflake: Comfortable with warehouses, Iceberg, cost optimization
- [ ] Databricks: Comfortable with notebooks, Delta Lake, Unity Catalog
- [ ] dbt: Project deployable to both platforms
- [ ] LinkedIn: Updated headline mentioning both stacks
- [ ] Resume: 1 page, metrics-focused, both Snowflake + Databricks listed
- [ ] Demo: 3-minute video
- [ ] Applications: 50+ jobs applied

---

## Certifications to Consider

| Certification | Platform | When to Take |
|--------------|----------|-------------|
| Snowflake SnowPro Core | Snowflake | After Week 5 |
| Databricks Data Engineer Associate | Databricks | After Week 6 |
| AWS Cloud Practitioner | AWS | After Week 12 |

---

## Your First Step — Do This Today

1. Sign up for [Databricks Community Edition](https://www.databricks.com/try-databricks) (free)
2. Sign up for [Snowflake free trial](https://signup.snowflake.com/) (if not done)
3. Install PySpark: `pip install pyspark`
4. Verify: `python -c "from pyspark.sql import SparkSession; print('Ready')"`
5. Create `week-03/pyspark_intro.py` — your first Spark job

---

*Roadmap based on Data with Baraa's analysis of 22,000 real job ads. Combined stack for maximum job market coverage.*
