# Overview


**Country Data Engineering Pipeline** is an end-to-end data engineering platform designed to ingest, store, transform, and model country data from the REST Countries API into analytics-ready datasets.

The platform demonstrates a modern data engineering workflow by combining automated API ingestion, object storage, cloud data warehousing, incremental loading, data transformation, and workflow orchestration. Raw API data is landed in MinIO, loaded into Snowflake, and transformed into structured dimensional models using dbt, with Apache Airflow orchestrating the end-to-end pipeline.

### 📊 Data Architecture



The platform follows a layered data architecture:
<img width="2227" height="1010" alt="image" src="https://github.com/user-attachments/assets/3b23d5ad-a5de-49ef-a2e3-dd84e57edb78" />

# Project Contents


### 🏢 The Business Context


- **Data Availability:** Country information is available through a REST API but requires a reliable ingestion process before it can be used for analytics.
- **Data Management Challenges:** Raw API responses are semi-structured and require consistent storage, schema handling, and transformation before analytical use.
- **Scalability & Reliability:** Repeatedly processing the entire dataset is inefficient and increases unnecessary warehouse workloads.
- **The Solution:** An automated data pipeline that captures raw API data, preserves it in object storage, incrementally loads new data into Snowflake, and produces analytics-ready dimensional models with dbt.

---

### 🎯 Key Objectives


- **Automated Data Ingestion:** Extract country data from the REST Countries API using Python and automatically store raw API responses in MinIO.
- **Raw Data Preservation:** Maintain immutable JSON snapshots in object storage to provide a durable raw-data layer for downstream processing.
- **Incremental Data Loading:** Use a Snowflake watermark mechanism to identify and process only newly ingested files.
- **Data Transformation:** Convert semi-structured JSON data into structured relational datasets using dbt.
- **Dimensional Modeling:** Build analytics-ready country dimensions containing geographic, demographic, governmental, and economic attributes.
- **Workflow Orchestration:** Use Apache Airflow to schedule and coordinate extraction, loading, and transformation workflows.
- **Data Warehouse Integration:** Store raw and curated datasets in Snowflake for analytical querying.

---

### 🏗️ End-to-End Pipeline Architecture


1. **Source:** REST Countries API
2. **Extraction:** Python extracts country data through authenticated API requests.
3. **Object Storage:** Raw JSON responses are timestamped and stored in MinIO.
4. **Data Warehouse:** Snowflake loads new JSON files into the `COUNTRIES_RAW` table using an incremental watermark.
5. **Transformation:** dbt parses and standardizes semi-structured JSON into `STG_COUNTRIES`.
6. **Dimensional Modeling:** dbt creates the analytics-ready `DIM_COUNTRIES` model.
7. **Orchestration:** Apache Airflow coordinates the pipeline and executes the workflow on a recurring schedule.

---


**Bronze / Raw Layer**

- `COUNTRIES_RAW`
- Preserves raw API responses in JSON format.
- Stores source file metadata and ingestion timestamps.
- Provides a historical record of ingested data.

**Staging Layer**

- `STG_COUNTRIES`
- Flattens nested JSON structures.
- Standardizes country attributes and data types.
- Provides a clean relational interface for downstream models.

**Analytics Layer**

- `DIM_COUNTRIES`
- Contains analytics-ready country attributes.
- Includes population density and population categorization.
- Provides geographic, demographic, governmental, capital, and currency information.

---

### ⚙️ Technology Stack


- **Python** — API extraction and MinIO ingestion
- **Apache Airflow** — Workflow orchestration and scheduling
- **MinIO** — S3-compatible object storage for raw data
- **Snowflake** — Cloud data warehouse
- **dbt** — SQL-based transformation and dimensional modeling
- **Docker & Docker Compose** — Containerized development environment
- **PostgreSQL** — Airflow metadata database
- **REST Countries API** — External data source

---

### 🔄 Pipeline Workflow


The pipeline is orchestrated by Apache Airflow and executes the following workflow:

```text
REST Countries API
        │
        ▼
   Python Extract
        │
        ▼
      MinIO
   Raw JSON Files
        │
        ▼
     Snowflake
   COUNTRIES_RAW
        │
        ▼
       dbt
        │
        ▼
   STG_COUNTRIES
        │
        ▼
   DIM_COUNTRIES
