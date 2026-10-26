########## 01 Environment setup ##########
import os
import json
import snowflake.connector
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-6-luna"

SAMPLE_N = 100
TOPICS = [
    "food_quality"
    , "delivery"
    , "pricing"
    , "service"
    , "packaging"
    , "courier_behavior"
    , "others"
]


"""
MENTAL MODEL
0. Setup: Set the model, batch limit, topics, prompt, and OpenAI client.
1. Connect: Open Snowflake and create the output table if needed.
2. Fetch: Get up to SAMPLE_N unprocessed reviews; stop if none.
3. Classify: Call OpenAI per review, validate labels, and skip failures.
4. Save: Insert successful results and commit.
5. Close: Close the Snowflake cursor and connection after saving.
"""
# Get connection through Open API Key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System Prompt
SYSTEM_PROMPT = """Classify this Zomato food delivery review.
Use a sentiment_score from -1.0 to 1.0. Set key_issue to a phrase of at most
six words describing the main issue, or null if there is no issue."""

REVIEW_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "review_classification",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "sentiment_label": {
                    "type": "string",
                    "enum": ["positive", "negative", "neutral"],
                },
                "sentiment_score": {"type": "number"},
                "topic": {"type": "string", "enum": TOPICS},
                "key_issue": {"type": ["string", "null"]},
            },
            "required": ["sentiment_label", "sentiment_score", "topic", "key_issue"],
            "additionalProperties": False,
        },
    },
}

########## 02 Connect to Snowflake ##########
def get_connection():
    for attempt in range(1, 4):
        print(f"Connecting to Snowflake (attempt {attempt}/3)...", flush=True)
        try:
            return snowflake.connector.connect(
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
                database=os.getenv("SNOWFLAKE_DATABASE"),
                schema=os.getenv("SNOWFLAKE_SCHEMA"),
                login_timeout=5,
                network_timeout=5,
                socket_timeout=5,
            )
        except snowflake.connector.errors.Error:
            if attempt == 3:
                raise
            print("Snowflake connection failed; retrying...", flush=True)

########## 03 Prepare output table on the Snowflake ##########
def create_output_table(cursor):
    print('creating table output')
    cursor.execute("CREATE SCHEMA IF NOT EXISTS ZOMATO.AI")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ZOMATO.AI.REVIEW_ENRICHED (
            REVIEW_ID STRING,
            SENTIMENT_LABEL STRING,
            SENTIMENT_SCORE FLOAT,
            TOPIC STRING,
            KEY_ISSUE STRING,
            MODEL STRING,
            ENRICHED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """
    )

########## 04 Fetch new reviews from Snowflake ##########
def get_reviews_to_enrich(cursor):
    cursor.execute(f"""
        SELECT 
            REVIEW_ID
            , COMMENT
        FROM ZOMATO.SOURCES.REVIEWS
        WHERE REVIEW_ID NOT IN (SELECT REVIEW_ID FROM ZOMATO.AI.REVIEW_ENRICHED)
        LIMIT {SAMPLE_N}
    """)
    return cursor.fetchall()

########## 05 Classify fetched review (if any) ##########
def classify_review(comment):
    response = client.chat.completions.create(
        model=MODEL,
        response_format=REVIEW_RESPONSE_FORMAT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": comment}
        ]
    )
    answer = response.choices[0].message.content
    labels = json.loads(answer)

    # GUARDRAIL: The schema checks types, but these two content rules still need validation.
    if not -1.0 <= labels["sentiment_score"] <= 1.0:
        raise ValueError("sentiment_score must be between -1.0 and 1.0")
    issue = labels["key_issue"]
    if issue is not None and (not issue.strip() or len(issue.split()) > 6):
        raise ValueError("key_issue must be null or a phrase of at most six words")

    return labels

########## 06 Save enriched reviews into Snowflake ##########
def save_results(cursor, results):
    """Insert all the enriched rows into Snowflake in one go."""
    print(f"Saving {len(results)} enriched reviews to Snowflake...")
    cursor.executemany(
        """
        INSERT INTO ZOMATO.AI.REVIEW_ENRICHED
            (review_id, sentiment_label, sentiment_score, topic, key_issue, model)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        results,
    )

########## 07 MAIN function ##########
def main():
    conn = get_connection()
    cursor = conn.cursor()
    create_output_table(cursor)
    reviews = get_reviews_to_enrich(cursor)

    if len(reviews) == 0:
        print("No new reviews to enrich.")
        return

    print(f"Enriching {len(reviews)} reviews...")

    results = []
    for review_id, comment in reviews:
        print(f"Classifying review {review_id}: {comment}")
        try:
            labels = classify_review(comment)
            print(f"Labels for review {review_id}: {labels}")
            results.append((
                review_id,
                labels["sentiment_label"],
                labels["sentiment_score"],
                labels["topic"],
                labels["key_issue"],
                MODEL
            ))
        except Exception as e:
            print(f"Error occurred while classifying review {review_id}: {e}")

    save_results(cursor, results)
    print(f"Saved {len(results)} enriched reviews to Snowflake.")
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
