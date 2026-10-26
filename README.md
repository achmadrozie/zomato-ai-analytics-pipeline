# Zomato AI Analytics Pipeline

> From raw food-delivery CSVs to governed dbt models, LLM-enriched reviews, and chat-based analytics: S3 → Snowflake → dbt → Airflow → OpenAI → Streamlit.

![Zomato analytics pipeline architecture](assets/zomato-architecture2.png)

*The diagram keeps its original model labels; the text-to-SQL app currently uses `gpt-6-luna`.*

---

## Problem

Analytics requests pile up with one analyst, and metric definitions scatter across reports and one-off queries, so numbers are hard to reconcile. This project builds a curated data product (one set of models and metric definitions) so routine questions can be self-served, by BI tools or by conversational apps.

![Before and after: analyst queue to self-service analytics](assets/problem-solution-combined.png)

*The "after" state is a design goal, not a measured result.*

## What gets built

| Layer | Implementation | Purpose |
| --- | --- | --- |
| Source | 7 CSVs: **10M orders**, **~23M order items**, 300K reviews, plus users, restaurants, food, menu | Zomato-style operational data |
| Lake + load | AWS S3 → Snowflake storage integration → `COPY INTO` `ZOMATO.SOURCES` | Keyless S3 access, no stored AWS keys |
| Transform | dbt: `staging` → `intermediate` → `core` → `marts` | Clean, join, model, aggregate |
| Semantic layer | 2 semantic models, 9 metrics (GMV, AOV, cancellation rate, ...) | One definition per business metric |
| Orchestration | Airflow DAG `zomato_batch` (daily) | Load → build → enrich → AI mart |
| AI enrichment | OpenAI `gpt-4o-mini` | Reviews → sentiment, topic, key issue |
| AI apps | Streamlit: review RAG and text-to-SQL | Qualitative and quantitative questions in plain English |

## Data model

```text
SOURCES ─→ STAGING (views) ─→ INTERMEDIATE (views) ─→ CORE (tables) ─┬─→ MARTS (tables)
 7 tables   7 stg models       date spine + features   2 facts        │    4 marts
                                                       4 dimensions   └─→ semantic models + metrics
```

| Schema | Models |
| --- | --- |
| `CORE` | `fact_order` (1 row per order), `fact_order_item` (1 row per item), `dim_customer`, `dim_restaurant`, `dim_food`, `dim_date` |
| `MARTS` | `mart_daily_city_revenue`, `mart_restaurant_performance`, `mart_delivery_sla` (p50/p90 by city and hour), `mart_review_insights` |

The two fact grains are kept separate on purpose: counting order items as orders is the classic way to inflate order metrics. Models are documented and tested in YAML (`unique`, `not_null`, `accepted_values`, `relationships`). See the [dbt README](dbt_zomato/README.md) for details.

## Semantic layer

Business metrics are defined once, in dbt YAML, on top of the two facts (plus a daily MetricFlow time spine).

| Semantic model | Grain | Dimensions | Metrics |
| --- | --- | --- | --- |
| `fact_order` | order | `order_date` (day), `city`, `order_status`, `payment_method` | `count_order_total`, `count_order_delivered`, `count_order_cancelled`, `gmv`, `aov`, `cancellation_rate` |
| `fact_order_item` | order item | `order_date` (day), `city` | `count_order_item`, `total_ordered_quantity`, `total_ordered_amount` |

| Metric | Type | Definition |
| --- | --- | --- |
| `gmv` | simple | Sum of `sales_amount` for **delivered** orders only |
| `aov` | ratio | `gmv` / `count_order_delivered` |
| `cancellation_rate` | derived | `100 × count_order_cancelled / count_order_total` (percent) |
| `count_order_*` | simple | Total, delivered, and cancelled order counts |
| `count_order_item`, `total_ordered_quantity`, `total_ordered_amount` | simple | Item rows, summed quantity, summed line amount |

Order metrics live on the order grain and item metrics on the item grain, so they are never mixed. Text-to-SQL reads these same YAML files, which is how a question like "cancellation rate by payment method" uses the intended formula.

## AI layer

| Script | What it does |
| --- | --- |
| [`01_enrich_reviews.py`](ai/01_enrich_reviews.py) | **LLM as a transformation step.** Classifies unprocessed reviews into schema-constrained JSON (`sentiment_label`, `sentiment_score`, `topic`, `key_issue`), validates it, and writes to `ZOMATO.AI`. dbt then models it into `mart_review_insights`. Batch-capped (`SAMPLE_N`) and skips already-processed reviews. |
| [`02_rag_chat.py`](ai/02_rag_chat.py) | **Chat with reviews.** Embeds reviews (`text-embedding-3-small`), retrieves the top 5 for a question, and answers with `gpt-4o-mini` grounded in them. |
| [`03_text_to_sql.py`](ai/03_text_to_sql.py) | **Chat with the warehouse.** Turns a question into one Snowflake `SELECT`, shows the SQL, data, and a chart when applicable. |

![Text-to-SQL example showing SQL and data output](assets/text-to-sql%20-%20demo_01.png)

**How text-to-SQL stays safe and consistent**

- Reads the dbt semantic model and metric YAML at runtime, so generation follows the same definitions as the models. It runs the SQL on Snowflake; it does not query MetricFlow.
- `SELECT` only: forbidden keywords are rejected, `LIMIT` ≤ 100 is requested, and queries run as the restricted `DBT_ROLE` with a 60s statement timeout.

## Orchestration

```text
reload_raw  →  dbt_build  →  enrich_reviews  →  dbt_build_ai
COPY INTO      dbt build     OpenAI enrichment   review insights mart
               (+ tests)
```

[`zomato_batch`](airflow/dags/zomato_batch.py) runs daily on local Airflow (Docker). The AI mart is tagged `ai` so the regular build can exclude it until enrichment has run.

## Repository map

| Path | Contents |
| --- | --- |
| [`snowflake/`](snowflake/) | Warehouse, schemas, role, storage integration, stage, source tables, `COPY INTO` |
| [`aws/iam/`](aws/iam/) | Example S3 read policy and role trust policy |
| [`dbt_zomato/`](dbt_zomato/) | Models, tests, semantic models, metrics |
| [`airflow/`](airflow/) | Docker setup and the `zomato_batch` DAG |
| [`ai/`](ai/) | Review enrichment, RAG, and text-to-SQL |

## Getting started

```bash
# 1. Snowflake + S3: run snowflake/01 → 05 in order, adjusting account-specific values
#    (AWS side: aws/iam/). Upload the CSVs to your bucket.

# 2. dbt (needs a local profile named dbt_zomato)
cd dbt_zomato
dbt deps && dbt build --exclude tag:ai

# 3. AI apps (OPENAI_API_KEY and SNOWFLAKE_* in env or .env)
python ai/01_enrich_reviews.py
cd dbt_zomato && dbt build --select tag:ai && cd ..
streamlit run ai/02_rag_chat.py
streamlit run ai/03_text_to_sql.py

# 4. Or schedule everything with Airflow
cd airflow && docker compose up --build
```

Credentials, dbt profiles, source CSVs, and embedding files are not in version control. The Airflow setup expects a dbt profile at `~/.dbt`.

## Tech stack

Python · AWS S3 · Snowflake · dbt Core · Apache Airflow · OpenAI API · Streamlit

## What's next

Measure it: compare AI answer correctness and consistency when given raw sources vs. modeled layers vs. semantic definitions and written context. Until then, the impact above remains a goal, not a result.

---

**Achmad Rozie** · [@achmadrozie](https://github.com/achmadrozie)
