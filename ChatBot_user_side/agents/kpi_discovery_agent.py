"""
KPI Discovery Agent - Web search powered KPI discovery tool.

This agent:
1. Searches the web for relevant KPIs based on user context
2. Provides reasoning behind each KPI suggestion
3. Returns LaTeX-formatted formulas for mathematical expressions
4. Fetches definitions from reliable sources
"""

import os
import re
import json
from typing import Optional, Callable
from dataclasses import dataclass

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient
from kpi_injection import retrieve_kpi_context
from env_loader import load_project_env

load_project_env()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    temperature=0.3,
)

tavily_client = None
if TAVILY_API_KEY:
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Tavily client: {e}")


@dataclass
class KPIResult:
    """Represents a single KPI suggestion."""
    name: str
    description: str
    formula_latex: str
    formula_plain: str
    reasoning: str
    category: str
    data_requirements: list[str]
    source: str
    sources: list[str]


KPI_FALLBACK_GUIDANCE = """
## FALLBACK KPI THINKING GUIDE

Use this guide only if retrieved KPI framework context and web context are weak.
Do not copy from it mechanically.

- Productivity themes: output rate, publish rate, user productivity
- Efficiency themes: duration utilization, time per asset, workflow conversion
- Growth themes: overall output growth where supported by the available data
- User themes: individual productivity, publishing success, scoped user efficiency
- Channel themes: channel-level output and conversion within the user-side schema

Never introduce unsupported fields such as platform metrics, monthly trend metrics,
revenue, cost, ROI, or detailed video-level quality measures.
"""

FRAMMER_SCHEMA_FIELDS = [
    "metric_focus",
    "time_period",
    "channel_name",
    "user_name",
    "content_category",
    "uploaded_count",
    "created_count",
    "published_count",
    "uploaded_duration_seconds",
    "created_duration_seconds",
    "published_duration_seconds",
]

SUPPORTED_DERIVED_REQUIREMENTS = {
    "upload_to_publish_ratio",
    "create_to_upload_ratio",
    "publish_to_created_ratio",
    "user_publish_success_rate",
    "duration_utilization_rate",
    "video_output_rate",
    "avg_uploaded_duration_seconds",
    "avg_created_duration_seconds",
    "avg_published_duration_seconds",
}

UNSUPPORTED_REQUIREMENT_KEYWORDS = {
    "quality_score",
    "qualityscore",
    "hours_worked",
    "hour_worked",
    "total_hours",
    "salary",
    "revenue",
    "roi",
    "profit",
    "cost",
    "customer",
    "order",
}


KPI_DISCOVERY_SYSTEM = """You are an expert KPI (Key Performance Indicator) analyst and consultant.

Your task is to suggest relevant KPIs based on the user's question, data context, and business needs.

## CONTEXT
You are working with the user-side Frammer analytics dataset.
Available data is limited to:
- user-level and channel+user level aggregates
- uploaded_count, created_count, published_count
- uploaded_duration_seconds, created_duration_seconds, published_duration_seconds
- metric_focus values: 'By User' and 'By Channel and User'
- time_period is mostly 'Overall' in this dataset

## AVAILABLE DATA DIMENSIONS
- Users: Individual content creators
- Channels: Named A, B, C, D, E, etc.
- Metrics: uploaded_count, created_count, published_count, *_duration_seconds

## AVAILABLE SCHEMA FIELDS (STRICT)
{schema_fields}

## FALLBACK KPI THINKING GUIDE
{fallback_guidance}

## SELECTED USER SCOPE
{selected_user_instruction}

## SOURCE PRIORITY
1. Trusted KPI framework RAG excerpts supplied in the user message
2. Real-time web context supplied in the user message
3. This fallback thinking guide only if the retrieved evidence is weak

If retrieved context exists, do not default to canned KPI bundles. Use retrieved evidence first.

## YOUR RESPONSE FORMAT
Return a JSON array of KPI objects. Each KPI must have:
{{
  "name": "KPI Name",
  "description": "Clear explanation of what this KPI measures",
  "formula_latex": "LaTeX formula using $...$ delimiters",
  "formula_plain": "Plain text version of the formula",
  "reasoning": "Why this KPI is relevant to the user's question (2-3 sentences)",
  "category": "Category (Productivity/Efficiency/Growth/User)",
  "data_requirements": ["list", "of", "required", "data", "fields"],
  "source": "One of: Framework, Web expansion, Hybrid",
  "sources": ["https://source-link-1", "https://source-link-2"]
}}

## RULES
1. Suggest 3-5 highly relevant KPIs based on the user's question.
2. Always include the LaTeX formula with proper delimiters ($...$).
3. Provide clear, actionable reasoning for each KPI.
4. Consider only the available user-side data when suggesting KPIs.
5. If the user asks for unsupported concepts, say they are unavailable instead of inventing substitutions.
6. Ensure formulas are mathematically correct and use standard notation.
7. Return ONLY valid JSON - no markdown fences, no explanation outside the JSON.
8. KPI data_requirements must be derivable from AVAILABLE SCHEMA FIELDS only.
9. Derived KPIs are allowed, but data_requirements must list source schema fields (not imaginary fields).
10. Never use unsupported fields like quality_score, hours_worked, revenue, ROI, cost, customers, orders.
11. When web context is available, include 1-3 source URLs in `sources`.
12. If selected user scope is active, every KPI must apply only to that selected user. Do not include team-level or all-user comparisons.
13. Treat KPI framework RAG context as the primary trusted source when available.
14. Use web context to expand or refresh KPI ideas beyond the framework, but never ignore the available schema.
15. Prefer KPIs that best match the user's focus area; do not return the same generic KPI bundle unless it is genuinely the best fit.
16. If framework excerpts exist, most returned KPIs should come from the framework; web-derived KPIs are supplements, not replacements.
17. When both framework and web context exist, target a mix like 2-4 framework or hybrid KPIs plus at most 1-2 web expansion KPIs.
18. When web context introduces a relevant KPI idea not present in the framework excerpts, you may include 1-2 such newer web-derived KPIs if they remain schema-compatible.

## LATEX FORMATTING RULES
- Use $...$ for inline formulas.
- Use \\frac{{num}}{{denom}} for fractions.
- Use \\times for multiplication.
- Use \\sum for summation.
- Use \\text{{...}} for text within formulas.
- Use subscripts like x_i and superscripts like x^2.
- Use \\left( and \\right) for auto-sizing parentheses.
"""


def _normalize_requirement(req: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", req.strip().lower()).strip("_")


def _is_supported_requirement(req: str) -> bool:
    req_norm = _normalize_requirement(req)
    if not req_norm:
        return False

    if any(keyword in req_norm for keyword in UNSUPPORTED_REQUIREMENT_KEYWORDS):
        return False

    if req_norm in FRAMMER_SCHEMA_FIELDS:
        return True

    if req_norm in SUPPORTED_DERIVED_REQUIREMENTS:
        return True

    # Friendly aliases that still map to schema-supported concepts
    alias_tokens = (
        "uploaded_count",
        "created_count",
        "published_count",
        "uploaded_duration_seconds",
        "created_duration_seconds",
        "published_duration_seconds",
        "time_period",
        "user_name",
        "channel_name",
        "content_category",
    )
    return any(token in req_norm for token in alias_tokens)


def _filter_kpis_by_schema(kpis: list[dict]) -> list[dict]:
    filtered: list[dict] = []
    for kpi in kpis:
        reqs = kpi.get("data_requirements", [])
        if not isinstance(reqs, list):
            reqs = []

        supported_reqs = [req for req in reqs if isinstance(req, str) and _is_supported_requirement(req)]

        # Keep only fully supported KPIs so every required ingredient is calculable.
        if reqs and len(supported_reqs) == len(reqs):
            kpi["data_requirements"] = supported_reqs
            filtered.append(kpi)

    return filtered


def _normalize_source_urls(urls: list[str]) -> list[str]:
    unique: list[str] = []
    for raw in urls:
        if not isinstance(raw, str):
            continue
        url = raw.strip()
        if not url.startswith(("http://", "https://")):
            continue
        if url not in unique:
            unique.append(url)
    return unique


def _normalize_source_refs(values: list[str]) -> list[str]:
    unique: list[str] = []
    for raw in values:
        if not isinstance(raw, str):
            continue
        value = " ".join(raw.split()).strip()
        if not value:
            continue
        if value not in unique:
            unique.append(value)
    return unique


def _build_source_bundle(
    rag_refs: list[str],
    web_urls: list[str],
    max_items: int = 4,
) -> list[str]:
    ordered: list[str] = []
    for value in _normalize_source_urls(web_urls) + _normalize_source_refs(rag_refs):
        if value not in ordered:
            ordered.append(value)
    return ordered[:max_items]


def _normalize_source_label(value: str) -> str:
    label = (value or "").strip().lower()
    if "web" in label:
        return "web"
    if "hybrid" in label or ("framework" in label and "web" in label):
        return "hybrid"
    if "framework" in label or "pdf" in label or "rag" in label or "vector" in label:
        return "framework"
    return "framework"


def _attach_kpi_sources(
    kpis: list[dict],
    rag_refs: list[str],
    web_urls: list[str],
) -> list[dict]:
    for kpi in kpis:
        source_kind = _normalize_source_label(str(kpi.get("source", "")))
        if source_kind == "web":
            kpi["source"] = "Web expansion"
            kpi["sources"] = _build_source_bundle([], web_urls, max_items=4)
        elif source_kind == "hybrid":
            kpi["source"] = "Hybrid"
            kpi["sources"] = _build_source_bundle(rag_refs, web_urls, max_items=4)
        else:
            kpi["source"] = "Framework"
            kpi["sources"] = _build_source_bundle(rag_refs, [], max_items=4)
    return kpis


def _rebalance_kpis(
    kpis: list[dict],
    rag_refs: list[str],
    web_urls: list[str],
) -> list[dict]:
    if not kpis:
        return []

    framework_like: list[dict] = []
    web_like: list[dict] = []
    for kpi in kpis:
        source_kind = _normalize_source_label(str(kpi.get("source", "")))
        if source_kind == "web":
            web_like.append(kpi)
        else:
            framework_like.append(kpi)

    if rag_refs:
        selected = framework_like[:4]
        if web_urls:
            selected.extend(web_like[:2])
        elif len(selected) < 5:
            selected.extend(framework_like[4:5])
        return selected[:5]

    if web_urls:
        return (framework_like + web_like)[:5]

    return kpis[:5]


def _extract_global_sources_from_kpis(kpis: list[dict]) -> list[str]:
    urls: list[str] = []
    for kpi in kpis:
        sources = kpi.get("sources", [])
        if isinstance(sources, str):
            sources = [sources]
        if isinstance(sources, list):
            for src in sources:
                if isinstance(src, str):
                    urls.append(src)
    return _normalize_source_refs(urls)


def _attach_source_routes(kpis: list[dict]) -> tuple[list[dict], list[str]]:
    """Attach per-KPI source-route metadata for UI/debug display."""
    route_lines: list[str] = []

    for idx, kpi in enumerate(kpis):
        name = kpi.get("name", f"KPI {idx + 1}")
        source_kind = _normalize_source_label(str(kpi.get("source", "")))
        sources = kpi.get("sources", [])
        first_source = str(sources[0]) if isinstance(sources, list) and sources else ""

        if source_kind == "web":
            kpi["source_route"] = "web_search"
            kpi["source_detail"] = first_source or "Web search context"
            route_lines.append(f"{name} -> Web Search")
        elif source_kind == "hybrid":
            kpi["source_route"] = "hybrid"
            kpi["source_detail"] = first_source or "Framework + Web"
            route_lines.append(f"{name} -> Hybrid")
        else:
            kpi["source_route"] = "vector_db"
            kpi["source_detail"] = first_source or "KPI PDF Vector DB"
            route_lines.append(f"{name} -> Vector DB")

    return kpis, route_lines


def discover_kpis(
    question: str,
    selected_user: Optional[str] = None,
    context: Optional[str] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Discover relevant KPIs based on user question and context.

    Args:
        question: User's natural language question about KPIs
        selected_user: Optional selected user scope for user-filtered sessions
        context: Optional additional context about their data/needs

    Returns:
        Dictionary with 'kpis' list and 'summary' text
    """

    def _emit(message: str) -> None:
        if progress_callback:
            try:
                progress_callback(message)
            except Exception:
                pass

    _emit("Calling KPI discovery agent...")
    if selected_user:
        selected_user_instruction = (
            f"Selected user scope is ACTIVE for '{selected_user}'. "
            "Every KPI must be framed only for this user. "
            "Do not suggest KPIs that require comparing with other users, "
            "team averages, or all-user totals."
        )
    else:
        selected_user_instruction = (
            "No selected user scope is active. Use normal user-side dataset scope."
        )

    system_prompt = KPI_DISCOVERY_SYSTEM.format(
        schema_fields=", ".join(FRAMMER_SCHEMA_FIELDS),
        fallback_guidance=KPI_FALLBACK_GUIDANCE,
        selected_user_instruction=selected_user_instruction,
    )

    user_prompt = f"USER QUESTION: {question}"
    if selected_user:
        user_prompt += (
            f"\n\nSELECTED USER (STRICT): {selected_user}\n"
            "Treat 'my/me' as this user only and avoid cross-user KPI suggestions."
        )
    if context:
        user_prompt += f"\n\nADDITIONAL CONTEXT: {context}"
        
    web_source_urls: list[str] = []
    vector_source_refs: list[str] = []
    source_route = "model_fallback"

    _emit("Checking KPI vector database...")
    try:
        vector_top_k = int(os.getenv("KPI_VECTOR_TOP_K", "5"))
    except Exception:
        vector_top_k = 5
    try:
        vector_min_score = float(os.getenv("KPI_VECTOR_MIN_SCORE", "0.33"))
    except Exception:
        vector_min_score = 0.33

    vector_result = retrieve_kpi_context(
        query=question,
        top_k=vector_top_k,
        min_score=vector_min_score,
        progress_callback=progress_callback,
    )

    if vector_result.get("success") and vector_result.get("hits"):
        vector_source_refs = list(vector_result.get("source_refs", []))
        _emit(
            f"Using KPI vector DB context ({len(vector_result.get('hits', []))} matched chunks)."
        )
        user_prompt += (
            "\n\nKPI KNOWLEDGE BASE CONTEXT (VECTOR DB, prioritize this):\n"
            + vector_result.get("context_for_prompt", "")
        )
        source_route = "vector_db"
    else:
        if not vector_result.get("success"):
            _emit("KPI vector DB unavailable. Continuing without framework context.")
        else:
            _emit("No strong KPI match in vector DB. Looking for web context.")

    if tavily_client:
        try:
            _emit("Searching web for KPI standards...")
            print(f"Searching Tavily for: {question}")
            search_result = tavily_client.search(
                query=f"Industry standard KPIs and mathematical formulas for: {question}",
                search_depth="advanced"
            )
            web_context = "\n".join(
                [f"- {result['content']}" for result in search_result.get('results', [])]
            )
            web_source_urls = [
                item.get("url", "")
                for item in search_result.get("results", [])
                if isinstance(item, dict)
            ]
            if web_context:
                _emit("Web context retrieved.")
                user_prompt += (
                    "\n\nREAL-TIME WEB CONTEXT (secondary to vector DB; use for newer KPI ideas):\n"
                    f"{web_context}"
                )
                if source_route == "model_fallback":
                    source_route = "web_search"
                elif source_route == "vector_db":
                    source_route = "hybrid"
        except Exception as e:
            print(f"Tavily search failed: {e}")
            _emit("Web search unavailable. Continuing with available knowledge.")

    if vector_source_refs:
        user_prompt += (
            "\n\nGROUNDING PRIORITY:\n"
            "- First prefer KPI definitions and formulas supported by the KPI framework excerpts.\n"
            "- Then use web context to add newer or broader industry KPIs only when they still fit the user-side schema.\n"
            "- Most KPIs should come from the framework when framework excerpts are available.\n"
            "- Include at most 1-2 web expansion KPIs when the web adds something useful.\n"
        )
    elif web_source_urls:
        user_prompt += (
            "\n\nWEB EXPANSION PRIORITY:\n"
            "- No strong framework excerpt was retrieved, so rely on the web context for grounded KPI ideas.\n"
            "- Include only schema-compatible KPIs and prefer the user-side dataset constraints.\n"
        )

    if web_source_urls:
        user_prompt += (
            "\n\nWEB SOURCE REQUIREMENT:\n"
            "- At least one returned source should be a real web URL from the provided web context when available.\n"
            "- Mark web-only KPI entries with source='Web expansion' and mixed ones with source='Hybrid'.\n"
        )

    user_prompt += "\n\nSuggest relevant KPIs. Return ONLY the JSON array."

    try:
        _emit("Generating KPI suggestions...")
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])

        raw_content = response.content.strip()

        # Clean up response - remove markdown fences if present
        raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content, flags=re.MULTILINE)
        raw_content = re.sub(r"\s*```$", "", raw_content, flags=re.MULTILINE)

        # Parse JSON
        kpis = json.loads(raw_content)

        if not isinstance(kpis, list):
            kpis = [kpis]

        _emit("Validating KPI fields against schema...")
        # Enforce schema-aware KPI requirements (allowing approved derived concepts).
        kpis = _filter_kpis_by_schema(kpis)
        kpis = _rebalance_kpis(kpis, vector_source_refs, web_source_urls)
        kpis = _attach_kpi_sources(kpis, vector_source_refs, web_source_urls)
        kpis, kpi_source_routes = _attach_source_routes(kpis)
        if kpi_source_routes:
            preview = " | ".join(kpi_source_routes[:3])
            suffix = " | ..." if len(kpi_source_routes) > 3 else ""
            _emit(f"KPI source routes: {preview}{suffix}")

        _emit("Preparing KPI summary...")
        # Generate summary
        summary = _generate_summary(question, kpis)

        return {
            "success": True,
            "kpis": kpis,
            "summary": summary,
            "query": question,
            "sources": _build_source_bundle(vector_source_refs, web_source_urls, max_items=6),
            "kpi_source_routes": kpi_source_routes,
            "source_route": source_route,
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse KPI suggestions: {e}",
            "raw_response": raw_content if 'raw_content' in locals() else None,
            "kpis": [],
            "summary": "I encountered an error while generating KPI suggestions.",
            "sources": [],
            "kpi_source_routes": [],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "kpis": [],
            "summary": f"An error occurred: {e}",
            "sources": [],
            "kpi_source_routes": [],
        }


def _generate_summary(question: str, kpis: list[dict]) -> str:
    """Generate a natural language summary of the KPI suggestions."""

    if not kpis:
        return "I couldn't find relevant KPIs for your query."

    summary_prompt = f"""Based on the question "{question}", I found {len(kpis)} relevant KPIs:

{chr(10).join(f"- **{kpi.get('name', 'Unknown')}**: {kpi.get('description', '')[:100]}..." for kpi in kpis[:5])}

Write a 2-3 sentence executive summary explaining why these KPIs are relevant and how they can help measure performance. Be concise and professional. Do not use markdown formatting."""

    try:
        response = llm.invoke([
            SystemMessage(content="You are a concise business analyst. Write brief, actionable summaries."),
            HumanMessage(content=summary_prompt),
        ])
        return response.content.strip()
    except Exception:
        return f"Here are {len(kpis)} relevant KPIs for measuring {question.lower()}."


def search_web_for_kpi(kpi_name: str) -> dict:
    """
    Search for additional information about a specific KPI.
    Uses Tavily API for actual web search if configured,
    otherwise falls back to LLM knowledge.
    """

    system_message = "You are a KPI expert with knowledge of industry standards and best practices."
    web_context = ""

    if tavily_client:
        try:
            print(f"Searching Tavily for specific KPI: {kpi_name}")
            search_result = tavily_client.search(
                query=f"Define the KPI {kpi_name}, including the mathematical formula and industry benchmarks",
                search_depth="advanced"
            )
            web_context = "\n".join([f"- {result['content']}" for result in search_result.get('results', [])])
        except Exception as e:
            print(f"Tavily search failed for {kpi_name}: {e}")

    search_prompt = f"""Provide detailed information about the KPI: "{kpi_name}"

Include:
1. Official definition from industry standards (cite source if known)
2. The mathematical formula in LaTeX format
3. How to interpret the results (what's good/bad)
4. Common variations or related KPIs
5. Best practices for using this KPI"""

    if web_context:
        search_prompt += f"\n\nUse this REAL-TIME WEB CONTEXT to ground your detailed response (cite sources from here):\n{web_context}"

    search_prompt += """\n\nFormat as JSON:
{{
    "name": "KPI Name",
    "definition": "Full definition",
    "formula_latex": "$formula$",
    "interpretation": "How to read the results",
    "benchmarks": "Industry benchmarks if applicable",
    "variations": ["related KPI 1", "related KPI 2"],
    "best_practices": ["practice 1", "practice 2"],
    "sources": ["source 1", "source 2"]
}}

Return ONLY valid JSON."""

    try:
        response = llm.invoke([
            SystemMessage(content=system_message),
            HumanMessage(content=search_prompt),
        ])

        raw = response.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)

        return json.loads(raw)
    except Exception as e:
        return {
            "name": kpi_name,
            "error": str(e),
            "definition": "Information not available",
        }


def get_kpis_for_data_context(data_summary: dict) -> dict:
    """
    Suggest KPIs based on available data structure.

    Args:
        data_summary: Dictionary describing available data fields

    Returns:
        KPI suggestions tailored to the data
    """

    context = f"""
Available data fields:
- Metrics: {', '.join(data_summary.get('metrics', []))}
- Dimensions: {', '.join(data_summary.get('dimensions', []))}
- Time range: {data_summary.get('time_range', 'Unknown')}
"""

    return discover_kpis(
        "What KPIs can I calculate with my available data?",
        context=context
    )


def handle_kpi_request(question: str, selected_user: Optional[str] = None) -> dict:
    """
    Main handler for KPI discovery requests.
    Called by the API when intent is classified as 'kpi'.

    Returns a dictionary with:
    - reply: Text summary for the user
    - kpis: List of KPI objects with LaTeX formulas
    - is_kpi_response: Flag for frontend to enable LaTeX rendering
    """

    result = discover_kpis(question, selected_user=selected_user)

    if not result["success"]:
        return {
            "reply": result["summary"],
            "kpis": [],
            "is_kpi_response": True,
            "kpi_sources": [],
            "kpi_source_routes": [],
        }

    # Format the reply with KPI details
    reply_parts = [result["summary"], ""]

    for i, kpi in enumerate(result["kpis"], 1):
        reply_parts.append(f"**{i}. {kpi.get('name', 'Unknown KPI')}**")
        reply_parts.append(f"{kpi.get('description', '')}")
        reply_parts.append(f"*Formula:* {kpi.get('formula_latex', 'N/A')}")
        reply_parts.append(f"*Why relevant:* {kpi.get('reasoning', '')}")
        reply_parts.append("")

    return {
        "reply": "\n".join(reply_parts),
        "kpis": result["kpis"],
        "is_kpi_response": True,
        "kpi_sources": result.get("sources", []),
        "kpi_source_routes": result.get("kpi_source_routes", []),
    }


def handle_kpi_request_with_progress(
    question: str,
    selected_user: Optional[str] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """KPI handler with optional live progress updates for streaming UIs."""
    result = discover_kpis(
        question,
        selected_user=selected_user,
        progress_callback=progress_callback,
    )

    if not result["success"]:
        return {
            "reply": result["summary"],
            "kpis": [],
            "is_kpi_response": True,
            "kpi_sources": [],
            "kpi_source_routes": [],
        }

    reply_parts = [result["summary"], ""]
    for i, kpi in enumerate(result["kpis"], 1):
        reply_parts.append(f"**{i}. {kpi.get('name', 'Unknown KPI')}**")
        reply_parts.append(f"{kpi.get('description', '')}")
        reply_parts.append(f"*Formula:* {kpi.get('formula_latex', 'N/A')}")
        reply_parts.append(f"*Why relevant:* {kpi.get('reasoning', '')}")
        reply_parts.append("")

    return {
        "reply": "\n".join(reply_parts),
        "kpis": result["kpis"],
        "is_kpi_response": True,
        "kpi_sources": result.get("sources", []),
        "kpi_source_routes": result.get("kpi_source_routes", []),
    }


# Example usage and testing
if __name__ == "__main__":
    # Test the KPI discovery
    test_questions = [
        "What KPIs should I track for measuring video production efficiency?",
        "How can I measure user productivity in content creation?",
        "What metrics help analyze platform performance?",
        "Suggest KPIs for monthly growth tracking",
    ]

    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {q}")
        print('='*60)

        result = handle_kpi_request(q)
        print(f"\nReply:\n{result['reply']}")
        print(f"\nKPIs found: {len(result['kpis'])}")

