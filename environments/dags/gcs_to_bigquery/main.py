from datetime import timedelta
from textwrap import dedent


from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from airflow.contrib.operators.gcp_sql_operator import (
    CloudSqlInstanceExportOperator,
    CloudSqlQueryOperator,
)
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.utils.dates import days_ago


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["hoge@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "tutorial",
    default_args=default_args,
    description="A simple DAG.",
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    tags=["example"],
) as dag:
    FILE_NAME = "dump_{{ ts }}.csv"
    EXPORT_URI = "gs://GCS_BUCKET/" + FILE_NAME
    PROJECT_ID = "PROJECT_ID"
    BIGQUERY_DATASET = "example_dataset"
    BIGQUERY_TABLE = "users"

    t1 = CloudSqlQueryOperator(
        task_id="query",
        gcp_cloudsql_conn_id="user-db",
        sql=[
            "DROP TABLE users;"
            "CREATE TABLE IF NOT EXISTS users (id SERIAL NOT NULL, name TEXT, PRIMARY KEY (id));",
            "INSERT INTO users VALUES (0, 'hoge');",
        ],
    )

    export_body = {
        "exportContext": {
            "databases": ["user-db"],
            "fileType": "csv",
            "uri": EXPORT_URI,
            "sqlExportOptions": {"tables": ["users"], "schemaOnly": False},
            "csvExportOptions": {"selectQuery": "select * from users;"},
        }
    }

    t2 = CloudSqlInstanceExportOperator(
        task_id="export",
        instance="user-db",
        body=export_body,
        project_id=PROJECT_ID,
        gcp_conn_id="google_cloud_default",
        api_version="v1beta4",
    )
    t2.template_fields = tuple(list(t2.template_fields) + ["body"])

    t3 = GoogleCloudStorageToBigQueryOperator(
        task_id="load-to-bigquery",
        bucket="composer-test-hoge",
        source_objects=[FILE_NAME],
        destination_project_dataset_table=f"{PROJECT_ID}.example_dataset.users",
        schema_fields=[
            {"name": "id", "type": "STRING", "mode": "NULLABLE"},
            {"name": "name", "type": "STRING", "mode": "NULLABLE"},
        ],
        write_disposition="WRITE_TRUNCATE",
    )

    t1 >> t2
    t2 >> t3
