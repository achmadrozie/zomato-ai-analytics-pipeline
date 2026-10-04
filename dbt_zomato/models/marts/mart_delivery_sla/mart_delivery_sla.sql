WITH delivered_orders AS (
    SELECT
        city
        , order_hour
        , delivery_time_min
    FROM {{ ref('fact_order') }}
    WHERE is_delivered
)

SELECT
    city
    , order_hour
    , COUNT(*) AS delivered_orders
    , ROUND(MEDIAN(delivery_time_min), 1) AS p50
    , ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY delivery_time_min), 1) AS p90
FROM delivered_orders
GROUP BY city, order_hour
