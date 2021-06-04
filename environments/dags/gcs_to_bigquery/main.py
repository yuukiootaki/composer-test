from datetime import timedelta
from textwrap import dedent


from airflow import DAG

from airflow.operators.bash_operator import BashOperator

# from airflow.contrib.operators.postgres_to_gcs_operator import (
#     PostgresToGoogleCloudStorageOperator,
# )

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
    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    t2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command="sleep 5",
        retries=3,
    )

    t3 = CloudSqlQueryOperator(
        task_id="query",
        gcp_cloudsql_conn_id="user-db",
        sql=[
            "create table if not exists users (id SERIAL NOT NULL, name TEXT, PRIMARY KEY (id));",
            "insert into users values (0, 'hoge')",
        ],
    )

    # t3 = PostgresToGoogleCloudStorageOperator(
    #     task_id="postgresToGCS",
    #     sql="select * from users;",
    #     bucket="composer-test-hoge",
    #     filename="dump",
    #     schema_filename=None,
    #     approx_max_file_size_bytes=1900000000000,
    #     postgres_conn_id="user-db",
    #     google_cloud_storage_conn_id="google_cloud_default",
    # )
    EXPORT_URI = "gs://composer-test-hoge/dump.csv"
    export_body = {
        "exportContext": {
            "databases": ["user-db"],
            "fileType": "csv",
            "uri": EXPORT_URI,
            "sqlExportOptions": {"tables": ["users"], "schemaOnly": False},
            "csvExportOptions": {"selectQuery": "select * from users;"},
        }
    }

    t4 = CloudSqlInstanceExportOperator(
        task_id="export",
        instance="user-db",
        body=export_body,
        project_id="gcp-test-149405",
        gcp_conn_id="google_cloud_default",
        api_version="v1beta4",
    )

    # t5 = GoogleCloudStorageToBigQueryOperator(
    #     task_id="load-to-bigquery",
    #     bucket="composer-test-hoge",
    #     source_objects=["dump.csv"],
    #     destination_project_dataset_table="gcp-test-149405.example_dataset",
    #     schema_fields=[
    #         {"name": "id", "type": "NUMBER", "mode": "NULLABLE"},
    #         {"name": "name", "type": "STRING", "mode": "NULLABLE"},
    #     ],
    #     write_disposition="WRITE_TRUNCATE",
    # )

    t1 >> t2
    t2 >> t3
    t3 >> t4
    # t4 >> t5
