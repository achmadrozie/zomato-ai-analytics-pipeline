# Airflow 3.x image with Snowflake support and a separate dbt environment.
FROM apache/airflow:3.0.3

# Providers for the Snowflake load task and the Airflow login.
RUN pip install --no-cache-dir \
      apache-airflow-providers-snowflake \
      apache-airflow-providers-fab

# Keep dbt's dependencies separate from Airflow's dependencies.
RUN python -m venv /opt/airflow/dbt_venv && \
    /opt/airflow/dbt_venv/bin/pip install --no-cache-dir "dbt-snowflake==1.12.1"
