"""Load Snowflake source tables, then build the dbt models."""

from datetime import datetime

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.bash import BashOperator


DBT = "/opt/airflow/dbt_venv/bin/dbt"
DBT_PROJECT = "/opt/airflow/dbt/dbt_zomato"
DBT_PROFILES = "/opt/airflow/.dbt"

COPY_RAW = [
    "COPY INTO ZOMATO.SOURCES.RESTAURANTS FROM @ZOMATO.SOURCES.ZOMATO_SOURCES_STAGE/restaurants ON_ERROR='CONTINUE'",
    "COPY INTO ZOMATO.SOURCES.FOOD FROM @ZOMATO.SOURCES.ZOMATO_SOURCES_STAGE/food ON_ERROR='CONTINUE'",
    "COPY INTO ZOMATO.SOURCES.MENU FROM @ZOMATO.SOURCES.ZOMATO_SOURCES_STAGE/menu ON_ERROR='CONTINUE'",
    "COPY INTO ZOMATO.SOURCES.ORDER_ITEMS FROM @ZOMATO.SOURCES.ZOMATO_SOURCES_STAGE/order_items ON_ERROR='CONTINUE'",
    "COPY INTO ZOMATO.SOURCES.ORDERS FROM @ZOMATO.SOURCES.ZOMATO_SOURCES_STAGE/orders ON_ERROR='CONTINUE'",
    "COPY INTO ZOMATO.SOURCES.REVIEWS FROM @ZOMATO.SOURCES.ZOMATO_SOURCES_STAGE/reviews ON_ERROR='CONTINUE'",
    "COPY INTO ZOMATO.SOURCES.USERS FROM @ZOMATO.SOURCES.ZOMATO_SOURCES_STAGE/users ON_ERROR='CONTINUE'",
]

with DAG(
    dag_id="zomato_batch",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["zomato", "dbt", "snowflake"],
) as dag:
    reload_raw = SQLExecuteQueryOperator(
        task_id="reload_raw",
        conn_id="snowflake_default",
        sql=COPY_RAW,
        autocommit=True,
    )

    dbt_build_core = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"{DBT} build --exclude tag:ai "
            f"--project-dir {DBT_PROJECT} --profiles-dir {DBT_PROFILES}"
        ),
    )

    enrich_reviews = BashOperator(
        task_id="enrich_reviews",
        bash_command="python /opt/airflow/ai/01_enrich_reviews.py",
    )

    dbt_build_ai = BashOperator(
        task_id = "dbt_build_ai",
        bash_command=f"{DBT} build --select tag:ai --project-dir {DBT_PROJECT} --profiles-dir {DBT_PROFILES}"
    )

    reload_raw >> dbt_build_core >> enrich_reviews >> dbt_build_ai
