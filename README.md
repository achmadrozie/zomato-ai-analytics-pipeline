# Zomato AI Analytics Pipeline

> An end-to-end food delivery analytics project built with AWS S3, Snowflake, dbt, Airflow, OpenAI, and Streamlit.

This project loads Zomato-style operational data into Snowflake, transforms it into analytics-ready models with dbt, enriches customer reviews with AI, and exposes both quantitative and qualitative insights through Streamlit apps.

## Architecture

```text
CSV data → AWS S3 → Snowflake sources → dbt staging → intermediate → core
                                                        ├─→ marts → BI reporting
                                                        ├─→ semantic models + metrics
                                                        └─→ AI review enrichment
                                                                  ↓
                                     Streamlit: text-to-SQL and review RAG
```

![Zomato analytics pipeline architecture](assets/zomato-architecture2.png)

The diagram shows the original model labels; the text-to-SQL app currently uses `gpt-6-luna`.

## What the project does

| Layer | Implementation | Purpose |
| --- | --- | --- |
| Ingestion | AWS S3, Snowflake stages, `COPY INTO` | Load orders, order items, users, restaurants, reviews, food, and menu data. |
| Transformation | dbt staging, intermediate, core, marts | Clean source data and build facts, dimensions, and reporting tables. |
| Semantic definitions | 2 dbt semantic models and 9 metrics | Define measures such as GMV, AOV, cancellation rate, and item quantity. |
| Orchestration | Airflow `zomato_batch` DAG | Run the source load, dbt builds, review enrichment, and AI mart build. |
| Review enrichment | OpenAI classification | Add sentiment, topic, and key issue to customer reviews. |
| Conversational analytics | Streamlit + OpenAI | Ask quantitative questions through text-to-SQL or qualitative questions through review RAG. |

### Analytics models

- **Core:** order and order-item facts, plus customer, restaurant, food, and date dimensions.
- **Marts:** daily city revenue, restaurant performance, delivery SLA, and review insights.
- **Metrics:** order counts, delivered and cancelled orders, GMV, AOV, cancellation rate, and order-item measures.

### AI apps

- [`ai/01_enrich_reviews.py`](ai/01_enrich_reviews.py) classifies reviews and writes the results to Snowflake.
- [`ai/02_rag_chat.py`](ai/02_rag_chat.py) embeds customer reviews and answers questions using retrieved reviews as context.
- [`ai/03_text_to_sql.py`](ai/03_text_to_sql.py) turns natural-language questions into Snowflake `SELECT` queries and displays SQL, data, and a chart when applicable. It reads the dbt semantic model and metric YAML files at runtime so those definitions inform SQL generation. The app executes the resulting SQL against Snowflake; it does not query MetricFlow directly.

## Repository map

| Path | Contents |
| --- | --- |
| [`snowflake/`](snowflake/) | Database setup, storage integration, stages, source tables, and load SQL. |
| [`dbt_zomato/`](dbt_zomato/) | dbt models, tests, semantic models, and metrics. |
| [`airflow/`](airflow/) | Local Airflow Docker setup and batch DAG. |
| [`ai/`](ai/) | Review enrichment, review RAG, and text-to-SQL apps. |
| [`aws/`](aws/) | Example IAM policies for S3 access. |

## Getting started

1. Clone the repository and prepare an AWS S3 bucket and Snowflake account.
2. Run the Snowflake scripts in [`snowflake/`](snowflake/) in numeric order, adjusting account-specific values and loading the source CSV files to S3.
3. Configure a local dbt profile named `dbt_zomato` for Snowflake. From `dbt_zomato/`, run `dbt deps` and `dbt build`.
4. Set `OPENAI_API_KEY` and the `SNOWFLAKE_*` environment variables used by the AI scripts. Run the Streamlit apps with `streamlit run ai/02_rag_chat.py` or `streamlit run ai/03_text_to_sql.py`.
5. For scheduled batch runs, configure the environment variables and Snowflake connection used by [`airflow/docker-compose.yaml`](airflow/docker-compose.yaml), then start the stack from `airflow/` with `docker compose up --build`.

Credentials, dbt profiles, source data, and generated embedding files are kept outside version control. The local Airflow setup also expects a dbt profile at `~/.dbt`.

## Tech stack

AWS S3 · Snowflake · dbt Core and MetricFlow definitions · Apache Airflow · OpenAI API · Streamlit · Python

---

**Achmad Rozie** — [@achmadrozie](https://github.com/achmadrozie)
