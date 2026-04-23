import os
from pathlib import Path
from typing import Any, AsyncIterator

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from env_loader import load_project_env

from conversation_context import get_last_result, save_last_result
from sql_prompting import AGENT_PREFIX, build_dynamic_sql_input

load_project_env()

BASE_DIR = Path(__file__).resolve().parent


def _resolve_local_path(raw_path: str) -> str:
    path = Path(raw_path)
    if path.is_absolute():
        return str(path)
    return str((BASE_DIR / path).resolve())

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DB_PATH = _resolve_local_path(os.getenv("DB_PATH", "chatbot_user_side.duckdb"))

# Connect via SQLAlchemy with read_only=True to avoid file lock conflicts
db = SQLDatabase.from_uri(
    f"duckdb:///{DB_PATH}", engine_args={"connect_args": {"read_only": True}}
)

llm = ChatGroq(model="openai/gpt-oss-120b", api_key=GROQ_API_KEY, temperature=0)

# In-memory session store for multi-turn conversation
session_store: dict[str, ChatMessageHistory] = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]


sql_agent = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="openai-tools",
    verbose=True,
    prefix=AGENT_PREFIX,
    handle_parsing_errors=True,
    max_iterations=10,
)

agent_with_memory = RunnableWithMessageHistory(
    sql_agent,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)


def invoke_sql_agent(question: str, session_id: str = "default", mode: str = "text") -> dict:
    """Invoke the SQL agent with dynamic prompting, falling back to the raw question."""
    enriched_input = build_dynamic_sql_input(question, top_k=3, mode=mode)
    use_memory = mode != "plot_data"

    def _invoke(payload: str) -> dict:
        if use_memory:
            return agent_with_memory.invoke(
                {"input": payload},
                config={"configurable": {"session_id": session_id}},
            )
        return sql_agent.invoke({"input": payload})

    try:
        return _invoke(enriched_input)
    except Exception:
        if enriched_input == question:
            raise
        return _invoke(question)


def _extract_text_from_chunk(chunk: Any) -> str:
    """Extract plain text token content from LangChain chunk payloads."""
    if chunk is None:
        return ""
    content = getattr(chunk, "content", chunk)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text" and isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("text"), str):
                    parts.append(item["text"])
        return "".join(parts)
    return ""


def _extract_output_text(obj: Any) -> str:
    """Best-effort extraction of final answer text from nested event payloads."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for key in ("output", "final_output", "answer", "result"):
            if key in obj:
                text = _extract_output_text(obj[key])
                if text:
                    return text
        return ""
    if isinstance(obj, list):
        for item in obj:
            text = _extract_output_text(item)
            if text:
                return text
    return ""


def _status_for_tool(name: str, is_start: bool) -> str:
    tool_name = (name or "").lower()
    if "sql_db_schema" in tool_name:
        return "Inspecting table schema..." if is_start else "Schema ready."
    if "sql_db_query_checker" in tool_name:
        return "Validating SQL query..." if is_start else "Query validated."
    if "sql_db_query" in tool_name:
        return "Searching database..." if is_start else "Database results received."
    if "sql_db_list_tables" in tool_name:
        return "Listing available tables..." if is_start else "Tables listed."
    return "Running tool..." if is_start else "Tool completed."


async def stream_sql_agent_events(
    question: str, session_id: str = "default", mode: str = "text"
) -> AsyncIterator[dict[str, Any]]:
    """
    Stream SQL-agent execution using astream_events(v2).
    Emits dict chunks:
    - {"type": "status", "message": "..."}
    - {"type": "token", "message": "..."}
    - {"type": "final", "reply": "..."}
    """
    enriched_input = build_dynamic_sql_input(question, top_k=3, mode=mode)
    use_memory = mode != "plot_data"
    candidate_payloads = [enriched_input] if enriched_input == question else [enriched_input, question]

    last_error: Exception | None = None
    for payload in candidate_payloads:
        runnable = agent_with_memory if use_memory else sql_agent
        input_payload = {"input": payload}
        config = {"configurable": {"session_id": session_id}} if use_memory else {}
        token_parts: list[str] = []
        final_output = ""

        try:
            async for event in runnable.astream_events(
                input_payload,
                config=config,
                version="v2",
            ):
                event_type = event.get("event", "")
                if event_type == "on_tool_start":
                    yield {"type": "status", "message": _status_for_tool(event.get("name", ""), True)}
                    continue
                if event_type == "on_tool_end":
                    yield {"type": "status", "message": _status_for_tool(event.get("name", ""), False)}
                    continue
                if event_type in {"on_chat_model_stream", "on_llm_stream"}:
                    chunk = event.get("data", {}).get("chunk")
                    token = _extract_text_from_chunk(chunk)
                    if token:
                        token_parts.append(token)
                        yield {"type": "token", "message": token}
                    continue
                if event_type in {"on_chain_end", "on_agent_finish"}:
                    output_candidate = _extract_output_text(event.get("data"))
                    if output_candidate:
                        final_output = output_candidate

            final_text = final_output or "".join(token_parts).strip()
            yield {"type": "final", "reply": final_text or "I could not generate an answer."}
            return
        except Exception as exc:
            last_error = exc
            # Try fallback payload if available.
            continue

    if last_error:
        raise last_error
    yield {"type": "final", "reply": "I could not generate an answer."}


def ask(question: str, session_id: str = "default") -> str:
    """Run the SQL agent with memory and dynamic RAG few-shot examples."""
    result = invoke_sql_agent(question, session_id=session_id, mode="text")
    return result.get("output", "I could not generate an answer.")


FOLLOWUP_CONTEXT_SYSTEM = """You are a concise analytics assistant.

The user is asking a follow-up about the immediately previous result in this same session.
Answer using ONLY the provided last-result context.

Rules:
- Treat references like "above", "this", "that", and "tell me more" as referring to the immediately previous saved result.
- Do not mention database tables, SQL, schema, or technical implementation details.
- If the last result is a chart, explain the chart's meaning using the saved summary and computed chart facts.
- If the last result is a text answer, expand on that answer directly and stay consistent with it.
- If the saved context is too limited to answer safely, say that briefly and ask the user what specific detail they want.
- Do not claim a trend, cause, or comparison unless it is directly supported by the provided chart facts.
- If the chart contains both rises and dips, describe it as fluctuating rather than steadily increasing or decreasing.
- Be direct, helpful, and professional.
- Return your final answer in valid Markdown.
- Prefer a compact structure:
  - `### Answer`
  - `### Key Points` (2-4 bullets)
"""


def answer_followup_from_context(question: str, session_id: str = "default") -> str | None:
    """Answer ambiguous follow-ups from the last saved result instead of loose chat history."""
    last_result = get_last_result(session_id)
    if not last_result:
        return None

    context_payload = {
        "result_type": last_result.get("result_type"),
        "question": last_result.get("question"),
        "reply": last_result.get("reply"),
        "source_question": last_result.get("source_question"),
        "source_reply": last_result.get("source_reply"),
        "data_sample": last_result.get("data_sample"),
        "data_columns": last_result.get("data_columns"),
        "source_data_sample": last_result.get("source_data_sample"),
        "source_data_columns": last_result.get("source_data_columns"),
        "chart_facts": last_result.get("chart_facts"),
        "source_chart_facts": last_result.get("source_chart_facts"),
    }

    response = llm.invoke(
        [
            SystemMessage(content=FOLLOWUP_CONTEXT_SYSTEM),
            HumanMessage(
                content=(
                    f"LAST RESULT CONTEXT:\n{context_payload}\n\n"
                    f"FOLLOW-UP QUESTION:\n{question}"
                )
            ),
        ]
    )
    return response.content.strip()


def save_text_result_context(
    session_id: str,
    question: str,
    reply: str,
) -> None:
    save_last_result(
        session_id,
        {
            "result_type": "text",
            "question": question,
            "reply": reply,
            "data_sample": None,
            "data_columns": None,
        },
    )


FOLLOWUP_PLOT_REWRITE_SYSTEM = """You rewrite ambiguous chart follow-up requests into a single standalone chart request.

You will receive:
- the user's current follow-up message
- the last saved result in the session

Rules:
- Resolve references like "above", "this", and "that" using the saved result only.
- If the saved result is a text answer about the top item in a category, prefer a chart of the broader comparison behind that answer, not a single-bar chart of only the winner.
- If the saved result is already a chart, preserve its topic and requested metric.
- Keep the request grounded in the available context and write one clear standalone plotting request.
- Return ONLY the rewritten user request, with no explanation.
"""


def rewrite_followup_plot_question(question: str, session_id: str = "default") -> str | None:
    """Rewrite ambiguous plot follow-ups into a standalone grounded chart request."""
    last_result = get_last_result(session_id)
    if not last_result:
        return None

    context_payload = {
        "result_type": last_result.get("result_type"),
        "source_question": last_result.get("source_question"),
        "source_reply": last_result.get("source_reply"),
        "latest_question": last_result.get("question"),
        "latest_reply": last_result.get("reply"),
        "source_data_sample": last_result.get("source_data_sample"),
        "source_data_columns": last_result.get("source_data_columns"),
        "source_chart_facts": last_result.get("source_chart_facts"),
    }

    response = llm.invoke(
        [
            SystemMessage(content=FOLLOWUP_PLOT_REWRITE_SYSTEM),
            HumanMessage(
                content=(
                    f"LAST RESULT CONTEXT:\n{context_payload}\n\n"
                    f"FOLLOW-UP PLOT REQUEST:\n{question}"
                )
            ),
        ]
    )
    return response.content.strip()


if __name__ == "__main__":
    print("=" * 60)
    print("  Frammer Analytics NL2SQL Chatbot (SQL Agent + Memory)")
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

            answer = ask(question, session_id="terminal")
            print(f"\nBot: {answer}")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
