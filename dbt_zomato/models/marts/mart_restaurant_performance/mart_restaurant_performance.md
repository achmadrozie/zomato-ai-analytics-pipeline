{% docs mart_restaurant_performance %}
Restaurant summary with one row per restaurant ID from orders. Order measures come from `fact_order`; restaurant name, city, and cuisine come from `dim_restaurant`. Monetary values are not converted between currencies.
{% enddocs %}

{% docs mart_restaurant_performance_restaurant_id %}
Restaurant identifier recorded on orders, used to join the restaurant dimension.
{% enddocs %}

{% docs mart_restaurant_performance_restaurant_name %}
Restaurant name from `dim_restaurant`, when an identifier match exists.
{% enddocs %}

{% docs mart_restaurant_performance_city %}
Restaurant city from `dim_restaurant`, when an identifier match exists.
{% enddocs %}

{% docs mart_restaurant_performance_cuisine %}
Restaurant cuisine from `dim_restaurant`, when an identifier match exists.
{% enddocs %}

{% docs mart_restaurant_performance_orders %}
Number of orders for the restaurant, regardless of status.
{% enddocs %}

{% docs mart_restaurant_performance_revenue %}
Sum of `fact_order.delivered_sales_amount`. Unparseable source sales amounts do not contribute to the sum.
{% enddocs %}

{% docs mart_restaurant_performance_avg_customer_rating %}
Average nonnull numeric customer rating on orders, rounded to two decimal places.
{% enddocs %}

{% docs mart_restaurant_performance_avg_delivery_min %}
Average nonnull numeric delivery time on orders, in minutes and rounded to one decimal place.
{% enddocs %}
