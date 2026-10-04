{% docs mart_delivery_sla %}
Delivery-time summary at one row per city and order hour, built from delivered orders in `fact_order`. This model reports duration percentiles; no SLA threshold or compliance rate is defined.
{% enddocs %}

{% docs mart_delivery_sla_city %}
City recorded on the order.
{% enddocs %}

{% docs mart_delivery_sla_order_hour %}
Hour of the order timestamp, from 0 through 23.
{% enddocs %}

{% docs mart_delivery_sla_delivered_orders %}
Number of delivered orders in the city and order-hour group.
{% enddocs %}

{% docs mart_delivery_sla_p50 %}
Median delivery time in minutes, rounded to one decimal place. Null or nonnumeric delivery times are excluded from the percentile.
{% enddocs %}

{% docs mart_delivery_sla_p90 %}
90th percentile of delivery time in minutes, rounded to one decimal place. Null or nonnumeric delivery times are excluded from the percentile.
{% enddocs %}
