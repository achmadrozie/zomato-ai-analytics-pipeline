########## 01 Environment setup ##########
import os
import numpy as np
import pandas as pd
import streamlit as st
import snowflake.connector
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-6-luna"
NEW_REVIEWS = 500
top_k = 5
CACHE_FILE = "review_embeddings.parquet"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
########## 02 Fetch reviews from Snowflake ##########
def read_reviews_from_snowflake():
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    query = f"""
        SELECT reviews.REVIEW_ID, restaurant.CITY, reviews.RATING, reviews.COMMENT
        FROM (
            SELECT REVIEW_ID, RESTAURANT_ID, RATING, COMMENT
            FROM ZOMATO.STAGING.STG_ZOMATO__REVIEW
            SAMPLE ({NEW_REVIEWS} ROWS)
        ) AS reviews
        LEFT JOIN ZOMATO.CORE.DIM_RESTAURANT AS restaurant
            ON TRY_TO_NUMBER(reviews.RESTAURANT_ID) = restaurant.RESTAURANT_ID
    """
    df = conn.cursor().execute(query).fetch_pandas_all()
    conn.close()

    df.columns = [col.lower() for col in df.columns]
    # The embeddings API rejects empty input, and staging only drops NULL comments, not blank ones.
    df = df[df["comment"].fillna("").str.strip() != ""].reset_index(drop=True)
    return df

########## 03 Create embeddings ##########
def embed(texts):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts)

    return [item.embedding for item in response.data]
    
########## 04 Load or cache reviews ##########
@st.cache_data()
def load_reviews():
    if os.path.exists(CACHE_FILE):
        return pd.read_parquet(CACHE_FILE)

    df = read_reviews_from_snowflake()
    df['embedding'] = embed(df['comment'].tolist())
    df.to_parquet(CACHE_FILE)
    return df

########## 05 Show app heading ##########
st.html("""
<style>
  [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
  [data-testid="stExpander"] details:focus-within {
    border-color: #16a34a !important;
    box-shadow: 0 0 0 1px #16a34a !important;
  }
</style>
""")

st.title("Chat with your Zomato Reviews")
st.caption(f"Searching {NEW_REVIEWS} review, answering with {CHAT_MODEL} model")

########## 06 Find relevant reviews ##########
def cosine_similarity(vec_a, vec_b):
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

def find_similar_reviews(question, df):
    question_vector = embed([question])[0]

    scores = []
    for review_vector in df['embedding']:
        scores.append(cosine_similarity(question_vector, review_vector))

    df = df.copy()
    df['score'] = scores
    return df.nlargest(top_k, 'score')

########## 07 Generate answer ##########
def ask_llm(question, top_reviews):
    context = ""

    for _, row in top_reviews.iterrows():
        context += f" ({row['city']}, {row['rating']} stars) {row['comment']}\n"

    system_prompt = (
        "Answer ONLY using the customer reviews provided. "
        "Be concise. If the reviews don't covert it, say so"
    )

    user_prompt = f"Questions: {question}\n\nReviews:\n{context}"

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content
    
########## 08 Run chat flow ##########
review_df = load_reviews()

question = st.text_input("Ask a question about your reviews:",
                         placeholder="e.g. What are the most common complaints about delivery?")

if question:
    top_reviews = find_similar_reviews(question, review_df)
    answer = ask_llm(question, top_reviews)

    st.markdown(f"**Answer:**")
    st.write(answer)

    with st.expander("Reviews used to build this answer"):
        st.dataframe(top_reviews[['city', 'rating', 'comment']], hide_index=True)
