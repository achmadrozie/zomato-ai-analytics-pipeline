# Zomato dbt models

This dbt project is the modeling layer of the [Zomato AI Analytics Pipeline](https://github.com/achmadrozie/zomato-ai-analytics-pipeline). It turns Snowflake source tables into documented facts, dimensions, marts, and metric definitions that analysts and AI apps can reuse.

## 1. Business problem — what I built and why it matters

Analytics requests can pile up with one analyst, while definitions scattered across reports and one-off queries make numbers harder to reconcile. This project builds a curated data product so routine questions can use consistent models and metrics, leaving analysts more time for work that needs judgment.

![Before and after: analyst queue to self-service analytics](../assets/problem-solution-combined.png)

The “after” state and faster decision time in this diagram are design goals, not measured results from this project.

## 2. Business usability and impact

The dbt models support two paths: analysts and BI reports can query curated core and mart tables, while conversational apps can use those tables and the metric definitions as context. For example, the text-to-SQL app displays the generated SQL and its Snowflake result:

![Text-to-SQL example showing SQL and data output](../assets/text-to-sql%20-%20demo_01.png)

The [text-to-SQL app](../ai/03_text_to_sql.py) reads dbt semantic model and metric YAML files at runtime to inform SQL generation. It executes the generated `SELECT` directly in Snowflake; it does not query MetricFlow. This screenshot demonstrates a working output, not a measured improvement in answer accuracy or decision speed.

## 3. Engineering solution, reliability, and reproducibility

### Architecture

![Zomato pipeline architecture](../assets/zomato-architecture2.png)

The dbt path is **sources → staging → intermediate → core → marts**, with semantic models and metrics defined on the core facts. The diagram retains its original AI model labels; the current text-to-SQL app uses `gpt-6-luna`.

| Layer | Materialization | Contents |
| --- | --- | --- |
| [`staging`](models/staging/zomato/) | Views | Standardized orders, order items, users, restaurants, reviews, food, and menu records. |
| [`intermediate`](models/intermediate/date/) | Views | Date spine and derived date features. |
| [`core`](models/core/) | Tables | `fact_order`, `fact_order_item`, and customer, restaurant, food, and date dimensions. |
| [`marts`](models/marts/) | Tables | Daily city revenue, restaurant performance, delivery SLA, and review insights. |

`fact_order` has one row per order; `fact_order_item` has one row per item. Keeping these grains separate matters when calculating order and item metrics. The [schema-name macro](macros/generate_schema_name.sql) places models in their configured `STAGING`, `INTERMEDIATE`, `CORE`, and `MARTS` schemas.

### Definitions and checks

The [`semantic_models`](models/semantic_models/) directory defines the order and order-item semantic models and a MetricFlow time spine. The [`metrics`](models/metrics/) directory defines nine metrics, including order counts, GMV, AOV, cancellation rate, item count, ordered quantity, and ordered amount. The YAML files hold their exact business definitions.

Model YAML files also contain dbt data tests. For example, [`fact_order`](models/core/fact_order/fact_order.yml) checks that `order_id` is unique and non-null, validates order statuses, and checks the customer relationship. These checks help catch data issues during `dbt build`; they do not by themselves establish end-to-end AI answer accuracy.

### Build locally

1. Prepare the Snowflake source tables using the scripts in [`../snowflake/`](../snowflake/).
2. Configure a local Snowflake dbt profile named `dbt_zomato`. Keep the profile and credentials outside this repository.
3. From `dbt_zomato/`, run:

   ```bash
   dbt debug
   dbt build --exclude tag:ai
   ```

4. Once review enrichment has populated its Snowflake output, run `dbt build --select tag:ai` for the review insights mart.

The [`zomato_batch` Airflow DAG](../airflow/dags/zomato_batch.py) runs source loading, the regular dbt build, review enrichment, and the AI mart build in sequence. See the [repository README](https://github.com/achmadrozie/zomato-ai-analytics-pipeline) for the full pipeline and app setup.

## 4. What's next?

A follow-up experiment can compare how access to source data, modeled layers, marts, semantic definitions, and written context affects AI answer correctness and consistency. That evaluation is separate from the dbt models documented here; the before/after impact remains a goal until it is measured.
