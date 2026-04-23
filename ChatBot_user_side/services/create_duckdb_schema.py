import os
import sys

import duckdb
import pandas as pd
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHATBOT_USER_ROOT = os.path.dirname(BASE_DIR)
USER_CORE_DIR = os.path.join(CHATBOT_USER_ROOT, "core")
if USER_CORE_DIR not in sys.path:
    sys.path.insert(0, USER_CORE_DIR)

from env_loader import load_project_env

load_project_env()

PROJECT_ROOT = os.path.dirname(CHATBOT_USER_ROOT)
USER_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "user")


def _data_file(name: str) -> str:
    return os.path.join(USER_DATA_DIR, name)


BY_USER_CSV = os.getenv(
    "USER_BY_USER_CSV",
    _data_file("combined_data(2025-3-1-2026-2-28) by user.csv"),
)
BY_CHANNEL_USER_CSV = os.getenv(
    "USER_BY_CHANNEL_USER_CSV",
    _data_file("combined_data(2025-3-1-2026-2-28) by channel and user.csv"),
)
DB_PATH = os.getenv("USER_DB_PATH", _data_file("chatbot_user_side.duckdb"))
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, DB_PATH)


def _safe_int(value) -> int:
    if pd.isna(value):
        return 0
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        return 0


def _time_to_seconds(time_str) -> int:
    """Convert hh:mm:ss or mm:ss strings to integer seconds."""
    if pd.isna(time_str):
        return 0

    text = str(time_str).strip()
    if not text:
        return 0

    parts = text.split(":")
    try:
        if len(parts) == 3:
            hours, minutes, seconds = [int(float(p)) for p in parts]
            return hours * 3600 + minutes * 60 + seconds
        if len(parts) == 2:
            minutes, seconds = [int(float(p)) for p in parts]
            return minutes * 60 + seconds
    except ValueError:
        return 0

    return 0


def _process_file(
    df: pd.DataFrame,
    metric_focus: str,
    user_column: str,
    channel_column: str | None = None,
) -> list[dict]:
    rows: list[dict] = []
    df.columns = [col.strip() for col in df.columns]

    for _, row in df.iterrows():
        rows.append(
            {
                "metric_focus": metric_focus,
                "time_period": "Overall",
                "channel_name": row.get(channel_column) if channel_column else None,
                "user_name": row.get(user_column),
                "content_category": None,
                "uploaded_count": _safe_int(row.get("Uploaded Count")),
                "created_count": _safe_int(row.get("Created Count")),
                "published_count": _safe_int(row.get("Published Count")),
                "uploaded_duration_seconds": _time_to_seconds(
                    row.get("Uploaded Duration (hh:mm:ss)")
                ),
                "created_duration_seconds": _time_to_seconds(
                    row.get("Created Duration (hh:mm:ss)")
                ),
                "published_duration_seconds": _time_to_seconds(
                    row.get("Published Duration (hh:mm:ss)")
                ),
            }
        )
    return rows


def build_duckdb() -> None:
    obt_rows: list[dict] = []

    by_user_df = pd.read_csv(BY_USER_CSV)
    obt_rows.extend(
        _process_file(
            by_user_df,
            metric_focus="By User",
            user_column="User",
        )
    )

    by_channel_user_df = pd.read_csv(BY_CHANNEL_USER_CSV)
    obt_rows.extend(
        _process_file(
            by_channel_user_df,
            metric_focus="By Channel and User",
            user_column="User",
            channel_column="Channel",
        )
    )

    aggregate_df = pd.DataFrame(obt_rows)
    con = duckdb.connect(database=DB_PATH)
    con.execute("DROP TABLE IF EXISTS aggregate_metrics_obt")
    con.execute("DROP TABLE IF EXISTS video_details")

    temp_csv = "temp_aggregate_metrics_obt.csv"
    aggregate_df.to_csv(temp_csv, index=False)
    try:
        con.execute(
            f"CREATE TABLE aggregate_metrics_obt AS SELECT * FROM read_csv_auto('{temp_csv}')"
        )
        print(
            "Created table 'aggregate_metrics_obt' with "
            f"{len(aggregate_df)} rows from 2 CSV files."
        )
        print("Metric focus breakdown:")
        print(aggregate_df["metric_focus"].value_counts().to_string())
    finally:
        con.close()
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

    print(f"Successfully created DuckDB database at: {DB_PATH}")


if __name__ == "__main__":
    build_duckdb()
