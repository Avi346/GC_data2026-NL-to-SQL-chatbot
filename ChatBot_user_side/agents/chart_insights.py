from __future__ import annotations

from typing import Any


def _to_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip().replace(",", "")
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


def build_chart_fact_pack(data: list[dict], question: str) -> dict[str, Any]:
    """Compute grounded chart facts for safer follow-up explanations."""
    if not data:
        return {
            "question": question,
            "row_count": 0,
            "numeric_columns": [],
            "label_columns": [],
            "key_points": ["No chart data was saved for this result."],
        }

    columns = sorted({key for row in data for key in row.keys()})
    numeric_columns: list[str] = []
    label_columns: list[str] = []

    for column in columns:
        numeric_values = [_to_float(row.get(column)) for row in data]
        valid_numeric = [value for value in numeric_values if value is not None]
        if valid_numeric and len(valid_numeric) >= max(2, len(data) // 2):
            numeric_columns.append(column)
        else:
            label_columns.append(column)

    key_points: list[str] = [f"The chart contains {len(data)} plotted rows."]

    if numeric_columns:
        primary_numeric = numeric_columns[0]
        numeric_series = [
            {"row": row, "value": _to_float(row.get(primary_numeric))}
            for row in data
            if _to_float(row.get(primary_numeric)) is not None
        ]

        if numeric_series:
            values = [item["value"] for item in numeric_series]
            key_points.append(
                f"The primary numeric column is '{primary_numeric}' with values ranging from {min(values):,.0f} to {max(values):,.0f}."
            )

            if label_columns:
                primary_label = label_columns[0]
                max_item = max(numeric_series, key=lambda item: item["value"])
                min_item = min(numeric_series, key=lambda item: item["value"])
                key_points.append(
                    f"The highest value appears at '{max_item['row'].get(primary_label)}' ({max_item['value']:,.0f}) and the lowest at '{min_item['row'].get(primary_label)}' ({min_item['value']:,.0f})."
                )

            if len(numeric_series) >= 2:
                first_value = numeric_series[0]["value"]
                last_value = numeric_series[-1]["value"]
                change = last_value - first_value
                direction = "increased" if change > 0 else "decreased" if change < 0 else "stayed flat"
                if direction == "stayed flat":
                    key_points.append(
                        f"From the first to the last plotted point, '{primary_numeric}' stayed flat at about {last_value:,.0f}."
                    )
                else:
                    key_points.append(
                        f"From the first to the last plotted point, '{primary_numeric}' {direction} by {abs(change):,.0f}."
                    )

                transitions = []
                series_values = [item["value"] for item in numeric_series]
                for previous, current in zip(series_values, series_values[1:]):
                    delta = current - previous
                    if delta > 0:
                        transitions.append("up")
                    elif delta < 0:
                        transitions.append("down")
                    else:
                        transitions.append("flat")

                unique_transitions = set(transitions)
                if unique_transitions <= {"up"}:
                    key_points.append("The series rises steadily across the plotted points.")
                elif unique_transitions <= {"down"}:
                    key_points.append("The series falls steadily across the plotted points.")
                elif "up" in unique_transitions and "down" in unique_transitions:
                    key_points.append("The series fluctuates, with both rises and dips across the plotted points.")

    return {
        "question": question,
        "row_count": len(data),
        "numeric_columns": numeric_columns,
        "label_columns": label_columns,
        "key_points": key_points,
        "data_preview": data[:12],
    }
