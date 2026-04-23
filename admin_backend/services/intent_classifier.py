
"""
Intent Classifier Agent - determines whether a user question requires:
- A chart/visualization (plot)
- A plain text answer (text)
- KPI discovery and suggestions (kpi)
"""

import os
import re

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=GROQ_API_KEY, temperature=0)


CLASSIFY_SYSTEM = """You are a routing classifier for an analytics chatbot.

Your ONLY job is to decide whether the user wants:
- A VISUAL CHART (plot)
- A TEXT ANSWER from the database (text)
- KPI DISCOVERY and suggestions (kpi)

───────────────────────────────────────────────
OUTPUT RULE (non-negotiable)
───────────────────────────────────────────────
Respond with EXACTLY one word — either:
  plot
  text
  kpi

No punctuation. No explanation. No markdown.

───────────────────────────────────────────────
ROUTE TO "kpi" when the user:
───────────────────────────────────────────────
• Explicitly asks about KPIs or metrics to track:
    "what KPIs should I track",
    "suggest KPIs for...",
    "which metrics are important",
    "recommend performance indicators",
    "what should I measure"

• Asks about formulas or calculations for metrics:
    "how do I calculate efficiency",
    "what's the formula for growth rate",
    "how to measure productivity",
    "show me the ROI formula"

• Asks for metric recommendations or suggestions:
    "what metrics matter for...",
    "suggest ways to measure...",
    "how can I track performance",
    "what indicators show success"

• Uses KPI-related keywords:
    KPI, key performance indicator, metric, measure,
    benchmark, indicator, scorecard, dashboard metrics,
    performance measure, success metric, efficiency ratio,
    productivity metric, growth metric

• Asks about industry standards or best practices for measurement:
    "industry standard metrics",
    "best KPIs for video production",
    "how do others measure..."

───────────────────────────────────────────────
ROUTE TO "plot" when the user:
───────────────────────────────────────────────
• Explicitly names a chart type:
    bar chart, bar graph, grouped bar, stacked bar,
    line chart, line graph, trend line,
    pie chart, donut chart,
    scatter plot, scatter chart, bubble chart,
    histogram, distribution chart,
    box plot, boxplot, whisker plot,
    violin plot, violin chart,
    heatmap, heat map, correlation matrix,
    area chart, stacked area,
    funnel chart, waterfall chart,
    gantt chart, timeline chart

• Uses a visualization intent verb:
    plot, chart, graph, visualize, visualise, draw,
    sketch a graph, generate a chart, show a chart,
    display a chart, render a chart, map out (data)

• Asks to "compare" values AND implies a visual output:
    "compare sales across regions visually",
    "show me how X vs Y looks as a chart"

• Asks about trends / distributions / patterns with visual intent:
    "show the trend of X over time as a graph",
    "what does the distribution of Y look like in a chart"

───────────────────────────────────────────────
ROUTE TO "text" when the user:
───────────────────────────────────────────────
• Asks a factual question about EXISTING DATA with no visual/KPI keyword:
    "how many users signed up last month",
    "which product had the highest sales",
    "what is the average order value"

• Uses list/fetch/count intent words for DATA RETRIEVAL:
    show, list, give me, tell me, find, fetch, count,
    which, who, what, when, how many, how much

• Asks for analysis, explanation, or prose summary of DATA:
    "why did sales drop", "summarize the performance",
    "explain the churn rate"

───────────────────────────────────────────────
PRIORITY RULES
───────────────────────────────────────────────
1. If the message explicitly mentions KPI, metric, indicator, formula,
   or asks "what should I measure/track" → answer "kpi"

2. If the message contains chart keywords or visualization verbs → answer "plot"

3. Otherwise → answer "text"

Examples:
  "show me how many users signed up"           → text
  "show me a bar chart of user signups"        → plot
  "what KPIs should I track for user growth"   → kpi
  "suggest metrics for measuring efficiency"   → kpi
  "how do I calculate publish rate"            → kpi
  "what's the formula for ROI"                 → kpi
  "compare revenue across regions"             → text
  "plot revenue across regions"                → plot
  "what metrics matter for video production"   → kpi
  "which user uploaded the most videos"        → text
"""


def classify_intent(question: str) -> str:
    """Classify a user question as 'plot', 'text', or 'kpi'."""
    q = (question or "").strip().lower()
    if not q:
        return "text"

    # Fast local fallback to keep routing stable even if the LLM is unavailable.
    kpi_patterns = (
        r"\bkpi(s)?\b",
        r"\bkey performance indicator(s)?\b",
        r"\bmetric(s)?\b",
        r"\bindicator(s)?\b",
        r"\bformula\b",
        r"\bmeasure\b",
    )
    plot_patterns = (
        r"\bplot\b",
        r"\bchart\b",
        r"\bgraph\b",
        r"\bvisuali[sz]e\b",
        r"\bline chart\b",
        r"\bbar chart\b",
        r"\bpie chart\b",
        r"\bscatter\b",
        r"\bheatmap\b",
        r"\bcompare\b.*\b(chart|plot|graph)\b",
    )

    if any(re.search(p, q) for p in kpi_patterns):
        return "kpi"
    if any(re.search(p, q) for p in plot_patterns):
        return "plot"

    try:
        response = llm.invoke(
            [
                SystemMessage(content=CLASSIFY_SYSTEM),
                HumanMessage(content=question),
            ]
        )
        answer = response.content.strip().lower()
        if "kpi" in answer:
            return "kpi"
        if "plot" in answer:
            return "plot"
    except Exception:
        # Fall back to text for resilience when model/network calls fail.
        pass

    return "text"
