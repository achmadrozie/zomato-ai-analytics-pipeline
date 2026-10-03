WITH source AS (
    SELECT *
    FROM {{ source('zomato', 'food') }}
)
, transformed AS (
    SELECT
        f_id                           AS food_id
        , item                         AS food_name
        , INITCAP(veg_or_non_veg)      AS veg_or_non_veg
    FROM source
    WHERE f_id IS NOT NULL
)

SELECT * FROM transformed
