{% docs fact_order %}
Order fact with one row per `order_id`. Selects staged order attributes and prepares typed values and reusable order-level measures. The model is incremental and merges selected rows by `order_id`; on incremental runs it selects only rows whose `order_timestamp` exceeds the maximum already in the fact.
{% enddocs %}

{% docs fact_order_order_id %}
Identifier of the order and unique key used for incremental merges.
{% enddocs %}

{% docs fact_order_order_timestamp %}
Order timestamp from the source; also used as the incremental selection cutoff.
{% enddocs %}

{% docs fact_order_order_date %}
Order date from the source, parsed to a date.
{% enddocs %}

{% docs fact_order_customer_id %}
Customer identifier, renamed from source `user_id` in staging.
{% enddocs %}

{% docs fact_order_restaurant_id %}
Restaurant identifier, renamed from source `r_id` in staging.
{% enddocs %}

{% docs fact_order_city %}
City parsed from the last comma-separated segment of the source `restaurant_city` value; staging uses the original value if no segment is found.
{% enddocs %}

{% docs fact_order_cuisine %}
Cuisine value recorded on the order.
{% enddocs %}

{% docs fact_order_payment_method %}
Payment method recorded on the order.
{% enddocs %}

{% docs fact_order_order_status %}
Order status from the source.
{% enddocs %}

{% docs fact_order_is_delivered %}
True when `order_status` equals `Delivered`; derived in staging.
{% enddocs %}

{% docs fact_order_is_cancelled %}
True when `order_status` equals `Cancelled`.
{% enddocs %}

{% docs fact_order_order_hour %}
Hour of day extracted from `order_timestamp`.
{% enddocs %}

{% docs fact_order_items_count %}
Item count recorded on the order.
{% enddocs %}

{% docs fact_order_sales_qty %}
Sales quantity recorded on the order.
{% enddocs %}

{% docs fact_order_subtotal %}
Subtotal amount recorded on the order.
{% enddocs %}

{% docs fact_order_discount %}
Discount amount recorded on the order.
{% enddocs %}

{% docs fact_order_delivery_fee %}
Delivery fee recorded on the order.
{% enddocs %}

{% docs fact_order_gst %}
GST amount recorded on the order.
{% enddocs %}

{% docs fact_order_sales_amount %}
Sales amount recorded on the order, parsed as a decimal. Unparseable values become null.
{% enddocs %}

{% docs fact_order_delivered_sales_amount %}
Sales amount for a delivered order and zero otherwise. A delivered order with an unparseable sales amount remains null.
{% enddocs %}

{% docs fact_order_customer_rating %}
Customer rating recorded on the order, parsed as a decimal when available.
{% enddocs %}

{% docs fact_order_delivery_time_min %}
Delivery time in minutes, parsed as a decimal when available.
{% enddocs %}
