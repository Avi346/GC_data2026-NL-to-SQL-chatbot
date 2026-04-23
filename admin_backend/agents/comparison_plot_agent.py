"""
Comparison Plot Agent - dedicated side-by-side comparison chart workflow.

This agent is intentionally separate from plotting_agent.py to keep comparison
behavior deterministic and avoid recursive/hallucinated plan generation.
"""

from __future__ import annotations

import base64
import io
import re
from typing import Callable, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import json

from langchain_core.messages import SystemMessage, HumanMessage
from chatbot import llm
from plotting_agent import handle_plot_request


def is_comparison_plot_request(question: str) -> bool:
    q = question.lower()
    has_side_by_side = any(token in q for token in ("side-by-side", "side by side", "two separate charts", "two charts"))
    has_plot = any(token in q for token in ("plot", "chart", "graph", "line", "bar", "visualize", "visualise"))
    return has_side_by_side and has_plot


COMPARISON_PLANNER_SYSTEM = """You are an expert analytics planner.
The user wants to compare two or more things side-by-side in distinct charts.
Your job is to break down their comparison request into 2 to 4 distinct standalone chart plotting queries.

Output ONLY a valid JSON object with exactly this structure:
{
  "focus": "A short 1-sentence description of the comparison",
  "plots": [
    {
      "label": "Short Title 1",
      "query": "A clear, standalone prompt for a charting agent (e.g. 'Plot overall uploaded_count where channel_name = \\'A\\'')"
    }
  ]
}
RULES:
1. Each query must be completely standalone with NO references to 'the other chart'.
2. If comparing values like Channel A vs Channel B, explicitly state the channel_name.
3. If no metric is specified, default to 'uploaded_count'.
4. Do NOT include Markdown fences (no ```json). Output raw JSON.
"""

def _build_subqueries(question: str) -> tuple[list[dict], str]:
    try:
        response = llm.invoke([
            SystemMessage(content=COMPARISON_PLANNER_SYSTEM),
            HumanMessage(content=question)
        ])
        
        text = response.content.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE).strip()
        
        data = json.loads(text)
        plots = data.get("plots", [])
        focus = data.get("focus", "Compare the charts side-by-side.")
        
        if len(plots) >= 2:
            return plots[:4], focus
    except Exception as e:
        print(f"Comparison planner LLM failed: {e}")
        pass
        
    # Safe fallback if JSON parsing or LLM fails
    clean_question = re.sub(r"^compare\s+", "", question, flags=re.IGNORECASE).strip()
    return (
        [
            {"label": "Chart 1", "query": f"Plot {clean_question}" if not any(tok in clean_question.lower() for tok in ("plot", "chart", "graph")) else clean_question},
            {"label": "Chart 2", "query": f"Plot {clean_question}" if not any(tok in clean_question.lower() for tok in ("plot", "chart", "graph")) else clean_question},
        ],
        "Compare the side-by-side charts.",
    )


def _combine_side_by_side(charts: list[tuple[str, str]]) -> str:
    if len(charts) < 2:
        raise ValueError("Need at least two charts to combine.")

    cols = 2
    rows = (len(charts) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(9 * cols, 6.2 * rows))
    fig.patch.set_facecolor("#0f1115")
    axes_list = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for ax in axes_list:
        ax.set_facecolor("#0f1115")
        ax.axis("off")

    for idx, (label, image_b64) in enumerate(charts):
        img = mpimg.imread(io.BytesIO(base64.b64decode(image_b64)), format="png")
        axes_list[idx].imshow(img)
        axes_list[idx].set_title(label, color="#f8fafc", fontsize=13, pad=8)

    for j in range(len(charts), len(axes_list)):
        axes_list[j].axis("off")

    fig.suptitle("Comparison View", color="#f8fafc", fontsize=16, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out = io.BytesIO()
    fig.savefig(out, format="png", dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    out.seek(0)
    encoded = base64.b64encode(out.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def handle_comparison_plot_request(
    question: str,
    session_id: str = "default",
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    def emit(message: str) -> None:
        if progress_callback:
            try:
                progress_callback(message)
            except Exception:
                pass

    emit("Calling comparison plot agent...")
    plans, focus = _build_subqueries(question)

    emit(f"Generating {len(plans)} charts...")
    results: list[tuple[str, dict]] = []
    for i, plan in enumerate(plans):
        emit(f"Rendering {plan['label']}...")
        result = handle_plot_request(
            plan["query"],
            f"{session_id}::cmp::{i}",
            progress_callback,
        )
        results.append((plan["label"], result))

    successful = [(label, r) for label, r in results if r.get("chart_image")]
    if len(successful) < 2:
        return {
            "reply": (
                "### Comparison Not Available\n"
                "- I could not generate enough charts for a valid side-by-side comparison.\n"
                "- Please use a clearer request like `Compare overall uploaded_count for Channel A vs Channel B`."
            ),
            "chart_image": successful[0][1].get("chart_image") if successful else None,
        }

    successful.sort(key=lambda x: x[0])
    emit("Aligning comparison charts side by side...")
    combined_chart = _combine_side_by_side([(label, r["chart_image"]) for label, r in successful])

    emit("Generating comparison summary...")
    comparison_context = {
        "focus": focus,
        "charts": []
    }
    for label, result in successful:
        comparison_context["charts"].append({
            "label": label,
            "facts": result.get("chart_facts", {}),
            "original_summary": result.get("reply", "")
        })

    try:
        summary_response = llm.invoke([
            SystemMessage(content=(
                "You are an expert data analyst giving a side-by-side comparison summary. "
                "You will receive a JSON payload containing facts about several charts. "
                "Write a brief, insightful comparative analysis (3-4 bullet points) that compares the charts, highlighting differences, winners, or notable trends. "
                "Do not output markdown headers like '### Comparison Summary'. "
                "Just output the bullet points directly starting with '- '."
            )),
            HumanMessage(content=json.dumps(comparison_context))
        ])
        unified_summary = summary_response.content.strip()
    except Exception as e:
        print(f"Comparison summary LLM failed: {e}")
        unified_summary = ""
        for label, result in successful:
            bullets = [
                line.strip() for line in result.get("reply", "").splitlines()
                if line.strip().startswith("-") or line.strip().startswith("*")
            ]
            unified_summary += f"\n**{label}:**\n" + ("\n".join(bullets) if bullets else "Data plotted successfully.")

    return {
        "reply": f"### Comparison Summary\n{unified_summary}",
        "chart_image": combined_chart,
    }
