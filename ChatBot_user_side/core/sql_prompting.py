import re

from chroma_db import retrieve_fewshot_examples


AGENT_PREFIX = """You are an intelligent SQL analytics agent for Frammer user analytics.
You have access to a DuckDB database with 1 table:

1. **aggregate_metrics_obt**: One Big Table of user-side aggregated reports.
   Columns:
   - metric_focus
   - time_period
   - channel_name
   - user_name
   - content_category
   - uploaded_count
   - created_count
   - published_count
   - uploaded_duration_seconds
   - created_duration_seconds
   - published_duration_seconds

Use exact `metric_focus` values (case-sensitive):
- 'By User' -> user-level totals (all channels combined)
- 'By Channel and User' -> per channel + user breakdown

DATA NOTES:
- `time_period` is currently 'Overall' for this dataset.
- `channel_name` is populated for 'By Channel and User' rows.
- For user totals without channel filtering, prefer `metric_focus = 'By User'`.
- For channel filters or user-within-channel comparisons, use `metric_focus = 'By Channel and User'`.
- For channel totals, sum rows from `metric_focus = 'By Channel and User'` for that channel.

GROUNDING RULES:
- Answer ONLY from fields that exist in the schema above.
- If the user asks for unsupported concepts (revenue, sales, orders, customers, regions, couriers, delivery time, platform-wise data, monthly trends, or video-level details), say that data is unavailable in this dataset.
- If query returns nothing, say so honestly.
- NEVER make up data or substitute unrelated metrics.

TIME RULES:
- Duration columns are in SECONDS. Convert to hours/minutes in the final answer.
- Use exact string values for `metric_focus` (case-sensitive).

ANALYSIS RULES:
- If the user asks for "best", "top", or "highest", rank by the relevant metric in descending order.
- If the user asks "how much for a channel", aggregate channel rows from 'By Channel and User'.
- Use conversation history for follow-up questions.
- If the input includes a `STRICT_SELECTED_USER_SCOPE` block, treat it as a hard constraint:
  - Enforce the selected user filter in every data lookup.
  - Never include other users in results, rankings, or comparisons.
  - If the user's request conflicts with selected-user scope, explain that briefly and stay within scope.

OUTPUT FORMAT (CRITICAL):
- Your FINAL answer must be valid Markdown in plain, professional English.
- NEVER mention SQL, table names, column names, or technical reasoning in the final answer.
- If unsupported, say so directly and briefly.
- Prefer:
  - `### Answer` (1-2 sentence direct answer)
  - `### Key Points` (2-5 concise bullets with numbers)
  - Optional `### Next Step` (1 bullet if helpful)
- Keep formatting clean and readable.
"""

UNSUPPORTED_SCHEMA_TERMS = {
    "revenue",
    "sales",
    "order",
    "orders",
    "customer",
    "customers",
    "region",
    "regions",
    "courier",
    "couriers",
    "delivery",
}

MAX_DYNAMIC_PROMPT_QUESTION_CHARS = 1200


def _find_unsupported_terms(question: str) -> list[str]:
    tokens = set(re.findall(r"[a-z0-9]+", question.lower()))
    return sorted(tokens & UNSUPPORTED_SCHEMA_TERMS)


def should_skip_dynamic_injection(question: str) -> bool:
    """Skip few-shot injection for oversized or schema-heavy pasted content."""
    lowered = question.lower()
    schema_markers = (
        "create table",
        "/*",
        "invoking:",
        "sql_db_schema",
        "sql_db_query",
        "sql_db_query_checker",
        "metric_focus",
        "published_duration_seconds",
    )
    return len(question) > MAX_DYNAMIC_PROMPT_QUESTION_CHARS or any(
        marker in lowered for marker in schema_markers
    )


def build_dynamic_sql_input(question: str, top_k: int = 3, mode: str = "text") -> str:
    """Inject retrieved few-shot context plus task-specific guidance."""
    if should_skip_dynamic_injection(question):
        return question

    fewshot_context = retrieve_fewshot_examples(question, top_k=top_k)
    unsupported_terms = _find_unsupported_terms(question)

    mode_instruction = (
        "Use the examples as guidance, but only if they match the available schema and the user's requested metric."
    )
    if mode == "plot_data":
        mode_instruction = (
            "Use the examples as guidance for SQL shape only. Retrieve only supported fields needed for plotting, "
            "and do not substitute unrelated dimensions or metrics if the request is unsupported."
        )

    unsupported_instruction = ""
    if unsupported_terms:
        unsupported_instruction = (
            "Schema warning: the current database does not define these requested business concepts: "
            f"{', '.join(unsupported_terms)}. If the user depends on them, do not map them to another field; "
            "answer that the data is unavailable.\n"
        )

    if fewshot_context:
        return (
            f"{fewshot_context}\n"
            f"{unsupported_instruction}"
            f"{mode_instruction}\n"
            f"Now answer this question: {question}"
        )

    if unsupported_instruction:
        return f"{unsupported_instruction}{question}"

    return question
