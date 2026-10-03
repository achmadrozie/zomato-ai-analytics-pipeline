USE ROLE ACCOUNTADMIN;
USE DATABASE ZOMATO;
USE SCHEMA SOURCES;

CREATE OR REPLACE TABLE SOURCES.restaurants (
    _idx STRING
    , id STRING
    , name STRING
    , city STRING
    , rating STRING
    , rating_count STRING
    , cost STRING
    , cuisine STRING
    , lic_no STRING
    , link STRING
    , address STRING
    , menu STRING
);

CREATE OR REPLACE TABLE SOURCES.food (
    _idx STRING
    , f_id STRING
    , item STRING
    , veg_or_non_veg STRING
);

CREATE OR REPLACE TABLE SOURCES.menu (
    _idx STRING
    , menu_id STRING
    , r_id STRING
    , f_id STRING
    , cuisine STRING
    , price STRING
);

CREATE OR REPLACE TABLE SOURCES.order_items (
    order_item_id STRING
    , order_id STRING
    , r_id STRING
    , f_id STRING
    , price STRING
    , quantity STRING
    , line_amount STRING
);

CREATE OR REPLACE TABLE SOURCES.orders (
  order_id STRING
  , order_timestamp STRING
  , order_date STRING
  , user_id STRING
  , r_id STRING
  , restaurant_city STRING
  , cuisine STRING
  , items_count STRING
  , sales_qty STRING
  , subtotal STRING
  , discount STRING
  , delivery_fee STRING
  , gst STRING
  , sales_amount STRING
  , currency STRING
  , payment_method STRING
  , order_status STRING
  , customer_rating STRING
  , delivery_time_min STRING
);

CREATE OR REPLACE TABLE SOURCES.reviews (
    review_id STRING
    , order_id STRING
    , user_id STRING
    , restaurant_id STRING
    , rating STRING
    , comment STRING
    , review_date STRING
);

CREATE OR REPLACE TABLE SOURCES.users (
    _idx STRING
    , user_id STRING
    , name STRING
    , email STRING
    , password STRING
    , age STRING
    , gender STRING
    , marital_status STRING
    , occupation STRING
    , monthly_income STRING
    , educational_qualifications STRING
    , family_size STRING
);


SELECT * FROM food LIMIT 5;