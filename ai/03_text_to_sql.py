################ 1. Environtment, Context Guardrail Setup ################
import os
import numpy as np
import pandas as pd
import streamlit as st
import snowflake.connector
from openai import OpenAI
import json
import sqlparse
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-6-luna"

FORBIDDEN_WORDS = ['drop', 'delete', 'truncate', 'alter', 'update', 'insert', 'create', 'replace', 'grant', 'revoke']

EXAMPLE_QUESTIONS = [
    "Top 10 cities by GMV",
    "Which cuisin has the most orders?",
    "Average delivery time by city, worst first",
    "Cancel rate by payment method"
]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCHEMA = """
Tables available in database ZOMATO (use these exact schema-qualified names):
CORE.FACT_ORDER(order_id, order_date, customer_id, restaurant_id, city, cuisine,
                payment_method, order_status, is_delivered, is_cancelled,
                sales_amount, delivered_sales_amount, customer_rating, delivery_time_min)
MARTS.MART_DAILY_CITY_REVENUE(order_date, city, orders, delivered_orders,
                              cancel_rate, gmv, aov)
MARTS.MART_RESTAURANT_PERFORMANCE(restaurant_id, restaurant_name, city, cuisine,
                                  orders, revenue, avg_customer_rating, avg_delivery_min)
MARTS.MART_DELIVERY_SLA(city, order_hour, delivered_orders, p50, p90)

CORE.FACT_ORDER has one row per order. For cancellation rate by payment method,
group CORE.FACT_ORDER by payment_method and calculate
100.0 * COUNT_IF(is_cancelled) / NULLIF(COUNT(*), 0).
Use a MARTS table only when it has every dimension and measure needed by the question.
"""
 
SYSTEM_PROMPT = f"""
You are a Snowflake SQL expert. Write ONE SELECT query that answers the question.
 
Rules:
- SELECT queries only, never modify data.
- Use the exact schema-qualified table names listed above.
- Add a LIMIT of 100 or less, unless the question asks for a single total.
- Reply as JSON in this exact format: {{"sql": "your query here"}}
 
{SCHEMA}
"""

################ 2. Get Connection to Snowflake ################

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="MARTS",
        role="DBT_ROLE",
        login_timeout=10,
        network_timeout=10,
        socket_timeout=10,
        session_parameters={"STATEMENT_TIMEOUT_IN_SECONDS": 60},
    )

def check_connection():
    cursor = get_connection().cursor()
    try:
        cursor.execute("SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
        return cursor.fetchone()
    finally:
        cursor.close()

################ 3. Generate SQL ################

def generate_sql(question):
    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]
    )
    answer = response.choices[0].message.content
    sql = json.loads(answer)["sql"]

    sql = sql.replace("ZOMATO.", "")
    return sql.strip().rstrip(";")

################ 4. Safety guard ################

def is_safe(sql):
    lowered = sql.lower()

    if not lowered.startswith("select") and not lowered.startswith("with"):
        return False

    for word in FORBIDDEN_WORDS:
        if word in lowered:
            return False

    return True

################ 5. Run query ################
def run_query(sql):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        return cursor.execute(sql).fetch_pandas_all()
    finally:
        cursor.close()

################ 6. UI + main flow ################
def main():
    st.title("Chat with your Zomato Data")
    st.caption(f"Ask in English, {MODEL} writes the SQL, Snowflake runs it")

    with st.sidebar:
        st.header("Example Questions")
        for q in EXAMPLE_QUESTIONS:
            st.markdown(f" - {q}")

        if st.button("Check Snowflake connection"):
            try:
                with st.spinner("Connecting to Snowflake..."):
                    role, database, schema = check_connection()
                st.success(f"Connected: {role} · {database}.{schema}")
            except Exception as e:
                get_connection.clear()
                st.error(f"Snowflake connection failed: {e}")
            st.stop()

    question = st.text_input("Enter your question here", 
                            placeholder="e.g. Top 10 restaurants by revenune in Banglore")


    if question:
        sql = generate_sql(question)
        formatted_sql = sqlparse.format(sql, reindent=True, keyword_case="upper")
        st.code(formatted_sql, language="sql")

        if not is_safe(sql):
            st.error("The generated SQL is not safe to run. Please modify your question.")

        else:
            try:
                df = run_query(sql)
                st.success(f"{len(df)} rows returned")
                st.dataframe(df, hide_index=True)

                if len(df.columns) == 2 and pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
                    st.bar_chart(df, x=df.columns[0], y=df.columns[1])

            except Exception as e:
                st.error(f"Error running query: {e}")

main()
