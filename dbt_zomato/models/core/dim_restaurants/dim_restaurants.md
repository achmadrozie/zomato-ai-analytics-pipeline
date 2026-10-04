{% docs dim_restaurants %}
Restaurant dimension with one row per restaurant. Selects the identifier, location, cuisine, rating, and cost attributes from `stg_zomato__restaurants`.
{% enddocs %}

{% docs dim_restaurants_restaurant_id %}
Unique numeric identifier of the restaurant, derived from the source restaurant ID.
{% enddocs %}

{% docs dim_restaurants_restaurant_name %}
Restaurant name from the source record.
{% enddocs %}

{% docs dim_restaurants_city %}
City extracted from the last comma-separated segment of the source city field, or the original value when no segment is found.
{% enddocs %}

{% docs dim_restaurants_cuisine %}
Cuisine value from the source restaurant record.
{% enddocs %}

{% docs dim_restaurants_rating %}
Restaurant rating converted to a decimal during staging. The source placeholder `--` becomes null.
{% enddocs %}

{% docs dim_restaurants_rating_count %}
Numeric count extracted from the source rating count text, such as `50` from `50+`.
{% enddocs %}

{% docs dim_restaurants_cost_for_two %}
Numeric cost for two people extracted from the source cost text.
{% enddocs %}
