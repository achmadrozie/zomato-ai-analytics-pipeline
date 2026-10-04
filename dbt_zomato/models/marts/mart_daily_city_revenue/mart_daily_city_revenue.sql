SELECT
    order_date
    , city
    , COUNT(*) AS orders
    , COALESCE(COUNT_IF(is_delivered), 0) AS delivered_orders
    , ROUND(DIV0(COALESCE(COUNT_IF(is_cancelled), 0), COUNT(*)), 4) AS cancel_rate
    , SUM(delivered_sales_amount) AS gmv
    , ROUND(
        DIV0(
            SUM(delivered_sales_amount)
            , COALESCE(COUNT_IF(is_delivered), 0)
        )
        , 2
    ) AS aov
FROM {{ ref('fact_order') }}
GROUP BY order_date, city
