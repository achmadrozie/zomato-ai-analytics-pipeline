{% docs fact_order_item %}
Order-item fact with one row per `order_item_id`. Joins staged items to staged orders on `order_id` to expose the order timestamp, date, and city on each item. The inner join excludes items without a matching staged order. Incremental runs merge all staged rows by `order_item_id`, so a late-arriving item for an older order is still considered.
{% enddocs %}

{% docs fact_order_item_order_item_id %}
Identifier of the order item and unique key used for incremental merges.
{% enddocs %}

{% docs fact_order_item_order_id %}
Identifier of the order containing the item.
{% enddocs %}

{% docs fact_order_item_restaurant_id %}
Restaurant identifier recorded on the item.
{% enddocs %}

{% docs fact_order_item_food_id %}
Food identifier, renamed from staged `f_id`.
{% enddocs %}

{% docs fact_order_item_order_ts %}
Timestamp of the related order from staging.
{% enddocs %}

{% docs fact_order_item_order_date %}
Calendar date of the related order, parsed from staging.
{% enddocs %}

{% docs fact_order_item_city %}
City associated with the related order, normalized in staging.
{% enddocs %}

{% docs fact_order_item_price %}
Recorded price of the item, cast to decimal in staging.
{% enddocs %}

{% docs fact_order_item_quantity %}
Recorded quantity of the item, cast to a number in staging.
{% enddocs %}

{% docs fact_order_item_line_amount %}
Recorded line amount from the item source, cast to decimal in staging. It is not recomputed from price and quantity.
{% enddocs %}
