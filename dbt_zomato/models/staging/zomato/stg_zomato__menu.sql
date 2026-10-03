with source as (
    select * 
    from {{ source('zomato','menu') }}
)
, transformed as (
    select
        menu_id
        , r_id      AS restaurant_id
        , f_id      AS food_id
        , cuisine   AS cuisine
        , CAST(price AS FLOAT)    AS price
    from source
)

select * from transformed