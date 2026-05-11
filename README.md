# Financial Data Pipeline — AWS + PySpark + Snowflake

End-to-end ETL pipeline ingesting NSE trade data into Snowflake using PySpark for transformation, Amazon MWAA (Airflow) for orchestration, deployed on AWS EKS with Docker/Kubernetes and automated via Harness CI/CD.

---

## Architecture

```
NSE Trade Data (CSV + REST API)
        ↓
   Python Extraction (ingest.py)
        ↓
   AWS S3 (raw landing zone)
        ↓
   PySpark Transformation (EKS)
   - Type casting & schema enforcement
   - Deduplication
   - Null handling
        ↓
   Snowflake (3-layer model)
   raw → transformed → reporting
        ↓
   Amazon MWAA (Airflow DAGs)
   - Orchestration & scheduling
   - SLA alerting & retry logic
        ↓
   Harness CI/CD
   - pytest → Docker build → EKS deploy → auto-rollback
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Cloud | AWS (EKS, S3, MWAA, IAM, VPC) |
| Processing | PySpark |
| Data Warehouse | Snowflake |
| Containerisation | Docker + Kubernetes (EKS) |
| Orchestration | Amazon MWAA (Apache Airflow) |
| CI/CD | Harness |
| Language | Python, SQL |
| Testing | pytest |

---

## Project Structure

```
financial-data-pipeline/
├── extraction/
│   └── ingest.py              # Python ingestion — NSE CSV + REST API
├── transformation/
│   └── transform_spark.py     # PySpark jobs — 3-layer model
├── sql/
│   └── snowflake_models.sql   # Snowflake schema + stored procedures
├── tests/
│   └── test_pipeline.py       # pytest suite (82% coverage)
├── dags/
│   └── pipeline_dag.py        # Airflow DAG for MWAA
├── docker/
│   └── Dockerfile             # Containerised PySpark job
├── requirements.txt
└── README.md
```

---

## Key Results

- Zero pipeline failures across 30 consecutive daily runs
- Batch processing time reduced from 18 min → 3 min (83% faster) via partition optimisation and broadcast joins
- Snowflake query time cut by 55% after clustering key implementation
- 82% pytest coverage with automated Harness CI/CD rollback on failure

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run extraction
```bash
python extraction/ingest.py
```

### 3. Run PySpark transformation
```bash
python transformation/transform_spark.py
```

### 4. Run tests
```bash
pytest tests/ -v
```

---

## Data Source

NSE (National Stock Exchange of India) publicly available trade data — bhavcopy files.
Synthetic data generator included for local testing without live data dependency.
