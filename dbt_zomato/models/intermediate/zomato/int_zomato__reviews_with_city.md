{% docs int_zomato__reviews_with_city %}
Reviews enriched with restaurant city, intended to have one row per review. Keeps every staged review with a non-null comment; city is null when its restaurant ID has no match in `stg_zomato__restaurants`.
{% enddocs %}

{% docs int_zomato__reviews_with_city_review_id %}
Unique identifier of the review from the staged reviews model.
{% enddocs %}

{% docs int_zomato__reviews_with_city_order_id %}
Identifier of the order associated with the review.
{% enddocs %}

{% docs int_zomato__reviews_with_city_customer_id %}
Numeric identifier of the customer who wrote the review.
{% enddocs %}

{% docs int_zomato__reviews_with_city_restaurant_id %}
Restaurant identifier stored as a string in staged reviews. The join converts it to a number to match the staged restaurant identifier.
{% enddocs %}

{% docs int_zomato__reviews_with_city_rating %}
Numeric rating supplied with the review.
{% enddocs %}

{% docs int_zomato__reviews_with_city_comment %}
Review comment. Staging excludes reviews where the source comment is null.
{% enddocs %}

{% docs int_zomato__reviews_with_city_review_date %}
Date of the review, cast to a date during staging.
{% enddocs %}

{% docs int_zomato__reviews_with_city_city %}
City from the matching staged restaurant. Null when no restaurant matches.
{% enddocs %}
