FROM apache/airflow:2.10.5-python3.11

USER airflow

RUN pip install --no-cache-dir \
    dbt-snowflake \
    minio \
    snowflake-connector-python \
    requests \
    python-dotenv







# FROM python:3.12-slim

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt \
#     dbt-snowflake

# COPY src/ /app/

# CMD ["python", "data_extraction.py"]

