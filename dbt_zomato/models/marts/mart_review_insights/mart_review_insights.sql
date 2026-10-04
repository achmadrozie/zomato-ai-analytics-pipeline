{{ config(tags=['ai']) }}

SELECT
    restaurant.city
    , enriched.topic
    , enriched.sentiment_label
    , COUNT(*) AS reviews
    , ROUND(AVG(TRY_TO_DOUBLE(enriched.sentiment_score)), 3) AS avg_sentiment_score
    , ROUND(AVG(reviews.rating), 2) AS avg_star_rating
    , COALESCE(COUNT_IF(enriched.key_issue IS NOT NULL), 0) AS flagged_issues
FROM {{ source('ai', 'review_enriched') }} AS enriched
INNER JOIN {{ ref('stg_zomato__review') }} AS reviews
    ON enriched.review_id = reviews.review_id
LEFT JOIN {{ ref('dim_restaurant') }} AS restaurant
    ON TRY_TO_NUMBER(reviews.restaurant_id) = restaurant.restaurant_id
GROUP BY restaurant.city, enriched.topic, enriched.sentiment_label
