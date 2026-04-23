"""
create_chroma_db.py
-------------------
Creates a persistent ChromaDB vector store containing 10 dynamic SQL schemas,
each with 5 NL → SQL few-shot examples, for the Frammer analytics DuckDB.

Run once before starting the API:
    python create_chroma_db.py

Output: ./chroma_db/   (persistent ChromaDB directory)
"""

import json
import os
import re

# Chroma's OpenTelemetry dependency chain can still rely on older generated
# protobuf modules, so prefer the Python implementation for compatibility.
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ─────────────────────────────────────────────
# 10 DYNAMIC SCHEMAS  (schema_id → metadata)
# Each schema has:
#   - schema_id   : unique key
#   - description : human-readable purpose
#   - tables      : tables involved
#   - key_filters : important WHERE clauses
#   - examples    : list of {question, sql} dicts (5 per schema)
# ─────────────────────────────────────────────

SCHEMAS = [

    # ── 1. User Performance ──────────────────────────────────────────────────
    {
        "schema_id": "user_performance",
        "description": (
            "Answers questions about individual user activity: how many videos a "
            "user uploaded, created, or published; total durations; comparisons "
            "between users. Uses aggregate_metrics_obt filtered to metric_focus "
            "= 'By User'."
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
                "question": "Show me published video counts for all users.",
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

    # ── 2. Channel Summary ───────────────────────────────────────────────────
    {
        "schema_id": "channel_summary",
        "description": (
            "Answers overall per-channel rollup questions: total uploads, creations, "
            "publications, and durations per channel. Uses aggregate_metrics_obt "
            "filtered to metric_focus = 'Overall Client Summary'."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {"metric_focus": "Overall Client Summary"},
        "examples": [
            {
                "question": "How many videos were uploaded by channel A?",
                "sql": (
                    "SELECT channel_name, uploaded_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Overall Client Summary' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'A';"
                ),
            },
            {
                "question": "Which channel published the most content?",
                "sql": (
                    "SELECT channel_name, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Overall Client Summary' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY published_count DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "Give me a summary of all channels sorted by videos created.",
                "sql": (
                    "SELECT channel_name, uploaded_count, created_count, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Overall Client Summary' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY created_count DESC;"
                ),
            },
            {
                "question": "What is the total created duration in hours for channel B?",
                "sql": (
                    "SELECT channel_name, "
                    "       ROUND(created_duration_seconds / 3600.0, 2) AS created_hours "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Overall Client Summary' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'B';"
                ),
            },
            {
                "question": "How many channels have published at least one video?",
                "sql": (
                    "SELECT COUNT(DISTINCT channel_name) AS active_channels "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Overall Client Summary' "
                    "  AND time_period = 'Overall' "
                    "  AND published_count > 0;"
                ),
            },
        ],
    },

    # ── 3. Platform Distribution ─────────────────────────────────────────────
    {
        "schema_id": "platform_distribution",
        "description": (
            "Answers questions about where content is published across social "
            "platforms (Facebook, Instagram, LinkedIn, Reels, Shorts, X/Twitter, "
            "YouTube, Threads) per channel. Uses metric_focus = 'Channel Platform "
            "Breakdown'."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {"metric_focus": "Channel Platform Breakdown"},
        "examples": [
            {
                "question": "How many videos did channel A publish on YouTube?",
                "sql": (
                    "SELECT channel_name, platform_youtube_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Channel Platform Breakdown' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'A';"
                ),
            },
            {
                "question": "Which channel has the most Instagram publications?",
                "sql": (
                    "SELECT channel_name, platform_instagram_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Channel Platform Breakdown' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY platform_instagram_count DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "Show all platform publish counts for channel I.",
                "sql": (
                    "SELECT channel_name, "
                    "       platform_facebook_count, platform_instagram_count, "
                    "       platform_linkedin_count, platform_reels_count, "
                    "       platform_shorts_count, platform_x_count, "
                    "       platform_youtube_count, platform_threads_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Channel Platform Breakdown' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'I';"
                ),
            },
            {
                "question": "What is the total Facebook publish duration in hours across all channels?",
                "sql": (
                    "SELECT ROUND(SUM(platform_facebook_duration_seconds) / 3600.0, 2) "
                    "       AS total_facebook_hours "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Channel Platform Breakdown' "
                    "  AND time_period = 'Overall';"
                ),
            },
            {
                "question": "List channels that have published on Reels.",
                "sql": (
                    "SELECT channel_name, platform_reels_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Channel Platform Breakdown' "
                    "  AND time_period = 'Overall' "
                    "  AND platform_reels_count > 0 "
                    "ORDER BY platform_reels_count DESC;"
                ),
            },
        ],
    },

    # ── 4. Content Input Type Analysis ───────────────────────────────────────
    {
        "schema_id": "content_input_type",
        "description": (
            "Answers questions about input content categories such as interview, "
            "news bulletin, speech, debate, podcast, drama, sports show, "
            "press conference, in-brief, discussion-show, special reports. "
            "Uses metric_focus = 'By Input Type'."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {"metric_focus": "By Input Type"},
        "examples": [
            {
                "question": "How many interview videos were uploaded overall?",
                "sql": (
                    "SELECT content_category, uploaded_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Input Type' "
                    "  AND time_period = 'Overall' "
                    "  AND content_category = 'interview';"
                ),
            },
            {
                "question": "Which content type was created the most?",
                "sql": (
                    "SELECT content_category, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Input Type' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY created_count DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "Show me all input types ranked by total upload duration.",
                "sql": (
                    "SELECT content_category, "
                    "       ROUND(uploaded_duration_seconds / 3600.0, 2) AS uploaded_hours "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Input Type' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY uploaded_duration_seconds DESC;"
                ),
            },
            {
                "question": "How many news bulletin videos were published?",
                "sql": (
                    "SELECT content_category, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Input Type' "
                    "  AND time_period = 'Overall' "
                    "  AND content_category = 'news bulletin';"
                ),
            },
            {
                "question": "Compare uploaded vs created counts across all input types.",
                "sql": (
                    "SELECT content_category, uploaded_count, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Input Type' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY uploaded_count DESC;"
                ),
            },
        ],
    },

    # ── 5. Content Output Type Analysis ──────────────────────────────────────
    {
        "schema_id": "content_output_type",
        "description": (
            "Answers questions about output formats: Full package, Key moments, "
            "My Key moments, Summary, Chapters. "
            "Uses metric_focus = 'By Output Type'."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {"metric_focus": "By Output Type"},
        "examples": [
            {
                "question": "How many Full package outputs were created?",
                "sql": (
                    "SELECT content_category, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Output Type' "
                    "  AND time_period = 'Overall' "
                    "  AND content_category = 'Full package';"
                ),
            },
            {
                "question": "Which output type has the highest published duration?",
                "sql": (
                    "SELECT content_category, "
                    "       ROUND(published_duration_seconds / 3600.0, 2) AS published_hours "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Output Type' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY published_duration_seconds DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "List all output types by number of creations.",
                "sql": (
                    "SELECT content_category, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Output Type' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY created_count DESC;"
                ),
            },
            {
                "question": "How many Summary outputs were published overall?",
                "sql": (
                    "SELECT content_category, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Output Type' "
                    "  AND time_period = 'Overall' "
                    "  AND content_category = 'Summary';"
                ),
            },
            {
                "question": "Compare Key moments vs My Key moments in terms of created count.",
                "sql": (
                    "SELECT content_category, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Output Type' "
                    "  AND time_period = 'Overall' "
                    "  AND content_category IN ('Key moments', 'My Key moments');"
                ),
            },
        ],
    },

    # ── 6. Language Breakdown ────────────────────────────────────────────────
    {
        "schema_id": "language_breakdown",
        "description": (
            "Answers questions about content distribution by language code "
            "(e.g., en, ar, es, mix). "
            "Uses metric_focus = 'By Language'."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {"metric_focus": "By Language"},
        "examples": [
            {
                "question": "How many videos were created in English?",
                "sql": (
                    "SELECT content_category AS language, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Language' "
                    "  AND time_period = 'Overall' "
                    "  AND content_category = 'en';"
                ),
            },
            {
                "question": "Which language has the highest number of uploads?",
                "sql": (
                    "SELECT content_category AS language, uploaded_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Language' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY uploaded_count DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "Show published counts for all languages.",
                "sql": (
                    "SELECT content_category AS language, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Language' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY published_count DESC;"
                ),
            },
            {
                "question": "What is the total upload duration in hours for Arabic content?",
                "sql": (
                    "SELECT content_category AS language, "
                    "       ROUND(uploaded_duration_seconds / 3600.0, 2) AS uploaded_hours "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Language' "
                    "  AND time_period = 'Overall' "
                    "  AND content_category = 'ar';"
                ),
            },
            {
                "question": "Compare upload and creation counts across all languages.",
                "sql": (
                    "SELECT content_category AS language, uploaded_count, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Language' "
                    "  AND time_period = 'Overall' "
                    "ORDER BY created_count DESC;"
                ),
            },
        ],
    },

    # ── 7. Monthly Trends ────────────────────────────────────────────────────
    {
        "schema_id": "monthly_trends",
        "description": (
            "Answers time-series and trend questions: month-by-month uploads, "
            "creations, and publications across the platform. "
            "Uses metric_focus = 'Monthly Overall'. "
            "time_period format: 'Jan, 2026', 'Dec, 2025', etc."
        ),
        "tables": ["aggregate_metrics_obt"],
        "key_filters": {"metric_focus": "Monthly Overall"},
        "examples": [
            {
                "question": "How many videos were uploaded in January 2026?",
                "sql": (
                    "SELECT time_period, uploaded_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Monthly Overall' "
                    "  AND time_period = 'Jan, 2026';"
                ),
            },
            {
                "question": "Which month had the highest number of creations?",
                "sql": (
                    "SELECT time_period, created_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Monthly Overall' "
                    "ORDER BY created_count DESC "
                    "LIMIT 1;"
                ),
            },
            {
                "question": "Show monthly upload trends for the entire available period.",
                "sql": (
                    "SELECT time_period, uploaded_count, created_count, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Monthly Overall' "
                    "  AND time_period != 'Overall' "
                    "ORDER BY STRPTIME(time_period, '%b, %Y');"
                ),
            },
            {
                "question": "What was the total published duration in hours in December 2025?",
                "sql": (
                    "SELECT time_period, "
                    "       ROUND(published_duration_seconds / 3600.0, 2) AS published_hours "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Monthly Overall' "
                    "  AND time_period = 'Dec, 2025';"
                ),
            },
            {
                "question": "Compare upload counts in October versus November 2025.",
                "sql": (
                    "SELECT time_period, uploaded_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Monthly Overall' "
                    "  AND time_period IN ('Oct, 2025', 'Nov, 2025');"
                ),
            },
        ],
    },

    # ── 8. Channel-User Drilldown ─────────────────────────────────────────────
    {
        "schema_id": "channel_user_drilldown",
        "description": (
            "Answers questions that combine a specific channel AND a specific user: "
            "how much a user contributed within a channel, cross-channel comparisons "
            "for one user, etc. "
            "Uses metric_focus = 'By Channel and User'."
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
                "question": "Show all users and their upload counts for channel I.",
                "sql": (
                    "SELECT user_name, uploaded_count, created_count, published_count "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'I' "
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
                    "  AND published_count > 0;"
                ),
            },
            {
                "question": "Compare created duration in hours for all users in channel H.",
                "sql": (
                    "SELECT user_name, "
                    "       ROUND(created_duration_seconds / 3600.0, 2) AS created_hours "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'By Channel and User' "
                    "  AND time_period = 'Overall' "
                    "  AND channel_name = 'H' "
                    "ORDER BY created_duration_seconds DESC;"
                ),
            },
        ],
    },

    # ── 9. Video Details Lookup ───────────────────────────────────────────────
    {
        "schema_id": "video_details_lookup",
        "description": (
            "Answers questions about individual videos: searching by type, "
            "uploader, team, publication status, or platform. "
            "Uses the video_details table directly."
        ),
        "tables": ["video_details"],
        "key_filters": {},
        "examples": [
            {
                "question": "How many videos of type podcast are in the system?",
                "sql": (
                    "SELECT type, COUNT(*) AS video_count "
                    "FROM video_details "
                    "WHERE type = 'podcast' "
                    "GROUP BY type;"
                ),
            },
            {
                "question": "List all published videos uploaded by Neha.",
                "sql": (
                    "SELECT video_id, headline, type, published_platform, published_url "
                    "FROM video_details "
                    "WHERE uploaded_by = 'Neha' "
                    "  AND is_published = TRUE;"
                ),
            },
            {
                "question": "How many videos have been published across all uploaders?",
                "sql": (
                    "SELECT COUNT(*) AS published_count "
                    "FROM video_details "
                    "WHERE is_published = TRUE;"
                ),
            },
            {
                "question": "Which video types exist and how many of each are there?",
                "sql": (
                    "SELECT type, COUNT(*) AS count "
                    "FROM video_details "
                    "GROUP BY type "
                    "ORDER BY count DESC;"
                ),
            },
            {
                "question": "Show all videos published on Instagram.",
                "sql": (
                    "SELECT video_id, headline, uploaded_by, published_url "
                    "FROM video_details "
                    "WHERE published_platform = 'instagram' "
                    "  AND is_published = TRUE;"
                ),
            },
        ],
    },

    # ── 10. Cross-Metric Comparison ───────────────────────────────────────────
    {
        "schema_id": "cross_metric_comparison",
        "description": (
            "Answers complex multi-dimensional questions that combine user, channel, "
            "time period, or platform filters. Typically joins or unions across "
            "multiple metric_focus values or computes efficiency ratios like "
            "publish rate (published/uploaded) or creation efficiency."
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
                    "WHERE metric_focus = 'Overall Client Summary' "
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
                "question": "Show the monthly trend of upload counts alongside channel A's share.",
                "sql": (
                    "SELECT m.time_period, "
                    "       m.uploaded_count AS total_uploaded, "
                    "       ca.uploaded_count AS channel_a_uploaded "
                    "FROM aggregate_metrics_obt m "
                    "LEFT JOIN aggregate_metrics_obt ca "
                    "  ON ca.metric_focus = 'Overall Client Summary' "
                    "  AND ca.time_period = m.time_period "
                    "  AND ca.channel_name = 'A' "
                    "WHERE m.metric_focus = 'Monthly Overall' "
                    "  AND m.time_period != 'Overall' "
                    "ORDER BY STRPTIME(m.time_period, '%b, %Y');"
                ),
            },
            {
                "question": "Compare total platform publish counts: YouTube vs Instagram vs Facebook.",
                "sql": (
                    "SELECT "
                    "  ROUND(SUM(platform_youtube_count), 0)   AS youtube_total, "
                    "  ROUND(SUM(platform_instagram_count), 0) AS instagram_total, "
                    "  ROUND(SUM(platform_facebook_count), 0)  AS facebook_total "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Channel Platform Breakdown' "
                    "  AND time_period = 'Overall';"
                ),
            },
            {
                "question": "Which month had the highest creation-to-upload efficiency?",
                "sql": (
                    "SELECT time_period, "
                    "       ROUND(created_count / NULLIF(uploaded_count, 0), 2) "
                    "       AS creation_efficiency "
                    "FROM aggregate_metrics_obt "
                    "WHERE metric_focus = 'Monthly Overall' "
                    "  AND time_period != 'Overall' "
                    "ORDER BY creation_efficiency DESC "
                    "LIMIT 1;"
                ),
            },
        ],
    },
]


# ─────────────────────────────────────────────
# BUILD CHROMADB
# ─────────────────────────────────────────────

def build_chroma_db(persist_dir: str = "./chroma_db") -> None:
    print(f"Initialising ChromaDB at '{persist_dir}' …")
    ef = create_embedding_function()

    client = chromadb.PersistentClient(path=persist_dir)

    # Drop old collection if it exists so the script is idempotent
    try:
        client.delete_collection("frammer_fewshots")
        print("  Deleted existing 'frammer_fewshots' collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name="frammer_fewshots",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    docs, metas, ids = [], [], []

    for schema in SCHEMAS:
        for idx, ex in enumerate(schema["examples"]):
            doc_id = f"{schema['schema_id']}__ex{idx}"
            # The document text that gets embedded = natural-language question
            document = ex["question"]
            meta = {
                "schema_id":   schema["schema_id"],
                "description": schema["description"],
                "tables":      json.dumps(schema["tables"]),
                "key_filters": json.dumps(schema["key_filters"]),
                "question":    ex["question"],
                "sql":         ex["sql"],
            }
            docs.append(document)
            metas.append(meta)
            ids.append(doc_id)

    collection.add(documents=docs, metadatas=metas, ids=ids)
    print(f"  Inserted {len(docs)} examples across {len(SCHEMAS)} schemas.")
    print("Done. ChromaDB is ready.")


# ─────────────────────────────────────────────
# RETRIEVAL (used at runtime by chatbot / api)
# ─────────────────────────────────────────────

_collection = None  # lazy singleton


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


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _fallback_examples(question: str, top_k: int = 3) -> list[dict]:
    """Local lexical fallback when vector retrieval is unavailable or stale."""
    question_tokens = _tokenize(question)
    scored_examples: list[tuple[int, dict]] = []

    for schema in SCHEMAS:
        schema_tokens = _tokenize(
            f"{schema['schema_id']} {schema['description']} {json.dumps(schema['key_filters'])}"
        )
        for example in schema["examples"]:
            example_tokens = _tokenize(example["question"])
            overlap = len(question_tokens & (schema_tokens | example_tokens))

            if "month" in question_tokens or "months" in question_tokens:
                if schema["schema_id"] == "monthly_trends":
                    overlap += 4
            if "latest" in question_tokens or "recent" in question_tokens:
                if schema["schema_id"] == "monthly_trends":
                    overlap += 2
            if "channel" in question_tokens and schema["schema_id"] == "channel_summary":
                overlap += 2
            if "user" in question_tokens and schema["schema_id"] == "user_performance":
                overlap += 2
            if "platform" in question_tokens and schema["schema_id"] == "platform_distribution":
                overlap += 2

            scored_examples.append(
                (
                    overlap,
                    {
                        "question": example["question"],
                        "sql": example["sql"],
                    },
                )
            )

    scored_examples.sort(key=lambda item: item[0], reverse=True)
    return [meta for score, meta in scored_examples[:top_k] if score > 0]


def get_chroma_collection(persist_dir: str = "./chroma_db"):
    """Return (or create) the ChromaDB collection for few-shot retrieval."""
    global _collection
    if _collection is not None:
        return _collection

    ef = create_embedding_function()
    client = chromadb.PersistentClient(path=persist_dir)

    try:
        _collection = client.get_collection(
            name="frammer_fewshots", embedding_function=ef
        )
    except Exception:
        # Collection doesn't exist yet – build it first
        print("[ChromaDB] Collection not found. Building it now …")
        build_chroma_db(persist_dir=persist_dir)
        _collection = client.get_collection(
            name="frammer_fewshots", embedding_function=ef
        )

    return _collection


def retrieve_fewshot_examples(question: str, top_k: int = 3) -> str:
    """
    Query ChromaDB for the top-k most similar NL→SQL examples.
    Returns a formatted string ready to be injected into the agent prompt.
    """
    metadatas: list[dict] = []

    try:
        collection = get_chroma_collection()
        results = collection.query(
            query_texts=[question],
            n_results=top_k,
            include=["metadatas", "distances"],
        )
        metadatas = results["metadatas"][0] if results["ids"][0] else []
    except Exception:
        metadatas = []

    if not metadatas:
        metadatas = _fallback_examples(question, top_k=top_k)

    if not metadatas:
        return ""

    lines = [
        "Here are some similar example queries for reference (use them as guidance):\n"
    ]
    for i, meta in enumerate(metadatas):
        lines.append(f"Example {i + 1}:")
        lines.append(f"  Question: {meta['question']}")
        lines.append(f"  SQL:      {meta['sql']}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    build_chroma_db()
