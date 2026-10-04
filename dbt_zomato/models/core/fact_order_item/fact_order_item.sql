{{
    config(
        materialized='incremental',
        unique_key='order_item_id',
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

SELECT
    oi.order_item_id
    , oi.order_id
    , oi.restaurant_id
    , oi.f_id AS food_id
    , o.order_timestamp AS order_ts
    , TRY_TO_DATE(o.order_date) AS order_date
    , o.city
    , oi.price
    , oi.quantity
    , oi.line_amount
FROM {{ ref('stg_zomato__order_item') }} AS oi
INNER JOIN {{ ref('stg_zomato__order') }} AS o
    ON oi.order_id = o.order_id
