-- Clean ratings, counts, costs, and city names from the source data.
WITH source AS (
    SELECT *
    FROM {{ source('zomato', 'restaurants') }}
)
, transformed AS (
    SELECT
        id::NUMBER                                                   AS restaurant_id
        , name                                                       AS restaurant_name
        , TRIM(COALESCE(REGEXP_SUBSTR(city, '[^,]+$'), city))         AS city
        , TRY_TO_DECIMAL(NULLIF(rating, '--'), 3, 1)                  AS rating
        , TRY_TO_NUMBER(REGEXP_SUBSTR(rating_count, '[0-9]+'))        AS rating_count
        , TRY_TO_NUMBER(REGEXP_SUBSTR(cost, '[0-9]+'))                AS cost_for_two
        , cuisine
        , lic_no                                                     AS license_no
    FROM source
    WHERE TRY_TO_NUMBER(id) IS NOT NULL
)

SELECT * FROM transformed
