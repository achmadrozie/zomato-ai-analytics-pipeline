{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

WITH orders AS (
    SELECT
        order_id
        , order_timestamp
        , TRY_TO_DATE(order_date) AS order_date
        , customer_id
        , restaurant_id
        , city
        , cuisine
        , payment_method
        , order_status
        , is_delivered
        , is_cancelled
        , is_refunded
        , HOUR(TRY_TO_TIMESTAMP_NTZ(order_timestamp)) AS order_hour
        , items_count
        , sales_qty
        , subtotal
        , discount
        , delivery_fee
        , gst
        , TRY_TO_DECIMAL(sales_amount, 18, 2) AS sales_amount
        , TRY_TO_DECIMAL(customer_rating, 5, 2) AS customer_rating
        , TRY_TO_DECIMAL(delivery_time_min, 10, 1) AS delivery_time_min
    FROM {{ ref('stg_zomato__order') }}
    {% if is_incremental() %}
        WHERE order_timestamp > (
            SELECT COALESCE(MAX(order_timestamp), '1900-01-01'::TIMESTAMP)
            FROM {{ this }}
        )
    {% endif %}
)

SELECT
    order_id
    , order_timestamp
    , order_date
    , customer_id
    , restaurant_id
    , city
    , cuisine
    , payment_method
    , order_status
    , is_delivered
    , is_cancelled
    , order_hour
    , items_count
    , sales_qty
    , subtotal
    , discount
    , delivery_fee
    , gst
    , sales_amount
    , IFF(is_delivered, sales_amount, 0) AS delivered_sales_amount
    , customer_rating
    , delivery_time_min
FROM orders
