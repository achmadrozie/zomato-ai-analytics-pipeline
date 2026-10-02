USE ROLE accountadmin;

-- Compute: extra-small, auto-suspend fast so the trial credits last.
CREATE WAREHOUSE IF NOT EXISTS ZOMATO_WH
    WAREHOUSE_SIZE      = 'XSMALL'
    AUTO_SUSPEND        = 60 -- time limit once the computation is not use for a period of time, in second
    AUTO_RESUME         = TRUE -- auto turn on the compute when the query is initiated
    INITIALLY_SUSPENDED = TRUE; -- warehouse starts in suspended state when created

-- Database + medallion schemas.
CREATE DATABASE IF NOT EXISTS ZOMATO;
CREATE SCHEMA  IF NOT EXISTS ZOMATO.SOURCES;        -- store data from backend
CREATE SCHEMA  IF NOT EXISTS ZOMATO.STAGING;        -- column standardization
CREATE SCHEMA  IF NOT EXISTS ZOMATO.INTERMEDIATE;   -- data manipulation and join
CREATE SCHEMA  IF NOT EXISTS ZOMATO.CORE;           -- core models - cannonical model - left join inly
CREATE SCHEMA  IF NOT EXISTS ZOMATO.MARTS;          -- aggregated version of core model(s) - combined
CREATE SCHEMA  IF NOT EXISTS ZOMATO.SNAPSHOTS;      -- SCD2 history (dbt)
CREATE SCHEMA  IF NOT EXISTS ZOMATO.AI;             -- LLM-enriched tables (OpenAI jobs)

-- A role dbt/Airflow will use.
CREATE ROLE IF NOT EXISTS DBT_ROLE;
GRANT USAGE   ON WAREHOUSE ZOMATO_WH TO ROLE DBT_ROLE;
GRANT OPERATE ON WAREHOUSE ZOMATO_WH TO ROLE DBT_ROLE;
GRANT ALL     ON DATABASE  ZOMATO    TO ROLE DBT_ROLE;
GRANT ALL     ON ALL SCHEMAS IN DATABASE ZOMATO TO ROLE DBT_ROLE;
GRANT ALL     ON FUTURE SCHEMAS IN DATABASE ZOMATO TO ROLE DBT_ROLE;
GRANT ALL     ON FUTURE TABLES IN DATABASE ZOMATO TO ROLE DBT_ROLE;
GRANT ALL     ON FUTURE VIEWS  IN DATABASE ZOMATO TO ROLE DBT_ROLE;

-- Let your login use the role (replace with your Snowflake username).
SET my_user = CURRENT_USER();
GRANT ROLE DBT_ROLE TO USER IDENTIFIER($my_user);

SELECT 'setup complete' AS status;