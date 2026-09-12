import requests
import os
import json
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from minio import Minio
from io import BytesIO


# CONFIGURATION
load_dotenv()

API_URL = 'https://api.restcountries.com/countries/v5'

API_KEY = os.getenv("API_KEY")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "triplens")


# EXTRACT FROM API

def extract_countries_data():

    print("Calling REST Countries API...")

    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }

    response = requests.get(API_URL, headers=headers, timeout=30)

    response.raise_for_status()

    data = response.json()

    print("API extraction successful.")

   # print(f"Extracted {len(data)} country records")

    return data


# UPLOAD JSON DATA TO MINIO

def upload_to_minio(data):
    print("Connecting to MinIo...")

    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # Create bucket if it doesn't exist
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
        print(f"Created bucket: {MINIO_BUCKET}")

    # Add Ingestion timestamp
    ingestion_timestamp = datetime.now(timezone.utc)

    timestamp = ingestion_timestamp.strftime(
        "%Y%m%dT%H%M%SZ"
    )

    # MinIO object path
    object_name = (
        f"bronze/countries/"
        f"countries_{timestamp}.json"
    )

    # Convert Python object to JSON bytes
    json_data = json.dumps(
        data,
        indent=2,
        ensure_ascii=False
    ).encode("utf-8")

    # Upload

    client.put_object(
        MINIO_BUCKET,
        object_name,
        BytesIO(json_data),
        length=len(json_data),
        content_type="application/json"
    )

    print(
        f"Uploaded JSON to MinIo: "
        f"{MINIO_BUCKET}/{object_name}"
    )


# MAIN
def main():
    data = extract_countries_data()

    upload_to_minio(data)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
