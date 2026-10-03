WITH reviews AS (
    SELECT *
    FROM {{ ref('stg_zomato__reviews') }}
)
, restaurants AS (
    SELECT *
    FROM {{ ref('stg_zomato__restaurants') }}
)
, joined AS (
    SELECT
        reviews.*
        , restaurants.city
    FROM reviews
    LEFT JOIN restaurants
        ON TRY_TO_NUMBER(reviews.restaurant_id) = restaurants.restaurant_id
)

SELECT * FROM joined
