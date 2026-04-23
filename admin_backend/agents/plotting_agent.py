"""
Plotting Agent - generates server-side matplotlib/seaborn charts from natural
language questions.

This agent reuses the existing SQL Agent from chatbot.py for data retrieval,
then uses the LLM to write a matplotlib/seaborn script and executes it
server-side to produce a base64 PNG chart.
"""

import ast
import json
import traceback
import re
import os
import time
from typing import Optional, Callable

from chart_insights import build_chart_fact_pack
from chatbot import invoke_sql_agent, llm
from conversation_context import save_last_result
from langchain_core.messages import HumanMessage, SystemMessage


# ─────────────────────────────────────────────────────────────────────────────
# Data retrieval
# ─────────────────────────────────────────────────────────────────────────────

DATA_RETRIEVAL_SYSTEM = """You are a data-retrieval assistant for an analytics chatbot.

The user will ask a question that needs data to be plotted.

Your ONLY job is to retrieve the raw data from the database and return it as a
JSON array of objects — nothing else.

OUTPUT RULES (non-negotiable):
1. Return ONLY a valid JSON array. Example: [{"label": "A", "value": 10}]
2. Do NOT include any explanation, markdown fences, or prose.
3. Do NOT summarise or interpret the data — return rows as-is.
4. Include ALL columns that could be useful for the chart (labels, values,
   categories, dates, units).
5. If the data contains dates or timestamps, keep them as-is (do not format).
6. If no relevant data exists, return an empty array: []
"""


def get_data_for_plot(
    question: str,
    session_id: str = "default",
    progress_callback: Optional[Callable[[str], None]] = None,
) -> tuple[str, list[dict]]:
    """Ask the existing SQL agent to retrieve data as raw JSON rows."""
    retrieval_question = (
        f"{question}\n\n"
        "IMPORTANT: Return ONLY the raw query result as a JSON array of objects. "
        "No explanation. No markdown. No prose. Just valid JSON.\n"
        "Example format: [{\"col_a\": \"value\", \"col_b\": 42}]\n"
        "If the requested metric or dimension does not exist in the available schema, "
        "return an empty array: []"
    )

    if progress_callback:
        progress_callback("Calling SQL agent for plot data...")
    result = invoke_sql_agent(retrieval_question, session_id=session_id, mode="plot_data")
    raw_output: str = result.get("output", "[]")
    data = _extract_json(raw_output)
    return raw_output, data


# ─────────────────────────────────────────────────────────────────────────────
# JSON extraction helpers
# ─────────────────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> list[dict]:
    """Best-effort JSON extraction from agent output."""
    cleaned = re.sub(r"```(?:json)?", "", text).strip().strip("`")

    candidates: list[str] = []

    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        candidates.append(match.group())

    first_bracket = cleaned.find("[")
    if first_bracket != -1:
        candidates.append(cleaned[first_bracket:])

    first_brace = cleaned.find("{")
    if first_brace != -1:
        candidates.append(cleaned[first_brace:])

    candidates.append(cleaned)

    for candidate in candidates:
        parsed = _parse_json_like(candidate)
        if parsed:
            return parsed

    return []


def _parse_json_like(text: str) -> list[dict]:
    """Parse valid or nearly-valid JSON/Python-literal row payloads."""
    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(text)
            if isinstance(parsed, list):
                return [item for item in parsed if isinstance(item, dict)]
            if isinstance(parsed, dict):
                return [parsed]
        except Exception:
            continue

    decoder = json.JSONDecoder()
    rows: list[dict] = []
    idx = 0
    while idx < len(text):
        brace_pos = text.find("{", idx)
        if brace_pos == -1:
            break
        try:
            parsed, end_idx = decoder.raw_decode(text, brace_pos)
            if isinstance(parsed, dict):
                rows.append(parsed)
                idx = end_idx
                continue
        except json.JSONDecodeError:
            pass
        idx = brace_pos + 1

    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Plotting script generation
# ─────────────────────────────────────────────────────────────────────────────

PLOT_SCRIPT_SYSTEM = """You are an expert Python data-visualization engineer.

You will be given:
  1. A user question describing the desired chart.
  2. A JSON array of data rows retrieved from a database.

Your job is to write a COMPLETE, SELF-CONTAINED Python script that produces
the chart and prints it as a base64-encoded PNG string.

═══════════════════════════════════════════════════
HARD RULES — violating any of these will cause failure
═══════════════════════════════════════════════════
1. Start with:
       import matplotlib
       matplotlib.use('Agg')
   This MUST be the first two lines before any other import.

2. Import ONLY from this whitelist:
       matplotlib, matplotlib.pyplot, matplotlib.ticker,
       matplotlib.dates, seaborn, pandas, numpy, io, base64, json

3. Embed the provided data VERBATIM as a Python list of dicts:
       data = [ ... ]

4. Always convert data to a pandas DataFrame:
       df = pd.DataFrame(data)

5. Coerce numeric columns explicitly before plotting:
       df["col"] = pd.to_numeric(df["col"], errors="coerce")
   Never assume a column is already numeric.

6. End the script by saving and printing base64:
       buf = io.BytesIO()
       fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                   facecolor=fig.get_facecolor())
       buf.seek(0)
       print(base64.b64encode(buf.read()).decode('utf-8'))
       plt.close(fig)
   The LAST line printed must be the raw base64 string — nothing else.

7. Return ONLY raw Python code. No markdown fences (no ```). No explanations.

═══════════════════════════════════════════════════
THEMING — always apply this dark theme
═══════════════════════════════════════════════════
Apply these rcParams BEFORE creating any figure:

    plt.rcParams.update({
        'figure.facecolor':  '#0f1115',
        'axes.facecolor':    '#0f1115',
        'axes.edgecolor':    '#1e293b',
        'axes.labelcolor':   '#f8fafc',
        'axes.titlecolor':   '#f8fafc',
        'text.color':        '#f8fafc',
        'xtick.color':       '#94a3b8',
        'ytick.color':       '#94a3b8',
        'grid.color':        '#1e293b',
        'grid.alpha':        0.4,
        'legend.facecolor':  '#1e293b',
        'legend.edgecolor':  '#334155',
        'legend.labelcolor': '#f8fafc',
    })

Accent color palette (use in order):
    COLORS = ['#6366f1','#a855f7','#22d3ee','#f472b6',
              '#34d399','#fb923c','#facc15','#60a5fa']

═══════════════════════════════════════════════════
LAYOUT & READABILITY RULES
═══════════════════════════════════════════════════
• Figure size: (12, 6) for most charts; (10, 8) for heatmaps; (8, 8) for pie.
• Title: fontsize=15, fontweight='bold', pad=18, color='#f8fafc'
• Axis labels: fontsize=12
• If there are MORE than 4 x-axis labels, rotate them 45°:
      plt.xticks(rotation=45, ha='right')
• If there are MORE than 8 x-axis labels, rotate them 90°.
• If a legend would have more than 6 entries, move it outside the axes:
      ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
      plt.tight_layout(rect=[0, 0, 0.82, 1])
  Otherwise use plt.tight_layout().
• Add light horizontal grid lines on the value axis for bar/line/area charts:
      ax.yaxis.grid(True, linestyle='--', alpha=0.4)
      ax.set_axisbelow(True)

═══════════════════════════════════════════════════
CHART TYPE GUIDE
═══════════════════════════════════════════════════
BAR CHART
  • Use seaborn.barplot (estimator='sum' if data is not pre-aggregated).
  • Add value labels on bars:
        for bar in ax.patches:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h * 1.01,
                        f'{h:,.0f}', ha='center', va='bottom',
                        fontsize=9, color='#f8fafc')

LINE CHART / TREND
  • Use seaborn.lineplot with markers=True, linewidth=2.
  • If the x-axis is a date/time column, parse it:
        df['date_col'] = pd.to_datetime(df['date_col'], errors='coerce')
    Then use matplotlib.dates.AutoDateFormatter for tick labels.

PIE CHART
  • Use plt.pie with autopct='%1.1f%%', startangle=140.
  • Pass colors=COLORS[:len(df)] and wedgeprops={'edgecolor': '#0f1115', 'linewidth': 1.5}.
  • Set ax.set_facecolor('#0f1115') explicitly after pie().

HISTOGRAM
  • Use seaborn.histplot with kde=True, color=COLORS[0], edgecolor='#0f1115'.

BOX PLOT
  • Use seaborn.boxplot.
  • x = categorical grouping column, y = numeric measure column.
  • If grouping column is not specified, use the first non-numeric column for x.

VIOLIN PLOT
  • Use seaborn.violinplot. Same column selection logic as box plot.
  • inner='box' for compact inner summary.

HEATMAP
  • Build a pivot_table first:
        pivot = df.pivot_table(index=row_col, columns=col_col,
                               values=val_col, aggfunc='sum', fill_value=0)
  • Use seaborn.heatmap with annot=True, fmt='.0f', cmap='magma',
    linewidths=0.3, linecolor='#0f1115'.

SCATTER PLOT
  • Use seaborn.scatterplot with s=80, alpha=0.75.
  • If a third categorical column exists, use it as hue.

AREA CHART
  • Use ax.fill_between(x, y, alpha=0.35, color=COLORS[0]).
  • Also draw the line: ax.plot(x, y, color=COLORS[0], linewidth=2).

GROUPED / STACKED BAR
  • Grouped: use seaborn.barplot with hue= the grouping column.
  • Stacked: pivot the data and use df.plot(kind='bar', stacked=True, ax=ax).

═══════════════════════════════════════════════════
DATA SHAPE HANDLING
═══════════════════════════════════════════════════
• Identify categorical columns by name patterns:
    *_name, *_type, *_category, *_source, *_channel, *_period, *_label
• Identify numeric columns by name patterns:
    *_count, *_total, *_sum, *_avg, *_rate, *_pct, *_duration, *_value, *_score

• If the data has only ONE row, still plot it — a single-bar chart is valid.

• If the user requests duration in hours/minutes but values look like seconds
  (> 3600 for "hours", > 60 for "minutes"), convert:
        df['col'] = df['col'] / 3600   # seconds → hours

• For boxplots/violins on row-level data (multiple rows per category),
  do NOT aggregate first — pass raw rows to seaborn directly.

• For heatmaps where multiple rows share the same cell key, aggregate with
  sum by default (or the operation the user implies).

• Never refuse to plot because data is not pre-aggregated.
  Use groupby / pivot_table / melt to reshape as needed.

═══════════════════════════════════════════════════
COMPLETE TEMPLATE (adapt as needed)
═══════════════════════════════════════════════════
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io, base64

data = [{"name": "A", "value": 10}, {"name": "B", "value": 20}]
df = pd.DataFrame(data)
df["value"] = pd.to_numeric(df["value"], errors="coerce")

COLORS = ['#6366f1','#a855f7','#22d3ee','#f472b6',
          '#34d399','#fb923c','#facc15','#60a5fa']

plt.rcParams.update({
    'figure.facecolor':  '#0f1115',
    'axes.facecolor':    '#0f1115',
    'axes.edgecolor':    '#1e293b',
    'axes.labelcolor':   '#f8fafc',
    'axes.titlecolor':   '#f8fafc',
    'text.color':        '#f8fafc',
    'xtick.color':       '#94a3b8',
    'ytick.color':       '#94a3b8',
    'grid.color':        '#1e293b',
    'grid.alpha':        0.4,
    'legend.facecolor':  '#1e293b',
    'legend.edgecolor':  '#334155',
    'legend.labelcolor': '#f8fafc',
})

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(df["name"], df["value"], color=COLORS[:len(df)])
ax.set_title("My Chart", fontsize=15, fontweight='bold', pad=18)
ax.set_xlabel("Category", fontsize=12)
ax.set_ylabel("Value", fontsize=12)
ax.yaxis.grid(True, linestyle='--', alpha=0.4)
ax.set_axisbelow(True)
plt.tight_layout()

buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
buf.seek(0)
print(base64.b64encode(buf.read()).decode('utf-8'))
plt.close(fig)
"""


def generate_plot_script(
    question: str,
    data: list[dict],
    error_context: Optional[str] = None,
    failed_script: Optional[str] = None,
) -> str:
    """Ask the LLM to write a plotting script for the given data."""
    user_prompt = (
        f"USER QUESTION: {question}\n\n"
        f"DATA (JSON):\n{json.dumps(data, indent=2)}\n\n"
        "Write the Python plotting script now. Return ONLY raw Python code — "
        "no markdown fences, no explanation."
    )

    if error_context:
        user_prompt += (
            "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "PREVIOUS ATTEMPT FAILED.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        if failed_script:
            user_prompt += (
                f"FAILED SCRIPT:\n{failed_script}\n\n"
            )
        user_prompt += (
            f"ERROR MESSAGE:\n{error_context}\n\n"
            "Instructions for the fix:\n"
            "• Read the error carefully and fix the exact line/issue.\n"
            "• Re-check column names against the DATA above — use exact names.\n"
            "• Ensure all numeric columns are coerced with pd.to_numeric().\n"
            "• If a column used for x/y does not exist, pick the correct column from the data.\n"
            "• If reshaping is needed (pivot, melt, groupby), add it.\n"
            "• Return ONLY the corrected Python code."
        )

    response = llm.invoke(
        [
            SystemMessage(content=PLOT_SCRIPT_SYSTEM),
            HumanMessage(content=user_prompt),
        ]
    )

    script = response.content.strip()
    # Strip markdown fences if the model adds them despite instructions
    script = re.sub(r"^```(?:python)?\s*", "", script, flags=re.MULTILINE)
    script = re.sub(r"\s*```$", "", script, flags=re.MULTILINE)
    return script.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Script execution
# ─────────────────────────────────────────────────────────────────────────────

def execute_plot_script(script: str) -> tuple[Optional[str], Optional[str]]:
    """Execute the generated plotting script in a sandboxed namespace."""
    import sys
    from io import StringIO

    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()

    try:
        safe_globals = {"__builtins__": __builtins__}
        exec(script, safe_globals)  # noqa: S102
    except Exception:
        error_message = traceback.format_exc()
        return None, error_message
    finally:
        sys.stdout = old_stdout

    output = captured.getvalue().strip()
    if not output:
        return None, "The plotting script produced no output. It must print the base64 PNG string."

    # The last non-empty line should be the base64 string
    b64_candidate = output.splitlines()[-1].strip()
    if len(b64_candidate) > 100:
        return b64_candidate, None

    return None, (
        f"Script output was too short to be a valid base64 PNG "
        f"(got {len(b64_candidate)} chars): {b64_candidate[:200]}"
    )


def _to_float(value) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip().replace(",", "")
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _select_plot_columns(data: list[dict]) -> tuple[Optional[str], Optional[str], list[str], list[str]]:
    if not data:
        return None, None, [], []

    columns = sorted({k for row in data for k in row.keys()})
    numeric_cols: list[str] = []
    label_cols: list[str] = []

    for col in columns:
        vals = [_to_float(row.get(col)) for row in data]
        valid = [v for v in vals if v is not None]
        if valid and len(valid) >= max(1, len(data) // 2):
            numeric_cols.append(col)
        else:
            label_cols.append(col)

    x_col = label_cols[0] if label_cols else None
    y_col = numeric_cols[0] if numeric_cols else None
    return x_col, y_col, label_cols, numeric_cols


def _infer_chart_type(question: str) -> str:
    q = question.lower()
    if "pie" in q or "donut" in q:
        return "pie"
    if "line" in q or "trend" in q or "over time" in q:
        return "line"
    if "scatter" in q:
        return "scatter"
    if "hist" in q or "distribution" in q:
        return "hist"
    return "bar"


def _has_any_numeric_value(data: list[dict]) -> bool:
    for row in data:
        for value in row.values():
            if _to_float(value) is not None:
                return True
    return False


def _summarize_without_llm(question: str, data: list[dict], chart_facts: dict) -> str:
    points = chart_facts.get("key_points", [])
    if not points:
        return "### Chart Summary\n- Here's the chart based on your query."

    bullets = points[:2] if len(points) >= 2 else points[:1]
    lines = ["### Chart Summary", f"- Query: {question}"]
    lines.extend([f"- {item}" for item in bullets])
    return "\n".join(lines)


def _build_safe_summary_payload(question: str, chart_facts: dict) -> dict:
    """Minimal payload for LLM summary generation to avoid leaking raw row-level data."""
    return {
        "question": question,
        "row_count": chart_facts.get("row_count", 0),
        "numeric_columns": chart_facts.get("numeric_columns", []),
        "label_columns": chart_facts.get("label_columns", []),
        "key_points": chart_facts.get("key_points", [])[:4],
    }


def _render_plot_fast(question: str, data: list[dict]) -> tuple[Optional[str], Optional[str]]:
    """
    Fast deterministic renderer for common chart requests.
    Falls back to LLM-generated code when data shape is ambiguous.
    """
    if not data:
        return None, "No data available for plotting."

    x_col, y_col, label_cols, numeric_cols = _select_plot_columns(data)
    if not numeric_cols:
        return None, "No numeric columns found for plotting."

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    import warnings
    import io
    import base64

    chart_type = _infer_chart_type(question)
    df = pd.DataFrame(data)

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if x_col and x_col in df.columns:
        df = df[df[x_col].notna()]

    if y_col is None:
        y_col = numeric_cols[0]

    plt.rcParams.update(
        {
            "figure.facecolor": "#0f1115",
            "axes.facecolor": "#0f1115",
            "axes.edgecolor": "#1e293b",
            "axes.labelcolor": "#f8fafc",
            "axes.titlecolor": "#f8fafc",
            "text.color": "#f8fafc",
            "xtick.color": "#94a3b8",
            "ytick.color": "#94a3b8",
            "grid.color": "#1e293b",
            "grid.alpha": 0.4,
            "legend.facecolor": "#1e293b",
            "legend.edgecolor": "#334155",
            "legend.labelcolor": "#f8fafc",
        }
    )
    colors = ["#6366f1", "#a855f7", "#22d3ee", "#f472b6", "#34d399", "#fb923c", "#facc15", "#60a5fa"]

    fig_size = (12, 6) if chart_type != "pie" else (8, 8)
    fig, ax = plt.subplots(figsize=fig_size)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if chart_type == "pie":
            if not x_col:
                return None, "Pie chart needs one label column and one numeric column."
            pie_df = df[[x_col, y_col]].dropna().sort_values(y_col, ascending=False)
            ax.pie(
                pie_df[y_col],
                labels=pie_df[x_col].astype(str),
                autopct="%1.1f%%",
                startangle=140,
                colors=colors[: len(pie_df)],
                wedgeprops={"edgecolor": "#0f1115", "linewidth": 1.5},
            )
            ax.set_title(question.strip()[:80] or "Distribution", fontsize=15, fontweight="bold", pad=18)
        elif chart_type == "line":
            if x_col:
                line_df = df[[x_col, y_col]].dropna()
                ax.plot(line_df[x_col].astype(str), line_df[y_col], color=colors[0], marker="o", linewidth=2)
                if len(line_df) > 4:
                    plt.xticks(rotation=45, ha="right")
            else:
                line_df = df[[y_col]].dropna().reset_index(drop=True)
                ax.plot(line_df.index, line_df[y_col], color=colors[0], marker="o", linewidth=2)
            ax.yaxis.grid(True, linestyle="--", alpha=0.4)
            ax.set_axisbelow(True)
            ax.set_ylabel(y_col)
            ax.set_title(question.strip()[:80] or "Trend", fontsize=15, fontweight="bold", pad=18)
        elif chart_type == "scatter":
            if len(numeric_cols) < 2:
                return None, "Scatter plot needs at least two numeric columns."
            x_num, y_num = numeric_cols[0], numeric_cols[1]
            plot_df = df[[x_num, y_num]].dropna()
            sns.scatterplot(data=plot_df, x=x_num, y=y_num, s=80, alpha=0.75, color=colors[0], ax=ax)
            ax.set_title(question.strip()[:80] or "Scatter Plot", fontsize=15, fontweight="bold", pad=18)
        elif chart_type == "hist":
            sns.histplot(df[y_col].dropna(), kde=True, color=colors[0], edgecolor="#0f1115", ax=ax)
            ax.set_title(question.strip()[:80] or "Distribution", fontsize=15, fontweight="bold", pad=18)
            ax.set_xlabel(y_col)
        else:
            # default bar chart
            if x_col:
                bar_df = df[[x_col, y_col]].dropna().sort_values(y_col, ascending=False)
                ax.bar(bar_df[x_col].astype(str), bar_df[y_col], color=[colors[i % len(colors)] for i in range(len(bar_df))])
                if len(bar_df) > 8:
                    plt.xticks(rotation=90)
                elif len(bar_df) > 4:
                    plt.xticks(rotation=45, ha="right")
            else:
                bar_df = df[[y_col]].dropna().reset_index(drop=True)
                ax.bar(bar_df.index.astype(str), bar_df[y_col], color=[colors[i % len(colors)] for i in range(len(bar_df))])

            for bar in ax.patches:
                h = bar.get_height()
                if h and h > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        h * 1.01,
                        f"{h:,.0f}",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                        color="#f8fafc",
                    )

            ax.yaxis.grid(True, linestyle="--", alpha=0.4)
            ax.set_axisbelow(True)
            ax.set_ylabel(y_col)
            ax.set_title(question.strip()[:80] or "Bar Chart", fontsize=15, fontweight="bold", pad=18)

    ax.set_xlabel(x_col if x_col else "Index")
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded, None


# ─────────────────────────────────────────────────────────────────────────────
# Main handler
# ─────────────────────────────────────────────────────────────────────────────

MAX_RETRIES = 2


def _handle_single_plot_request(
    question: str,
    session_id: str = "default",
    progress_callback: Optional[Callable[[str], None]] = None,
    persist_context: bool = True,
) -> dict:
    """Single-chart flow used by both standard and comparison modes."""
    def _emit(message: str) -> None:
        if progress_callback:
            try:
                progress_callback(message)
            except Exception:
                pass

    _emit("Calling plotting agent...")
    t0 = time.perf_counter()
    # 1. Retrieve data
    try:
        _emit("Querying database for chart data...")
        raw_output, data = get_data_for_plot(
            question,
            session_id=session_id,
            progress_callback=progress_callback,
        )
    except Exception as e:
        return {
            "reply": f"Sorry, I couldn't retrieve the data needed for this chart. Error: {e}",
            "chart_image": None,
        }
    t_data = time.perf_counter()

    if not data:
        return {
            "reply": (
                "### Data Not Available\n"
                "- I wasn't able to retrieve any matching data to build this chart.\n"
                "- This usually happens if the requested timeframe (like day-by-day) or metric isn't supported by the current data schema."
            ),
            "chart_image": None,
        }
    if not _has_any_numeric_value(data):
        return {
            "reply": (
                "### Chart Not Available\n"
                "- The retrieved rows do not contain numeric values to plot.\n"
                "- This usually means the requested breakdown is not present in the current schema."
            ),
            "chart_image": None,
        }

    # 2. Prefer fast deterministic renderer for common chart types.
    _emit("Rendering chart...")
    chart_b64, error_context = _render_plot_fast(question, data)
    used_llm_plotter = False
    t_fast = time.perf_counter()

    # 3. Fallback to LLM-generated plotting script when needed.
    script: Optional[str] = None
    if chart_b64 is None:
        used_llm_plotter = True
        if error_context and "No numeric columns found for plotting" in error_context:
            return {
                "reply": (
                    "### Chart Not Available\n"
                    "- I could not find any numeric series for this request.\n"
                    "- Please try a metric available in the data (uploaded_count, created_count, published_count, or duration fields)."
                ),
                "chart_image": None,
            }
        _emit("Fallback: generating plotting script with LLM...")
        for attempt in range(MAX_RETRIES + 1):
            try:
                script = generate_plot_script(
                    question,
                    data,
                    error_context=error_context if attempt > 0 else None,
                    failed_script=script if attempt > 0 else None,
                )
            except Exception as e:
                return {
                    "reply": f"I retrieved the data but couldn't generate a plot script. Error: {e}",
                    "chart_image": None,
                }

            chart_b64, error_context = execute_plot_script(script)
            if chart_b64 is not None:
                break  # success
    t_plot = time.perf_counter()

    # 4. If all retries failed, return raw data
    if chart_b64 is None:
        return {
            "reply": (
                "I retrieved the data but chart generation failed after "
                f"{MAX_RETRIES + 1} attempts."
                + (f"\n\nLast error:\n{error_context}" if error_context else "")
                + "\n\nHere's the raw data:\n\n"
                + json.dumps(data, indent=2)
            ),
            "chart_image": None,
        }

    # 5. Build chart facts and generate summary.
    _emit("Generating chart summary...")
    data_sample = data[:5]
    data_columns = sorted({key for row in data_sample for key in row.keys()})
    chart_facts = build_chart_fact_pack(data, question)

    use_llm_summary = os.getenv("PLOT_SUMMARY_WITH_LLM", "1") == "1"
    if use_llm_summary:
        try:
            safe_summary_payload = _build_safe_summary_payload(question, chart_facts)
            summary_response = llm.invoke(
                [
                    SystemMessage(
                        content=(
                            "You are a concise data analyst. You will receive a sanitized "
                            "chart-facts payload only. Write a Markdown summary. "
                            "Use this structure:\n"
                            "### Chart Summary\n"
                            "- bullet 1\n"
                            "- bullet 2\n"
                            "Do NOT mention SQL, database tables, or technical details."
                        )
                    ),
                    HumanMessage(
                        content=f"Sanitized chart facts: {json.dumps(safe_summary_payload)}"
                    ),
                ]
            )
            summary = summary_response.content.strip()
        except Exception:
            summary = _summarize_without_llm(question, data, chart_facts)
    else:
        summary = _summarize_without_llm(question, data, chart_facts)

    if persist_context:
        save_last_result(
            session_id,
            {
                "result_type": "plot",
                "question": question,
                "reply": summary,
                "data_sample": data_sample,
                "data_columns": data_columns,
                "full_data": data,
                "chart_facts": chart_facts,
                "used_llm_plotter": used_llm_plotter,
            },
        )

    print(
        "[PlotPerf] "
        f"data_fetch={t_data - t0:.2f}s "
        f"fast_render={t_fast - t_data:.2f}s "
        f"fallback_render={t_plot - t_fast:.2f}s "
        f"summary+save={time.perf_counter() - t_plot:.2f}s "
        f"total={time.perf_counter() - t0:.2f}s "
        f"rows={len(data)} "
        f"used_llm_plotter={used_llm_plotter}"
    )

    return {
        "reply": summary,
        "chart_image": chart_b64,
        "_chart_facts": chart_facts,
    }


def handle_plot_request(
    question: str,
    session_id: str = "default",
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """End-to-end handler for standard single-chart requests."""
    return _handle_single_plot_request(
        question=question,
        session_id=session_id,
        progress_callback=progress_callback,
        persist_context=True,
    )
