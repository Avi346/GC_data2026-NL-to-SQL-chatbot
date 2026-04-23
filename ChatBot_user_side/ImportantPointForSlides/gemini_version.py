import duckdb
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyDj66FrKRDXgJIZjN0Gq7rLXQFUMefLWu0"
DB_PATH = "frammer_analytics.duckdb"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)

con = duckdb.connect(database=DB_PATH, read_only=True)

# --- Schema context for the LLM ---
SCHEMA_CONTEXT = """
You are a SQL expert working with a DuckDB database containing Frammer video production analytics.
There are exactly 2 tables. You MUST pick the correct one based on the user's question.

### TABLE 1: video_details
Use this table when the user asks about individual videos, headlines, sources, or specific video-level details.
Columns:
- headline (VARCHAR): The title/headline of the video (obfuscated)
- source (VARCHAR): Source URL of the video
- team_name (VARCHAR): The team the video belongs to (mostly 'Unknown')
- type (VARCHAR): Content type - 'interview', 'news bulletin', 'speech', 'debate', 'special reports', 'press conference', 'discussion-show', 'sports show', 'podcast', 'drama', 'in-brief'
- uploaded_by (VARCHAR): Name of the user who uploaded the video
- video_id (BIGINT): Unique numeric ID for the video
- published_platform (VARCHAR): Platform where published (e.g., 'YouTube'). Empty if not published.
- published_url (VARCHAR): URL of the published video. Empty if not published.
- is_published (BOOLEAN): Whether the video was published (true/false)
Row count: ~14,918 videos

### TABLE 2: aggregate_metrics_obt
Use this table when the user asks about counts, durations, totals, summaries, channels, or aggregate statistics.
This is a "One Big Table" that merges 10 different summary reports. Use the `metric_focus` column to filter the right slice.
Columns:
- metric_focus (VARCHAR): CRITICAL filter. Possible values:
    'By User' - aggregated per user
    'By Channel and User' - aggregated per channel+user combo
    'By Input Type' - aggregated per content type (interview, speech, etc.)
    'By Output Type' - aggregated per output format (Full package, Key moments, Chapters, etc.)
    'By Language' - aggregated per language (en, hi, mix, etc.)
    'Overall Client Summary' - per-channel totals
    'Monthly Overall' - monthly totals
    'Channel Platform Breakdown' - per-channel publishing counts by platform
- time_period (VARCHAR): 'Overall' or a month like 'Feb, 2026', 'Jan, 2026'
- channel_name (VARCHAR): Channel workspace name (A, B, C, D, etc.). Only filled for channel-related metric_focus values.
- user_name (VARCHAR): User name. Only filled for user-related metric_focus values.
- content_category (VARCHAR): Content type, language, or output type depending on metric_focus.
- uploaded_count (DOUBLE): Number of videos uploaded
- created_count (DOUBLE): Number of videos created
- published_count (DOUBLE): Number of videos published
- uploaded_duration_seconds (DOUBLE): Total upload duration in SECONDS
- created_duration_seconds (DOUBLE): Total creation/editing duration in SECONDS
- published_duration_seconds (DOUBLE): Total published duration in SECONDS
- platform_facebook_count, platform_instagram_count, platform_linkedin_count, platform_reels_count, platform_shorts_count, platform_x_count, platform_youtube_count, platform_threads_count (DOUBLE): Publishing counts per platform. Only filled when metric_focus = 'Channel Platform Breakdown'.
- platform_*_duration_seconds (DOUBLE): Corresponding durations per platform.

IMPORTANT RULES:
1. Always use DuckDB SQL syntax.
2. Duration columns are already in SECONDS. To show hours, divide by 3600. To show minutes, divide by 60.
3. When filtering text values, use exact case as shown above (e.g., 'By User' not 'by user').
4. Return ONLY the raw SQL query. No markdown, no explanation, no backticks.
"""

# --- Router Prompt: decides which table to use ---
ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a routing agent. Given a user question about Frammer video data, decide which table to query.
Reply with EXACTLY one word: either "video_details" or "aggregate_metrics_obt".

Rules:
- "video_details" for questions about specific videos, headlines, listing videos, filtering by uploaded_by, published platform, or video-level lookups.
- "aggregate_metrics_obt" for questions about counts, totals, durations, summaries, channels, users ranked by metrics, monthly trends, or platform publishing breakdowns.
"""),
    ("human", "{question}")
])

# --- SQL Generation Prompt ---
SQL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SCHEMA_CONTEXT),
    ("human", "The router decided to use table: {table}\n\nUser question: {question}\n\nGenerate a DuckDB SQL query to answer this question. Return ONLY the SQL query, nothing else.")
])

# --- Answer Generation Prompt ---
ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful data analyst. Given a user's question and the SQL query results, provide a clear, concise answer in natural language. If duration values are in seconds, convert them to hours and minutes for readability."),
    ("human", "Question: {question}\n\nSQL Query: {sql}\n\nQuery Results:\n{results}\n\nProvide a clear answer:")
])

# --- Build chains ---
router_chain = ROUTER_PROMPT | llm | StrOutputParser()
sql_chain = SQL_PROMPT | llm | StrOutputParser()
answer_chain = ANSWER_PROMPT | llm | StrOutputParser()


def ask(question: str) -> str:
    """Full pipeline: Route -> Generate SQL -> Execute -> Answer."""
    # Step 1: Route to the correct table
    table = router_chain.invoke({"question": question}).strip()
    if table not in ("video_details", "aggregate_metrics_obt"):
        table = "aggregate_metrics_obt"  # safe fallback
    print(f"  [Router] -> {table}")

    # Step 2: Generate SQL
    raw_sql = sql_chain.invoke({"question": question, "table": table}).strip()
    # Clean any accidental markdown wrapping
    raw_sql = raw_sql.replace("```sql", "").replace("```", "").strip()
    print(f"  [SQL]    -> {raw_sql}")

    # Step 3: Execute SQL on DuckDB
    try:
        result_df = con.execute(raw_sql).df()
        results_str = result_df.to_string(index=False)
    except Exception as e:
        results_str = f"SQL Error: {e}"
        print(f"  [Error]  -> {results_str}")

    # Step 4: Generate natural language answer
    answer = answer_chain.invoke({
        "question": question,
        "sql": raw_sql,
        "results": results_str
    })
    return answer


# --- Terminal Chat Loop ---
if __name__ == "__main__":
    print("=" * 60)
    print("  Frammer Analytics NL2SQL Chatbot")
    print("  Type your question and press Enter.")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    while True:
        try:
            question = input("\nYou: ").strip()
            if not question:
                continue
            if question.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            answer = ask(question)
            print(f"\nBot: {answer}")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
