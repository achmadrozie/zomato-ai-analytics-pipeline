{% docs mart_review_insights %}
Review summary at one row per restaurant city, AI topic, and sentiment label. Only reviews present in both `ZOMATO.AI.REVIEW_ENRICHED` and `stg_zomato__review` are included; staging excludes reviews without comments. City comes from the matching restaurant dimension and can be null if no restaurant matches.
{% enddocs %}

{% docs mart_review_insights_city %}
City of the reviewed restaurant, from `dim_restaurant`.
{% enddocs %}

{% docs mart_review_insights_topic %}
Topic assigned by the AI enrichment process.
{% enddocs %}

{% docs mart_review_insights_sentiment_label %}
Sentiment label assigned by the AI enrichment process.
{% enddocs %}

{% docs mart_review_insights_reviews %}
Number of enriched reviews in the city, topic, and sentiment group.
{% enddocs %}

{% docs mart_review_insights_avg_sentiment_score %}
Average numeric AI sentiment score, rounded to three decimal places.
{% enddocs %}

{% docs mart_review_insights_avg_star_rating %}
Average numeric star rating from staged reviews, rounded to two decimal places.
{% enddocs %}

{% docs mart_review_insights_flagged_issues %}
Number of enriched reviews with a nonnull AI `key_issue` value.
{% enddocs %}
