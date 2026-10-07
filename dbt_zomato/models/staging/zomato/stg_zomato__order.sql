WITH source AS (
    SELECT *
    FROM {{ source('zomato', 'orders') }}
)
, transformed AS (
    SELECT
        order_id
        , order_timestamp
        , order_date
        , user_id                                  AS customer_id
        , r_id                                     AS restaurant_id
        , TRIM(
            COALESCE(REGEXP_SUBSTR(restaurant_city, '[^,]+$'), restaurant_city)
        )                                          AS city
        , cuisine
        , items_count
        , sales_qty
        , subtotal
        , discount
        , delivery_fee
        , gst
        , sales_amount
        , currency
        , payment_method
        , order_status
        , IFF(order_status = 'Delivered', True, False)          AS is_delivered
        , IFF(order_status = 'Cancelled', True, False)          AS is_cancelled
        , IFF(order_status = 'Refunded', True, False)           AS is_refunded
        , customer_rating
        , delivery_time_min
    FROM source
)

SELECT * FROM transformed
