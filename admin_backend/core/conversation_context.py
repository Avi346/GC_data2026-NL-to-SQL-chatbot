import re
from typing import Any


_last_result_store: dict[str, dict[str, Any]] = {}

FOLLOWUP_PATTERNS = (
    r"\bthe above\b",
    r"\babove\b",
    r"\bthis\b",
    r"\bthat\b",
    r"\btell me more\b",
    r"\bexplain (it|this|that|the above)\b",
    r"\bwhat does (this|that|the above)\b",
    r"\binsight about (this|that|the above)\b",
    r"\bwhat does (this|that|the above) plot\b",
    r"\bwhat does (this|that|the above) chart\b",
)

PLOT_REQUEST_PATTERNS = (
    r"\bplot\b",
    r"\bchart\b",
    r"\bgraph\b",
    r"\bbar plot\b",
    r"\bbar chart\b",
    r"\bline chart\b",
    r"\bhistogram\b",
    r"\bheatmap\b",
    r"\bscatter\b",
    r"\bpie chart\b",
    r"\bvisuali[sz]e\b",
)

PLOT_EXPLANATION_PATTERNS = (
    r"\btell me more about .*plot\b",
    r"\btell me more about .*chart\b",
    r"\bexplain .*plot\b",
    r"\bexplain .*chart\b",
    r"\bwhat does .*plot\b",
    r"\bwhat does .*chart\b",
    r"\binsight about .*plot\b",
    r"\binsight about .*chart\b",
    r"\bdescribe .*plot\b",
    r"\bdescribe .*chart\b",
)


def is_followup_question(question: str) -> bool:
    lowered = question.lower().strip()
    return any(re.search(pattern, lowered) for pattern in FOLLOWUP_PATTERNS)


def is_plot_like_question(question: str) -> bool:
    lowered = question.lower().strip()
    return any(re.search(pattern, lowered) for pattern in PLOT_REQUEST_PATTERNS)


def is_plot_explanation_question(question: str) -> bool:
    lowered = question.lower().strip()
    return any(re.search(pattern, lowered) for pattern in PLOT_EXPLANATION_PATTERNS)


def save_last_result(session_id: str, payload: dict[str, Any]) -> None:
    payload = dict(payload)
    payload.setdefault("source_question", payload.get("question"))
    payload.setdefault("source_reply", payload.get("reply"))
    payload.setdefault("source_data_sample", payload.get("data_sample"))
    payload.setdefault("source_data_columns", payload.get("data_columns"))
    payload.setdefault("source_full_data", payload.get("full_data"))
    payload.setdefault("source_chart_facts", payload.get("chart_facts"))
    _last_result_store[session_id] = payload


def get_last_result(session_id: str) -> dict[str, Any] | None:
    return _last_result_store.get(session_id)


def update_last_result(session_id: str, **updates: Any) -> dict[str, Any] | None:
    current = _last_result_store.get(session_id)
    if not current:
        return None
    current.setdefault("source_question", current.get("question"))
    current.setdefault("source_reply", current.get("reply"))
    current.setdefault("source_data_sample", current.get("data_sample"))
    current.setdefault("source_data_columns", current.get("data_columns"))
    current.setdefault("source_full_data", current.get("full_data"))
    current.setdefault("source_chart_facts", current.get("chart_facts"))
    current.update(updates)
    _last_result_store[session_id] = current
    return current
