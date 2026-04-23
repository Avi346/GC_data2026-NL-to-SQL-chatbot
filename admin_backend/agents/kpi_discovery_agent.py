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

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient

from kpi_injection import connect_qdrant, get_embedder, search_pdf_chunks

load_dotenv()

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


_qdrant_client = None
_qdrant_embedder = None


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
- Growth themes: month-over-month growth, trend velocity
- Platform themes: platform mix, distribution, coverage
- Content themes: content type mix, content type efficiency
- User themes: user contribution, publishing success, channel/user comparisons

For non-video domains, prefer generic measurable operational or growth KPIs only when they
can still be expressed using the available schema. Never introduce unsupported business fields.
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
    "platform_facebook_count",
    "platform_instagram_count",
    "platform_linkedin_count",
    "platform_reels_count",
    "platform_shorts_count",
    "platform_x_count",
    "platform_youtube_count",
    "platform_threads_count",
    "platform_facebook_duration_seconds",
    "platform_instagram_duration_seconds",
    "platform_linkedin_duration_seconds",
    "platform_reels_duration_seconds",
    "platform_shorts_duration_seconds",
    "platform_x_duration_seconds",
    "platform_youtube_duration_seconds",
    "platform_threads_duration_seconds",
]

SUPPORTED_DERIVED_REQUIREMENTS = {
    "upload_to_publish_ratio",
    "user_publish_success_rate",
    "duration_utilization_rate",
    "month_over_month_growth_rate",
    "platform_distribution_index",
    "cross_platform_coverage",
    "content_mix_ratio",
    "content_type_efficiency",
    "video_output_rate",
    "user_productivity_score",
    "channel_efficiency_score",
    "content_velocity_trend",
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
You are working with a video production analytics platform called Frammer that tracks:
- Video uploads, creations, and publications
- User productivity metrics
- Channel performance
- Platform distribution (YouTube, Instagram, Facebook, LinkedIn, Reels, Shorts, X, Threads)
- Content types (interview, news bulletin, speech, debate, podcast, drama, etc.)
- Monthly trends and time-series data
- Duration metrics (in seconds)

## AVAILABLE DATA DIMENSIONS
- Users: Individual content creators
- Channels: Named A, B, C, D, E, etc.
- Platforms: YouTube, Instagram, Facebook, LinkedIn, Reels, Shorts, X, Threads
- Content Types: interview, news bulletin, speech, debate, podcast, drama, sports show, etc.
- Time Periods: Monthly data from March 2025 to February 2026
- Metrics: uploaded_count, created_count, published_count, *_duration_seconds

## AVAILABLE SCHEMA FIELDS (STRICT)
{schema_fields}

## FALLBACK KPI THINKING GUIDE
{fallback_guidance}

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
  "category": "Category (Productivity/Efficiency/Growth/Quality/Platform/User)",
  "data_requirements": ["list", "of", "required", "data", "fields"],
  "source": "One of: Framework, Web expansion, Hybrid",
  "sources": ["https://source-link-1", "https://source-link-2"]
}}

## RULES
1. Suggest 3-5 highly relevant KPIs based on the user's question
2. Always include the LaTeX formula with proper delimiters ($...$)
3. Provide clear, actionable reasoning for each KPI
4. Consider the available data when suggesting KPIs
5. If the user asks about something outside video production, suggest general business KPIs
6. Ensure formulas are mathematically correct and use standard notation
7. Return ONLY valid JSON - no markdown fences, no explanation outside the JSON
8. KPI data_requirements must be derivable from AVAILABLE SCHEMA FIELDS only
9. Derived KPIs are allowed, but data_requirements must list source schema fields (not imaginary fields)
10. Never use unsupported fields like quality_score, hours_worked, revenue, ROI, cost, customers, orders
11. When web context is available, include 1-3 source URLs in `sources`
12. Treat KPI framework RAG context as the primary trusted source when available
13. Use web context only to expand or refresh KPI ideas beyond the framework, not to ignore the available schema
14. Prefer KPIs that best match the user's focus area; do not return the same generic KPI bundle unless it is genuinely the best fit
15. If two candidate KPIs are very similar, keep the one that is more directly calculable from the available schema
16. Do not reuse fallback KPI patterns when retrieved evidence suggests a more specific KPI set
17. Every KPI must be justified by the user's focus plus the available schema, not just general KPI knowledge
18. When web context introduces a relevant KPI idea not present in the framework excerpts, you may include 1-2 such newer web-derived KPIs if they remain schema-compatible
19. If framework excerpts exist, most returned KPIs should come from the framework; web-derived KPIs are supplements, not replacements
20. When both framework and web context exist, target a mix like 2-4 framework or hybrid KPIs plus at most 1-2 web expansion KPIs

## LATEX FORMATTING RULES
- Use $...$ for inline formulas
- Use \\frac{{num}}{{denom}} for fractions
- Use \\times for multiplication
- Use \\sum for summation
- Use \\text{{...}} for text within formulas
- Use subscripts like x_i and superscripts like x^2
- Use \\left( and \\right) for auto-sizing parentheses
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
        "platform_",
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
    if "framework" in label or "pdf" in label or "rag" in label:
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


def _get_kpi_rag_resources():
    global _qdrant_client, _qdrant_embedder
    if _qdrant_client is None:
        _qdrant_client = connect_qdrant()
    if _qdrant_embedder is None:
        _qdrant_embedder = get_embedder()
    return _qdrant_client, _qdrant_embedder


def _retrieve_kpi_rag_context(
    question: str,
    context: Optional[str] = None,
    top_k: int = 5,
) -> tuple[str, list[str], list[dict]]:
    query = question.strip()
    if context:
        query = f"{question}\n\nContext:\n{context.strip()}"

    client, embedder = _get_kpi_rag_resources()
    matches = search_pdf_chunks(client, embedder, query=query, top_k=top_k)

    context_lines: list[str] = []
    references: list[str] = []
    for idx, match in enumerate(matches, start=1):
        text = " ".join(str(match.get("text", "")).split())
        if not text:
            continue
        page = match.get("page", "Unknown")
        score = match.get("score", 0)
        context_lines.append(
            f"[RAG {idx}] page={page} score={score:.3f} text={text}"
        )
        references.append(f"User KPI Framework Premium (page {page})")

    unique_refs: list[str] = []
    for ref in references:
        if ref not in unique_refs:
            unique_refs.append(ref)

    return "\n".join(context_lines), unique_refs, matches


def _retrieve_web_kpi_context(question: str, context: Optional[str] = None) -> tuple[str, list[str]]:
    if not tavily_client:
        return "", []

    query = (
        "Industry standard KPIs, formulas, definitions, and benchmarking guidance for: "
        f"{question}"
    )
    if context:
        query += f". Additional business context: {context}"

    search_result = tavily_client.search(query=query, search_depth="advanced")
    snippets: list[str] = []
    urls: list[str] = []
    for item in search_result.get("results", []):
        if not isinstance(item, dict):
            continue
        content = " ".join(str(item.get("content", "")).split())
        title = " ".join(str(item.get("title", "")).split())
        url = str(item.get("url", "")).strip()
        if content:
            prefix = f"{title}: " if title else ""
            snippets.append(f"- {prefix}{content}")
        if url:
            urls.append(url)

    return "\n".join(snippets), _normalize_source_urls(urls)


def _question_keywords(question: str, context: Optional[str] = None) -> list[str]:
    text = f"{question} {context or ''}".lower()
    keywords: list[str] = []
    candidate_terms = (
        "efficiency",
        "productivity",
        "growth",
        "monthly",
        "trend",
        "channel",
        "platform",
        "user",
        "publish",
        "upload",
        "duration",
        "content type",
        "mix",
        "coverage",
        "velocity",
        "comparison",
    )
    for term in candidate_terms:
        if term in text and term not in keywords:
            keywords.append(term)
    return keywords


def discover_kpis(
    question: str,
    context: Optional[str] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Discover relevant KPIs based on user question and context.

    Args:
        question: User's natural language question about KPIs
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
    system_prompt = KPI_DISCOVERY_SYSTEM.format(
        schema_fields=", ".join(FRAMMER_SCHEMA_FIELDS),
        fallback_guidance=KPI_FALLBACK_GUIDANCE,
    )

    user_prompt = f"USER QUESTION: {question}"
    if context:
        user_prompt += f"\n\nADDITIONAL CONTEXT: {context}"

    rag_source_refs: list[str] = []
    rag_matches: list[dict] = []
    try:
        _emit("Retrieving trusted KPI framework references...")
        rag_context, rag_source_refs, rag_matches = _retrieve_kpi_rag_context(
            question,
            context=context,
            top_k=5,
        )
        if rag_context:
            _emit("KPI framework context retrieved.")
            user_prompt += (
                "\n\nPRIMARY KPI FRAMEWORK CONTEXT (trusted RAG excerpts):\n"
                f"{rag_context}"
            )
    except Exception as e:
        print(f"KPI RAG retrieval failed: {e}")
        _emit("KPI framework retrieval unavailable. Continuing with built-in knowledge.")

    web_source_urls: list[str] = []
    try:
        _emit("Searching web for newer KPI guidance...")
        web_context, web_source_urls = _retrieve_web_kpi_context(question, context=context)
        if web_context:
            _emit("Web context retrieved.")
            user_prompt += (
                "\n\nSECONDARY WEB CONTEXT (use only for expansion or freshness):\n"
                f"{web_context}"
            )
    except Exception as e:
        print(f"Tavily search failed: {e}")
        _emit("Web search unavailable. Continuing with framework and domain knowledge.")

    question_keywords = _question_keywords(question, context=context)
    if question_keywords:
        user_prompt += (
            "\n\nUSER FOCUS SIGNALS:\n"
            f"- Prioritize KPIs matching these themes: {', '.join(question_keywords)}"
        )

    if rag_matches:
        user_prompt += (
            "\n\nGROUNDING PRIORITY:\n"
            "- First prefer KPI definitions and formulas supported by the KPI framework excerpts.\n"
            "- Then use web context to add newer or broader industry KPIs only when they still fit Frammer's schema.\n"
            "- Avoid returning the same generic KPI bundle unless it is clearly the best fit for this question.\n"
            "- Use fallback KPI intuition only if retrieved evidence is weak or incomplete.\n"
            "- Most KPIs should come from the framework when framework excerpts are available.\n"
        )
    elif web_source_urls:
        user_prompt += (
            "\n\nWEB EXPANSION PRIORITY:\n"
            "- No framework excerpts were retrieved, so rely on the web context for grounded KPI ideas.\n"
            "- Include newer web-derived KPIs when they are relevant and schema-compatible.\n"
        )

    if web_source_urls:
        user_prompt += (
            "\n\nWEB SOURCE REQUIREMENT:\n"
            "- At least one returned source should be a real web URL from the provided web context when available.\n"
            "- If the web context suggests a useful KPI not covered in the framework excerpts, include it.\n"
            "- Mark such KPI entries with source='Web expansion' or source='Hybrid'.\n"
        )

    if rag_matches:
        user_prompt += (
            "\n\nMIX TARGET:\n"
            "- Prefer a framework-led set.\n"
            "- If web context adds something genuinely new, include only 1-2 web expansion KPIs.\n"
            "- Mark framework-led KPI entries with source='Framework'.\n"
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
        kpis = _rebalance_kpis(kpis, rag_source_refs, web_source_urls)
        kpis = _attach_kpi_sources(kpis, rag_source_refs, web_source_urls)

        _emit("Preparing KPI summary...")
        # Generate summary
        summary = _generate_summary(question, kpis)

        return {
            "success": True,
            "kpis": kpis,
            "summary": summary,
            "query": question,
            "sources": _build_source_bundle(rag_source_refs, web_source_urls, max_items=6),
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse KPI suggestions: {e}",
            "raw_response": raw_content if 'raw_content' in locals() else None,
            "kpis": [],
            "summary": "I encountered an error while generating KPI suggestions.",
            "sources": [],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "kpis": [],
            "summary": f"An error occurred: {e}",
            "sources": [],
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


def handle_kpi_request(question: str) -> dict:
    """
    Main handler for KPI discovery requests.
    Called by the API when intent is classified as 'kpi'.

    Returns a dictionary with:
    - reply: Text summary for the user
    - kpis: List of KPI objects with LaTeX formulas
    - is_kpi_response: Flag for frontend to enable LaTeX rendering
    """

    result = discover_kpis(question)

    if not result["success"]:
        return {
            "reply": result["summary"],
            "kpis": [],
            "is_kpi_response": True,
            "kpi_sources": [],
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
    }


def handle_kpi_request_with_progress(
    question: str,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """KPI handler with optional live progress updates for streaming UIs."""
    result = discover_kpis(question, progress_callback=progress_callback)

    if not result["success"]:
        return {
            "reply": result["summary"],
            "kpis": [],
            "is_kpi_response": True,
            "kpi_sources": [],
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

