import json
import re
import asyncio
import os
import sys
import importlib.util
from pathlib import Path
from functools import lru_cache
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

ADMIN_CORE_DIR = (Path(__file__).resolve().parent / "admin_backend" / "core").resolve()
if str(ADMIN_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(ADMIN_CORE_DIR))

from admin_backend.core.chatbot import (
    answer_followup_from_context,
    invoke_sql_agent,
    stream_sql_agent_events,
    rewrite_followup_plot_question,
    save_text_result_context,
)
from admin_backend.core.conversation_context import (
    get_last_result,
    is_followup_question,
    is_plot_explanation_question,
    is_plot_like_question,
    update_last_result,
)
from admin_backend.core.intent_classifier import classify_intent
from admin_backend.core.comparison_plot_agent import (
    is_comparison_plot_request,
    handle_comparison_plot_request,
)
from admin_backend.core.kpi_discovery_agent import handle_kpi_request, handle_kpi_request_with_progress
from admin_backend.core.plotting_agent import handle_plot_request

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
USER_APP_DIR = (BASE_DIR / "ChatBot_user_side").resolve()
USER_APP_FILE = USER_APP_DIR / "api.py"


def _resolve_local_path(raw_path: str) -> str:
    path = Path(raw_path)
    if path.is_absolute():
        return str(path)
    return str((BASE_DIR / path).resolve())


@lru_cache(maxsize=1)
def _load_user_api_module():
    """
    Load ChatBot_user_side/api.py as an isolated module and ensure
    its local imports resolve from ChatBot_user_side first.
    """
    if not USER_APP_FILE.exists():
        raise RuntimeError(f"User API file not found: {USER_APP_FILE}")

    user_dir = str(USER_APP_DIR)
    user_module_names = [
        "chatbot",
        "conversation_context",
        "intent_classifier",
        "comparison_plot_agent",
        "kpi_discovery_agent",
        "plotting_agent",
        "sql_prompting",
        "chroma_db",
        "kpi_injection",
        "env_loader",
    ]

    # Ensure user-side imports are not shadowed by already-loaded root modules.
    for mod_name in user_module_names:
        if mod_name in sys.modules:
            del sys.modules[mod_name]

    if user_dir not in sys.path:
        sys.path.insert(0, user_dir)
    else:
        # Keep user dir at highest priority for imports like `chatbot`.
        sys.path.remove(user_dir)
        sys.path.insert(0, user_dir)

    spec = importlib.util.spec_from_file_location("chatbot_user_api_module", str(USER_APP_FILE))
    if not spec or not spec.loader:
        raise RuntimeError("Could not load ChatBot_user_side/api.py module spec.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

app = FastAPI(title="Frammer NL2SQL API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def healthcheck():
    return {
        "status": "ok",
        "mode": "admin",
        "supports_user_filter": False,
    }


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    user_filter_enabled: bool = False
    user_name: str | None = None


class ChatResponse(BaseModel):
    reply: str
    chart_image: str | None = None
    kpis: list[dict[str, Any]] | None = None
    kpi_sources: list[str] | None = None
    kpi_source_routes: list[str] | None = None
    is_kpi_response: bool = False


VALID_USERS_CSV = os.getenv(
    "VALID_USERS_CSV",
    "data/admin/combined_data(2025-3-1-2026-2-28) by user.csv",
)
VALID_USERS_CSV = _resolve_local_path(VALID_USERS_CSV)


@lru_cache(maxsize=1)
def _load_valid_user_lookup() -> dict[str, str]:
    try:
        df = pd.read_csv(VALID_USERS_CSV, usecols=["User"])
    except Exception as exc:
        raise RuntimeError(
            f"Could not load valid users from '{VALID_USERS_CSV}'."
        ) from exc

    lookup: dict[str, str] = {}
    for raw in df["User"].dropna().astype(str):
        name = raw.strip()
        if not name:
            continue
        key = name.casefold()
        if key not in lookup:
            lookup[key] = name
    return lookup


def _valid_users_sorted() -> list[str]:
    return sorted(_load_valid_user_lookup().values(), key=str.casefold)


def _normalize_scoped_user(
    user_filter_enabled: bool,
    user_name: str | None,
) -> str | None:
    if not user_filter_enabled:
        return None

    if not user_name or not user_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Please provide a user name when user filter is enabled.",
        )

    lookup = _load_valid_user_lookup()
    canonical_name = lookup.get(user_name.strip().casefold())
    if not canonical_name:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid user name '{user_name.strip()}'.",
        )
    return canonical_name


def _scoped_session_id(session_id: str, scoped_user: str | None) -> str:
    if not scoped_user:
        return session_id
    return f"{session_id}::user::{scoped_user.casefold()}"


def _apply_user_scope(question: str, scoped_user: str | None) -> str:
    if not scoped_user:
        return question

    safe_user = scoped_user.replace("'", "''")
    return (
        f"{question}\n\n"
        "STRICT_SELECTED_USER_SCOPE:\n"
        f"- The selected user is exactly: '{safe_user}'.\n"
        f"- Every data lookup must use user_name = '{safe_user}'.\n"
        "- Do not include other users in comparisons, rankings, summaries, or totals.\n"
        "- If the question asks for all users/team/global values, refuse briefly and say this session is locked to the selected user only.\n"
        "- Treat references like 'my', 'me', and 'mine' as the selected user above.\n"
        "- If data is missing for the selected user, say so clearly."
    )


def _stream_event(event: str, payload: dict[str, Any] | None = None) -> str:
    body = json.dumps(payload or {}, ensure_ascii=True)
    return f"event: {event}\ndata: {body}\n\n"


def _ndjson(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False) + "\n"


def _iter_text_chunks(text: str, chunk_size: int = 80):
    words = text.split()
    if not words:
        return

    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > chunk_size:
            yield current + " "
            current = word
        else:
            current = candidate

    if current:
        yield current


def _iter_word_tokens(text: str):
    if not text:
        return
    for token in re.findall(r"\S+\s*", text):
        yield token


def _resolve_followup(question: str, session_id: str) -> tuple[str, str | None]:
    active_question = question
    direct_reply = None

    if not is_followup_question(question):
        return active_question, direct_reply

    if is_plot_explanation_question(question):
        direct_reply = answer_followup_from_context(question, session_id=session_id)
        if direct_reply:
            if get_last_result(session_id):
                update_last_result(
                    session_id,
                    question=question,
                    reply=direct_reply,
                )
            else:
                save_text_result_context(
                    session_id,
                    question=question,
                    reply=direct_reply,
                )
            return active_question, direct_reply

    if is_plot_like_question(question):
        rewritten_plot_question = rewrite_followup_plot_question(
            question, session_id=session_id
        )
        if rewritten_plot_question:
            active_question = rewritten_plot_question
            return active_question, direct_reply

    direct_reply = answer_followup_from_context(question, session_id=session_id)
    if direct_reply:
        if get_last_result(session_id):
            update_last_result(
                session_id,
                question=question,
                reply=direct_reply,
            )
        else:
            save_text_result_context(
                session_id,
                question=question,
                reply=direct_reply,
            )

    return active_question, direct_reply


def _process_chat_request(
    question: str,
    session_id: str,
    scoped_user: str | None = None,
) -> ChatResponse:
    active_question, followup_reply = _resolve_followup(question, session_id)
    if followup_reply:
        return ChatResponse(reply=followup_reply)

    scoped_question = _apply_user_scope(active_question, scoped_user)

    if is_comparison_plot_request(scoped_question):
        result = handle_comparison_plot_request(scoped_question, session_id=session_id)
        return ChatResponse(
            reply=result.get("reply", "I could not generate a comparison chart."),
            chart_image=result.get("chart_image"),
        )

    intent = classify_intent(active_question)

    if intent == "plot":
        result = handle_plot_request(scoped_question, session_id=session_id)
        return ChatResponse(
            reply=result.get("reply", "I could not generate a chart."),
            chart_image=result.get("chart_image"),
        )

    if intent == "kpi":
        try:
            result = handle_kpi_request(scoped_question, selected_user=scoped_user)
        except TypeError:
            result = handle_kpi_request(scoped_question)
        return ChatResponse(
            reply=result.get("reply", "I could not generate KPI suggestions."),
            kpis=result.get("kpis"),
            kpi_sources=result.get("kpi_sources"),
            kpi_source_routes=result.get("kpi_source_routes"),
            is_kpi_response=result.get("is_kpi_response", False),
        )

    result = invoke_sql_agent(scoped_question, session_id=session_id, mode="text")
    reply = result.get("output", "I could not generate an answer.")
    save_text_result_context(session_id, question=question, reply=reply)
    return ChatResponse(reply=reply)


def _call_kpi_with_progress(
    question: str,
    scoped_user: str | None,
    progress_cb,
):
    """
    Support both legacy and new KPI function signatures.
    Legacy: handle_kpi_request_with_progress(question, progress_cb)
    New:    handle_kpi_request_with_progress(question, scoped_user, progress_cb)
    """
    try:
        return handle_kpi_request_with_progress(question, scoped_user, progress_cb)
    except TypeError as exc:
        message = str(exc)
        if "positional argument" not in message and "given" not in message:
            raise
        return handle_kpi_request_with_progress(question, progress_cb)


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    question = request.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        return _process_chat_request(question, request.session_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/admin/chat", response_model=ChatResponse)
def admin_chat_endpoint(request: ChatRequest):
    return chat_endpoint(request)


@app.post("/api/user/chat", response_model=ChatResponse)
def user_chat_endpoint(request: ChatRequest):
    try:
        user_api = _load_user_api_module()
        user_request = user_api.ChatRequest(
            message=request.message,
            session_id=request.session_id,
            user_filter_enabled=request.user_filter_enabled,
            user_name=request.user_name,
        )
        return user_api.chat_endpoint(user_request)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _build_chat_stream_response(
    *,
    question: str,
    session_id: str,
    scoped_user: str | None = None,
):
    scoped_session_id = _scoped_session_id(session_id, scoped_user)

    async def event_generator():
        try:
            token_delay_ms = int(os.getenv("STREAM_TOKEN_DELAY_MS", "8"))
        except Exception:
            token_delay_ms = 8
        token_delay = token_delay_ms / 1000.0

        try:
            yield _ndjson({"type": "status", "message": "Understanding your query..."})

            if is_followup_question(question):
                yield _ndjson({"type": "status", "message": "Reviewing previous context..."})

            active_question, followup_reply = _resolve_followup(question, scoped_session_id)
            if followup_reply:
                yield _ndjson({"type": "status", "message": "Preparing the answer..."})
                for chunk in _iter_word_tokens(followup_reply):
                    yield _ndjson({"type": "token", "message": chunk})
                    if token_delay:
                        await asyncio.sleep(token_delay)
                yield _ndjson({"type": "result", **ChatResponse(reply=followup_reply).model_dump()})
                yield _ndjson({"type": "done"})
                return

            scoped_question = _apply_user_scope(active_question, scoped_user)
            yield _ndjson({"type": "status", "message": "Classifying your request..."})
            intent = classify_intent(active_question)

            if is_comparison_plot_request(scoped_question):
                yield _ndjson({"type": "status", "message": "Calling comparison chart agent..."})
                queue: asyncio.Queue[str] = asyncio.Queue()
                loop = asyncio.get_running_loop()

                def progress_cb(message: str) -> None:
                    loop.call_soon_threadsafe(queue.put_nowait, message)

                task = asyncio.create_task(
                    asyncio.to_thread(
                        handle_comparison_plot_request,
                        scoped_question,
                        scoped_session_id,
                        progress_cb,
                    )
                )

                while not task.done():
                    try:
                        msg = await asyncio.wait_for(queue.get(), timeout=0.1)
                        yield _ndjson({"type": "status", "message": msg})
                    except asyncio.TimeoutError:
                        pass

                while not queue.empty():
                    yield _ndjson({"type": "status", "message": queue.get_nowait()})

                cmp_result = await task
                response = ChatResponse(**cmp_result)
            elif intent == "plot":
                yield _ndjson({"type": "status", "message": "Calling plotting agent..."})
                queue: asyncio.Queue[str] = asyncio.Queue()
                loop = asyncio.get_running_loop()

                def progress_cb(message: str) -> None:
                    loop.call_soon_threadsafe(queue.put_nowait, message)

                task = asyncio.create_task(
                    asyncio.to_thread(
                        handle_plot_request,
                        scoped_question,
                        scoped_session_id,
                        progress_cb,
                    )
                )

                while not task.done():
                    try:
                        msg = await asyncio.wait_for(queue.get(), timeout=0.1)
                        yield _ndjson({"type": "status", "message": msg})
                    except asyncio.TimeoutError:
                        pass

                while not queue.empty():
                    yield _ndjson({"type": "status", "message": queue.get_nowait()})

                plot_result = await task
                response = ChatResponse(**plot_result)
            elif intent == "kpi":
                yield _ndjson({"type": "status", "message": "Calling KPI discovery agent..."})
                queue = asyncio.Queue()
                loop = asyncio.get_running_loop()

                def progress_cb(message: str) -> None:
                    loop.call_soon_threadsafe(queue.put_nowait, message)

                task = asyncio.create_task(
                    asyncio.to_thread(
                        _call_kpi_with_progress,
                        scoped_question,
                        scoped_user,
                        progress_cb,
                    )
                )

                while not task.done():
                    try:
                        msg = await asyncio.wait_for(queue.get(), timeout=0.1)
                        yield _ndjson({"type": "status", "message": msg})
                    except asyncio.TimeoutError:
                        pass

                while not queue.empty():
                    yield _ndjson({"type": "status", "message": queue.get_nowait()})

                kpi_result = await task
                response = ChatResponse(**kpi_result)
            else:
                yield _ndjson({"type": "status", "message": "Calling SQL agent..."})
                reply = ""
                async for chunk in stream_sql_agent_events(
                    scoped_question,
                    session_id=scoped_session_id,
                    mode="text",
                ):
                    if chunk.get("type") == "status":
                        yield _ndjson({"type": "status", "message": chunk.get("message", "")})
                    elif chunk.get("type") == "token":
                        for piece in _iter_word_tokens(chunk.get("message", "")):
                            yield _ndjson({"type": "token", "message": piece})
                            if token_delay:
                                await asyncio.sleep(token_delay)
                    elif chunk.get("type") == "final":
                        reply = chunk.get("reply", "")

                save_text_result_context(
                    scoped_session_id,
                    question=question,
                    reply=reply,
                )
                response = ChatResponse(reply=reply)

            if response.reply and (intent in {"plot", "kpi"} or is_comparison_plot_request(scoped_question)):
                for chunk in _iter_word_tokens(response.reply):
                    yield _ndjson({"type": "token", "message": chunk})
                    if token_delay:
                        await asyncio.sleep(token_delay)

            yield _ndjson({"type": "result", **response.model_dump()})
            yield _ndjson({"type": "done"})
        except Exception as exc:
            yield _ndjson({"type": "error", "message": str(exc)})
            yield _ndjson({"type": "done"})

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    question = request.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return _build_chat_stream_response(
        question=question,
        session_id=request.session_id,
        scoped_user=None,
    )


@app.post("/api/admin/chat/stream")
async def admin_chat_stream_endpoint(request: ChatRequest):
    return await chat_stream_endpoint(request)


@app.post("/api/user/chat/stream")
async def user_chat_stream_endpoint(request: ChatRequest):
    try:
        user_api = _load_user_api_module()
        user_request = user_api.ChatRequest(
            message=request.message,
            session_id=request.session_id,
            user_filter_enabled=request.user_filter_enabled,
            user_name=request.user_name,
        )
        return await user_api.chat_stream_endpoint(user_request)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/user/users")
def list_valid_users():
    try:
        user_api = _load_user_api_module()
        return user_api.list_valid_users()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/admin/health")
def admin_healthcheck():
    return {
        "status": "ok",
        "mode": "admin",
        "supports_user_filter": False,
    }


@app.get("/api/user/health")
def user_healthcheck():
    try:
        user_api = _load_user_api_module()
        return user_api.healthcheck()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
