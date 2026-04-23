# Frammer Analytics NL2SQL Chatbot

This project builds an intelligent analytics chatbot for content platforms, enabling users to extract actionable insights from complex dashboard data using natural language.

Traditional dashboards capture large volumes of data but fail to help users identify inefficiencies and key decision points. This system bridges that gap by combining NL2SQL, KPI discovery, and conversational analytics.

The system transforms static dashboards into an interactive, insight-driven interface that helps users:
- Identify content pipeline inefficiencies
- Analyze drop-offs across stages (upload → publish)
- Discover high-impact KPIs dynamically

## Problem Statement

Existing analytics dashboards provide extensive data but lack intuitive ways to:
- Navigate insights across the content lifecycle
- Identify inefficiencies and drop-offs
- Support decision-making in real time

Users often struggle to connect fragmented metrics, leading to underutilized data and poor content optimization.

## Key Insights Enabled

- Identified ~99% drop-off between content creation and publishing
- Detected large volumes of unused content (~14,000+ items)
- Measured AI efficiency using Input-to-Output Expansion Multiplier (IOEM)
- Analyzed user publishing effectiveness using UPES metric
- Evaluated platform and language distribution gaps (PDBS, LCR)

## System Architecture

- Intent Router → routes user queries
- SQL Agent → generates and executes queries
- KPI Discovery Agent → suggests relevant metrics
- Plotting Agent → generates visualizations
- Insights Agent → produces final interpretations

Built on:
- One Big Table (OBT) schema for efficient querying
- RAG pipeline for contextual retrieval

## Key Features

- **Conversational NL2SQL Engine:** Converts natural language queries into SQL, executes them on structured data, and returns results in real time.

- **Multi-Agent Architecture:** Modular system with specialized agents:
  - SQL Agent for query generation and execution  
  - KPI Discovery Agent for identifying relevant metrics  
  - Plotting Agent for visualizations  
  - Insights Agent for generating interpretative summaries  

- **RAG-Enhanced Intelligence:** 
  - Dynamic few-shot retrieval for improved NL→SQL accuracy  
  - Document-based RAG for contextual KPI understanding  

- **Conversational Analytics:** Enables users to explore data, generate insights, and visualize trends through a single query interface.

- **KPI-Driven Insight Framework:** Designed and integrated custom metrics to capture inefficiencies across the content lifecycle (e.g., drop-offs, performance gaps).

- **Automated Visualization:** Generates charts (trend lines, comparisons, distributions) directly from user queries.

- **Role-Based System (Admin & User):** Separate workflows and capabilities for administrative analytics and end-user interaction.

- **Production-Ready Deployment:** Fully containerized using Docker for scalable and reproducible deployment.

##  Tech Stack

- Backend: FastAPI, Python
- AI/LLM: Groq, LangChain
- Vector DB: ChromaDB, Qdrant
- Database: DuckDB, PostgreSQL, SQLAlchemy
- Data Processing: Pandas, NumPy
- Visualization: Matplotlib, Seaborn
- Frontend: React

## Project Structure

- **`api.py` (root):** The main FastAPI application that combines the admin and user backends.
- **`admin_backend/`:** Contains the backend code for the admin-facing features.
    - **`agents/`:**  Contains specialized agents for tasks like plotting, KPI discovery, and chart insights.
    - **`core/`:**  The core logic of the admin backend, including the chatbot, database connections, and intent classification.
    - **`services/`:**  Provides services like database schema creation and KPI injection.
- **`ChatBot_user_side/`:** Contains the backend code for the user-facing chatbot. It has a similar structure to the `admin_backend`.
- **`data/`:**  Contains the data used by the application, separated into `admin` and `user` folders.
- **`frontend-figma-skills/`:** contains the frontend code for the application.
- **`docker-compose.yml`:**  Defines the services, networks, and volumes for a multi-container Docker application.
- **`requirements.txt`:**  Lists the Python dependencies for the project.
- **`run_all_initializers.py`:** A script to run all initializers.

## Environment

Create `.env` from `.env.example` and set at least:

```env
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_tavily_api_key_here
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_here
DATABASE_URL="postgresql://user:password@hostname/dbname?sslmode=require&channel_binding=require"
ADMIN_DB_PATH=data/admin/frammer_analytics.duckdb
USER_DB_PATH=data/user/chatbot_user_side.duckdb
PORT=5000
```

## Local Run

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Initialize admin+user data stores:

```bash
python run_all_initializers.py
```

3) Start backend:

```bash
uvicorn api:app --reload
```

4) Start frontend (new terminal):

```bash
cd frontend-figma-skills/ops-dashboard
npm install
npm run dev
```

## API Endpoints

- Admin
  - `GET /api/admin/health`
  - `POST /api/admin/chat`
  - `POST /api/admin/chat/stream`
- User
  - `GET /api/user/health`
  - `GET /api/user/users`
  - `POST /api/user/chat`
  - `POST /api/user/chat/stream`

## Docker

Use one command:

```bash
docker compose up --build
```

Services:

- `qdrant`
- `init-data` (runs `python run_all_initializers.py`)
- `backend` (runs `uvicorn api:app --host 0.0.0.0 --port 8000`)

## Quick Checks

- `http://localhost:8000/api/admin/health`
- `http://localhost:8000/api/user/health`
- `http://localhost:8000/api/user/users`

## Example

### Query 1: Trend Analysis

**User Query:**
"Generate a line chart showing the month-by-month uploaded count vs published count for the entire organization"

**System Output:**
- Automatically generates SQL query
- Produces a time-series visualization comparing uploaded vs published content
- Provides a natural language summary of trends

**Insight:**
- Identifies growth patterns and gaps between content creation and publishing
- Highlights peak months and overall trend progression

---

### Query 2: KPI Discovery

**User Query:**
"Suggest 3 KPIs to measure the overall efficiency of our video production pipeline from upload to publish"

**System Output:**
- Recommends relevant KPIs (e.g., Editorial Throughput Ratio)
- Provides mathematical definitions and formulas
- Explains business relevance of each metric

**Example KPI:**
- **Editorial Throughput Ratio (ETR)**  
  Measures how efficiently uploaded content gets published  
  `ETR = (Published Count / Uploaded Count) × 100`

---

### End-to-End Capability

A single query can:
- Generate SQL
- Retrieve data
- Create visualizations
- Provide insights
- Suggest KPIs with explanations

## My Contributions

- **RAG & Few-Shot Retrieval Pipeline:** Built vector-based retrieval using ChromaDB to dynamically select relevant NL→SQL examples, improving prompt grounding and query accuracy. Contributed to document-level RAG for KPI knowledge retrieval.

- **One Big Table (OBT) Data Modeling:** Designed and implemented a unified OBT schema (`aggregate_metrics_obt`) to consolidate multiple data sources, eliminating complex joins and enabling faster, more reliable NL2SQL querying.

- **KPI Discovery System:** Developed a dynamic KPI discovery module that identifies and suggests relevant business metrics based on user queries and context.

- **Data Processing & EDA:** Performed data cleaning, standardization, and exploratory data analysis to ensure data quality and uncover key trends, anomalies, and metric behavior for downstream analytics.

- **Reporting & Presentation:** Authored the final project report and co-presented system architecture, insights, and outcomes.
