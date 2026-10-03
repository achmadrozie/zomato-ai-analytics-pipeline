WITH source AS (
    SELECT *
    FROM {{ source('zomato', 'reviews') }}
)
, transformed AS (
    SELECT
        review_id
        , order_id
        , user_id::NUMBER              AS customer_id
        , restaurant_id::STRING        AS restaurant_id
        , rating::NUMBER               AS rating
        , comment::STRING              AS comment
        , review_date::DATE            AS review_date
    FROM source
    WHERE comment IS NOT NULL
)

SELECT * FROM transformed
