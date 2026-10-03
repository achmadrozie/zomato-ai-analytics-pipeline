with source as (
    select * 
    from {{ source('zomato','menu') }}
)
, transformed as (
    select
        menu_id
        , r_id                    AS restaurant_id
        , f_id                    AS food_id
        , SPLIT(cuisine, ',')     AS cuisine
        , TRY_TO_DOUBLE(price::VARCHAR) AS price
    from source
)

select * from transformed
