# Frammer User-Side NL2SQL Chatbot

This is a cloned user-side version of the admin chatbot.
Frontend and backend flow remain the same, but the database is now built from
only these two CSVs:

- `combined_data(2025-3-1-2026-2-28) by user.csv`
- `combined_data(2025-3-1-2026-2-28) by channel and user.csv`

## What Changed in This User-Side Clone

- Separate folder: `ChatBot_user_side`
- Separate DB path: `chatbot_user_side.duckdb`
- OBT builder (`create_duckdb_schema.py`) now loads only the 2 CSVs above
- SQL prompting and few-shot examples are constrained to user-side schema only

## Active Schema

The chatbot uses one table:

- `aggregate_metrics_obt`

Supported `metric_focus` values:

- `By User`
- `By Channel and User`

Important columns:

- `channel_name`
- `user_name`
- `uploaded_count`
- `created_count`
- `published_count`
- `uploaded_duration_seconds`
- `created_duration_seconds`
- `published_duration_seconds`
- `time_period` (currently `Overall`)

## Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables (copy from `.env.example` if needed):

```env
GROQ_API_KEY=your_key_here
DB_PATH=chatbot_user_side.duckdb
```

3. Build the DuckDB from the two user-side CSVs:

```bash
python create_duckdb_schema.py
```

4. Optional: rebuild user-side Chroma few-shot store:

```bash
python chroma_db.py
```

5. Frontend setup:

```bash
cd frontend
npm install
cd ..
```

## Run

Backend:

```bash
uvicorn api:app --reload
```

Frontend:

```bash
cd frontend
npm start
```

Terminal chatbot:

```bash
python chatbot.py
```

## Notes

- Admin project remains unchanged in `ChatBot/`.
- This user-side clone answers only from the two attached CSV-derived schema.
- Unsupported asks (video-level details, platform-level breakdown, monthly trends, revenue/sales, etc.) are intentionally rejected.
