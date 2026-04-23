"""
Few-shot retrieval for the user-side Frammer chatbot.

This module stores and retrieves NL -> SQL examples that are valid for the
user-side schema only:
  - aggregate_metrics_obt (metric_focus in {'By User', 'By Channel and User'})
"""

from __future__ import annotations

import json
import os
import re

# Chroma can pull older OpenTelemetry protobuf code paths; prefer the Python
# implementation for compatibility with newer protobuf packages.
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

COLLECTION_NAME = "chatbot_user_side_fewshots"


SCHEMAS = [
    {
        "schema_id": "user_performance",
        "description": (
            "Questions about totals by user across all channels using "
            "metric_focus = 'By User'."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {"metric_focus": "By User"},
        "examples": [
            {
                "question": "How many videos did Chandan upload in total?",
                "sql": (
                    "SELECT user_name, uploaded_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By User' "
                    "  AND time_period = 'Overall' "
                    "  AND user_name = 'Chandan';"
                ),
            },
            {
                "question": "Which user created the most videos overall?",
                "sql": (
                    "SELECT user_name, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By User' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY created_count DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "Show published video counts for all users.",
                "sql": (
                    "SELECT user_name, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By User' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY published_count DESC;"
                ),
            },
            {
                "question": "What is the total upload duration in hours for Sandeep Belaki?",
                "sql": (
                    "SELECT user_name, "
                    "       ROUND(uploaded_duration_seconds / 3600.0, 2) AS uploaded_hours "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By User' "
                    "  AND time_period = 'Overall' "
                    "  AND user_name = 'Sandeep Belaki';"
                ),
            },
            {
                "question": "List the top 5 users by number of videos created.",
                "sql": (
                    "SELECT user_name, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By User' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY created_count DESC "
                    "LIMIT 5;"
                ),
            },
        ],
    },
    {
        "schema_id": "channel_user_drilldown",
        "description": (
            "Questions about user performance within a specific channel using "
            "metric_focus = 'By Channel and User'."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {"metric_focus": "By Channel and User"},
        "examples": [
            {
                "question": "How many videos did Chandan upload for channel A?",
                "sql": (
                    "SELECT channel_name, user_name, uploaded_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'A' "
                    "  AND user_name = 'Chandan';"
                ),
            },
            {
                "question": "Which user created the most videos in channel B?",
                "sql": (
                    "SELECT channel_name, user_name, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'B' "
                    "ORDER BY created_count DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "Show all users and their published counts for channel C.",
                "sql": (
                    "SELECT user_name, uploaded_count, created_count, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'C' "
                    "ORDER BY published_count DESC;"
                ),
            },
            {
                "question": "Compare uploaded versus created counts by user for channel A.",
                "sql": (
                    "SELECT user_name, uploaded_count, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'A' "
                    "ORDER BY uploaded_count DESC;"
                ),
            },
            {
                "question": "Across which channels did Nitesh publish content?",
                "sql": (
                    "SELECT channel_name, user_name, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND user_name = 'Nitesh' "
                    "  AND published_count > 0 "
                    "ORDER BY channel_name;"
                ),
            },
        ],
    },
    {
        "schema_id": "channel_totals",
        "description": (
            "Questions about channel totals derived by summing users within each channel "
            "from metric_focus = 'By Channel and User'."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {"metric_focus": "By Channel and User"},
        "examples": [
            {
                "question": "What is the total uploaded count for channel A?",
                "sql": (
                    "SELECT channel_name, SUM(uploaded_count) AS total_uploaded_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'A' "
                    "GROUP BY channel_name;"
                ),
            },
            {
                "question": "Which channel has the highest total created count?",
                "sql": (
                    "SELECT channel_name, SUM(created_count) AS total_created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "GROUP BY channel_name "
                    "ORDER BY total_created_count DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "What is total published duration in hours for channel B?",
                "sql": (
                    "SELECT channel_name, "
                    "       ROUND(SUM(published_duration_seconds) / 3600.0, 2) AS published_hours "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'B' "
                    "GROUP BY channel_name;"
                ),
            },
            {
                "question": "Compare total uploads for channels A and B.",
                "sql": (
                    "SELECT channel_name, SUM(uploaded_count) AS total_uploaded_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name IN ('A', 'B') "
                    "GROUP BY channel_name "
                    "ORDER BY total_uploaded_count DESC;"
                ),
            },
            {
                "question": "List all channels ranked by published count.",
                "sql": (
                    "SELECT channel_name, SUM(published_count) AS total_published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "GROUP BY channel_name "
                    "ORDER BY total_published_count DESC;"
                ),
            },
        ],
    },
    {
        "schema_id": "efficiency_metrics",
        "description": (
            "Questions about publish-rate and efficiency style ratios for users/channels."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {},
        "examples": [
            {
                "question": "What percentage of uploaded videos got published overall?",
                "sql": (
                    "SELECT ROUND(100.0 * SUM(published_count) / NULLIF(SUM(uploaded_count), 0), 2) "
                    "       AS publish_rate_pct "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By User' "
                    "  AND time_period = 'Overall';"
                ),
            },
            {
                "question": "Which user has the best publish-to-upload ratio?",
                "sql": (
                    "SELECT user_name, "
                    "       ROUND(100.0 * published_count / NULLIF(uploaded_count, 0), 2) "
                    "       AS publish_rate_pct "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By User' "
                    "  AND time_period = 'Overall' "
                    "  AND uploaded_count > 0 "
                    "ORDER BY publish_rate_pct DESC "
                    "LIMIT 5;"
                ),
            },
            {
                "question": "Which channel has the highest publish rate?",
                "sql": (
                    "SELECT channel_name, "
                    "       ROUND(100.0 * SUM(published_count) / NULLIF(SUM(uploaded_count), 0), 2) "
                    "       AS publish_rate_pct "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "GROUP BY channel_name "
                    "HAVING SUM(uploaded_count) > 0 "
                    "ORDER BY publish_rate_pct DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "Show created-to-upload efficiency for each user.",
                "sql": (
                    "SELECT user_name, "
                    "       ROUND(100.0 * created_count / NULLIF(uploaded_count, 0), 2) "
                    "       AS create_efficiency_pct "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By User' "
                    "  AND time_period = 'Overall' "
                    "  AND uploaded_count > 0 "
                    "ORDER BY create_efficiency_pct DESC;"
                ),
            },
            {
                "question": "Which user has the highest published duration?",
                "sql": (
                    "SELECT user_name, published_duration_seconds "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By User' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY published_duration_seconds DESC "
                    "LIMIT 1;"
                ),
            },
        ],
    },
]


def create_embedding_function():
    """Build the embedding function with a clearer offline/network failure."""
    model_name = os.getenv("CHROMA_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    local_only = os.getenv("CHROMA_EMBEDDING_LOCAL_ONLY", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }

    try:
        return SentenceTransformerEmbeddingFunction(
            model_name=model_name,
            local_files_only=local_only,
        )
    except Exception as exc:
        raise RuntimeError(
            "Failed to load the Chroma embedding model "
            f"'{model_name}'. If this machine cannot reach Hugging Face, "
            "download the model once in a network-enabled environment or set "
            "CHROMA_EMBEDDING_MODEL to a local model path. You can also set "
            "CHROMA_EMBEDDING_LOCAL_ONLY=1 to force offline loading."
        ) from exc


def build_chroma_db(persist_dir: str = "./chatbot_user_side_chroma_db") -> None:
    """Build/rebuild the ChromaDB collection for few-shot retrieval."""
    print(f"Initializing ChromaDB at '{persist_dir}'...")
    ef = create_embedding_function()
    client = chromadb.PersistentClient(path=persist_dir)

    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing '{COLLECTION_NAME}' collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    docs: list[str] = []
    metas: list[dict] = []
    ids: list[str] = []

    for schema in SCHEMAS:
        for idx, example in enumerate(schema["examples"]):
            docs.append(example["question"])
            metas.append(
                {
                    "schema_id": schema["schema_id"],
                    "description": schema["description"],
                    "tables": json.dumps(schema["tables"]),
                    "key_filters": json.dumps(schema["key_filters"]),
                    "question": example["question"],
                    "sql": example["sql"],
                }
            )
            ids.append(f"{schema['schema_id']}__ex{idx}")

    collection.add(documents=docs, metadatas=metas, ids=ids)
    print(f"Inserted {len(docs)} examples across {len(SCHEMAS)} schemas.")
    print("Done. User-side ChromaDB is ready.")


_collection = None


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _fallback_examples(question: str, top_k: int = 3) -> list[dict]:
    """Lexical fallback retrieval if vector search is unavailable."""
    question_tokens = _tokenize(question)
    scored: list[tuple[int, dict]] = []

    for schema in SCHEMAS:
        schema_tokens = _tokenize(
            f"{schema['schema_id']} {schema['description']} {json.dumps(schema['key_filters'])}"
        )
        for example in schema["examples"]:
            example_tokens = _tokenize(example["question"])
            overlap = len(question_tokens & (schema_tokens | example_tokens))

            if "channel" in question_tokens and schema["schema_id"] in {
                "channel_user_drilldown",
                "channel_totals",
            }:
                overlap += 2
            if "user" in question_tokens and schema["schema_id"] == "user_performance":
                overlap += 2
            if {
                "rate",
                "ratio",
                "efficiency",
                "percentage",
                "percent",
            } & question_tokens and schema["schema_id"] == "efficiency_metrics":
                overlap += 3

            scored.append(
                (
                    overlap,
                    {"question": example["question"], "sql": example["sql"]},
                )
            )

    scored.sort(key=lambda item: item[0], reverse=True)
    return [meta for score, meta in scored[:top_k] if score > 0]


def get_chroma_collection(persist_dir: str = "./chatbot_user_side_chroma_db"):
    """Return (or build) the user-side Chroma collection."""
    global _collection
    if _collection is not None:
        return _collection

    ef = create_embedding_function()
    client = chromadb.PersistentClient(path=persist_dir)

    try:
        _collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    except Exception:
        print(f"[ChromaDB] '{COLLECTION_NAME}' not found. Building it now...")
        build_chroma_db(persist_dir=persist_dir)
        _collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)

    return _collection


def retrieve_fewshot_examples(question: str, top_k: int = 3) -> str:
    """
    Retrieve top-k similar NL -> SQL examples and format as prompt context.
    """
    metadatas: list[dict] = []

    try:
        collection = get_chroma_collection()
        results = collection.query(
            query_texts=[question],
            n_results=top_k,
            include=["metadatas", "distances"],
        )
        if results.get("ids") and results["ids"][0]:
            metadatas = results["metadatas"][0]
    except Exception:
        metadatas = []

    if not metadatas:
        metadatas = _fallback_examples(question, top_k=top_k)

    if not metadatas:
        return ""

    lines = ["Here are some similar example queries for reference (use as guidance):\n"]
    for i, meta in enumerate(metadatas, start=1):
        lines.append(f"Example {i}:")
        lines.append(f"  Question: {meta['question']}")
        lines.append(f"  SQL:      {meta['sql']}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    build_chroma_db()
