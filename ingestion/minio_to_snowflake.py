from datetime import datetime, timezone
import logging
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from minio import Minio
import snowflake.connector

load_dotenv()

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

SNOWFLAKE_STAGE = "TRIPLENS_RAW_STAGE"
SNOWFLAKE_TABLE = "COUNTRIES_RAW"
SNOWFLAKE_WATERMARK_TABLE = "PIPELINE_WATERMARK"
SOURCE_NAME = "countries"


def ensure_watermark_table(cursor) -> None:
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {SNOWFLAKE_WATERMARK_TABLE} (
            source_name STRING,
            last_loaded_timestamp TIMESTAMP_NTZ,
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)


def get_watermark(cursor, source_name: str):
    cursor.execute(
        f"SELECT last_loaded_timestamp FROM {SNOWFLAKE_WATERMARK_TABLE} "
        f"WHERE source_name = %s",
        (source_name,),
    )
    row = cursor.fetchone()
  #  return row[0] if row else None
    if not row:
        return None

    watermark = row[0]

    if watermark.tzinfo is None:
        watermark = watermark.replace(tzinfo=timezone.utc)

    return watermark


def update_watermark(cursor, source_name: str, new_timestamp) -> None:
    cursor.execute(
        f"""
        MERGE INTO {SNOWFLAKE_WATERMARK_TABLE} t
        USING (SELECT %s AS source_name, %s AS ts) s
        ON t.source_name = s.source_name
        WHEN MATCHED THEN UPDATE SET
            t.last_loaded_timestamp = s.ts,
            t.updated_at = CURRENT_TIMESTAMP()
        WHEN NOT MATCHED THEN INSERT (source_name, last_loaded_timestamp)
            VALUES (s.source_name, s.ts)
        """,
        (source_name, new_timestamp),
    )


def run_pipeline():
    logger.info("Connecting to MinIO...")
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    logger.info("Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )
    cursor = conn.cursor()

    try:
        ensure_watermark_table(cursor)

        watermark = get_watermark(cursor, SOURCE_NAME)
        logger.info(f"Current watermark: {watermark}")

        objects = list(minio_client.list_objects(MINIO_BUCKET, recursive=True))
        json_objects = [
            o for o in objects if o.object_name.lower().endswith(".json")]

        if watermark is not None:
            json_objects = [
                o for o in json_objects if o.last_modified > watermark]

        json_objects.sort(key=lambda o: o.last_modified)  # oldest first

        if not json_objects:
            logger.info("No new files to load.")
            return

        logger.info(f"Found {len(json_objects)} new file(s) to load.")

        for obj in json_objects:
            with tempfile.TemporaryDirectory() as temp_dir:
                local_file = Path(temp_dir) / Path(obj.object_name).name

                logger.info(f"Downloading {obj.object_name}...")
                minio_client.fget_object(
                    MINIO_BUCKET, obj.object_name, str(local_file))

                logger.info(
                    f"Uploading {local_file.name} to Snowflake stage...")
                cursor.execute(
                    f"PUT 'file:///{local_file.as_posix()}' @{SNOWFLAKE_STAGE} "
                    f"AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
                )

                logger.info(
                    f"Loading {local_file.name} into {SNOWFLAKE_TABLE}...")
                cursor.execute(f"""
                    COPY INTO {SNOWFLAKE_TABLE} (RAW_DATA, SOURCE_FILE)
                    FROM (
                        SELECT $1, '{local_file.name}'
                        FROM @{SNOWFLAKE_STAGE}/{local_file.name}
                    )
                    
                    FILE_FORMAT = (TYPE = 'JSON')
                """)

            # Advance the watermark and commit right after each file, so if
            # a later file fails, this one won't be reloaded on the next run.
            update_watermark(cursor, SOURCE_NAME, obj.last_modified)
            conn.commit()
            logger.info(f"Loaded: {obj.object_name}")

    finally:
        cursor.close()
        conn.close()

    logger.info("SUCCESS: all new files loaded.")


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    run_pipeline()


if __name__ == "__main__":
    main()
