{% docs mart_daily_city_revenue %}
Daily order and revenue summary at one row per order date and city, built from `fact_order`. Monetary values use `sales_amount` from the order fact and are not converted between currencies.
{% enddocs %}

{% docs mart_daily_city_revenue_order_date %}
Calendar date of the order from `fact_order.order_date`.
{% enddocs %}

{% docs mart_daily_city_revenue_city %}
City recorded on the order.
{% enddocs %}

{% docs mart_daily_city_revenue_orders %}
Number of orders, regardless of status.
{% enddocs %}

{% docs mart_daily_city_revenue_delivered_orders %}
Number of orders whose `is_delivered` flag is true.
{% enddocs %}

{% docs mart_daily_city_revenue_cancel_rate %}
Cancelled orders divided by all orders in the date and city group, rounded to four decimal places.
{% enddocs %}

{% docs mart_daily_city_revenue_gmv %}
Sum of `fact_order.delivered_sales_amount`. Unparseable source sales amounts are null and do not contribute to the sum.
{% enddocs %}

{% docs mart_daily_city_revenue_aov %}
GMV divided by delivered order count, rounded to two decimal places; zero when the group has no delivered orders.
{% enddocs %}
