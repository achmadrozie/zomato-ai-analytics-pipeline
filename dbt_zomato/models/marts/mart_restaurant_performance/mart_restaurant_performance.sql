WITH order_metrics AS (
    SELECT
        restaurant_id
        , COUNT(*) AS orders
        , SUM(delivered_sales_amount) AS revenue
        , ROUND(AVG(customer_rating), 2) AS avg_customer_rating
        , ROUND(AVG(delivery_time_min), 1) AS avg_delivery_min
    FROM {{ ref('fact_order') }}
    GROUP BY restaurant_id
)

SELECT
    orders.restaurant_id
    , restaurant.restaurant_name
    , restaurant.city
    , restaurant.cuisine
    , orders.orders
    , orders.revenue
    , orders.avg_customer_rating
    , orders.avg_delivery_min
FROM order_metrics AS orders
LEFT JOIN {{ ref('dim_restaurant') }} AS restaurant
    ON TRY_TO_NUMBER(orders.restaurant_id) = restaurant.restaurant_id
