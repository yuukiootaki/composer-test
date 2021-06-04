from datetime import timedelta
from textwrap import dedent


from airflow import DAG

from airflow.operators.bash_operator import BashOperator

# from airflow.contrib.operators.postgres_to_gcs_operator import (
#     PostgresToGoogleCloudStorageOperator,
# )

from airflow.contrib.operators.gcp_sql_operator import CloudSqlInstanceExportOperator
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
    EXPORT_URI = "gs://composer-test-hoge/dump.sql"
    export_body = {
        "exportContext": {
            "databases": ["users"],
            "fileType": "csv",
            "uri": EXPORT_URI,
            "sqlExportOptions": {"tables": ["users"], "schemaOnly": False},
            "offload": False,
            "csvExportOptions": {"selectQuery": "select * from users;"},
        }
    }

    t3 = CloudSqlInstanceExportOperator(
        task_id="export",
        instance="user-db",
        body=export_body,
        project_id="gcp-test-149405",
        gcp_conn_id="google_cloud_default",
        api_version="v1beta4",
    )

    t1 >> t2
    t2 >> t3
