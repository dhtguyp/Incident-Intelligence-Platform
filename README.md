# AI SRE — Incident Intelligence Platform

An full-stack **AI-assisted incident investigation platform** that helps SREs and software engineers investigate production incidents by combining structured operational data (SQLite) with unstructured operational knowledge (Qdrant vector database) and LLM reasoning (Gemini).

---

## 🏗️ Architecture Overview

```text
                         ┌──────────────────┐
                         │    React UI      │
                         │    (Mantine)     │
                         └────────┬─────────┘
                                  │ HTTP / JSON
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │  (Python 3.12)   │
                         └───────┬──────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐    ┌──────────────┐   ┌──────────────┐
       │   SQLite    │    │    Qdrant    │   │  Gemini AI   │
       │             │    │              │   │              │
       │ incidents   │    │ embeddings   │   │ investigation│
       │ services    │    │ runbooks     │   │ synthesis    │
       │ deployments │    │ postmortems  │   │              │
       │ events      │    │ logs         │   │              │
       └─────────────┘    └──────────────┘   └──────────────┘
```

---

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, Vite, Mantine UI
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, `uv` package manager
- **Databases**:
  - **SQLite**: Structured operational metadata (incidents, services, events, deployments, metrics)
  - **Qdrant**: Vector storage for unstructured knowledge chunks (runbooks, logs, postmortems)
- **AI / LLM**: Google Gemini API (`gemini-1.5-flash` / `gemini-embedding-001`)
- **Deployment**: Docker & Docker Compose (Multi-stage build)

---

## 🚀 Quickstart & Running

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/)
- A Gemini API Key from Google AI Studio (`GEMINI_API_KEY`)

### 1. Set Environment Variables

Create a `.env` file or export your Gemini API key:

```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

### 2. Launch the Platform

Build and start the services using Docker Compose:

```bash
docker compose up -d --build
```

This starts:
1. `app`: The unified container running the FastAPI backend and serving the compiled React frontend static assets on port `8000`.
2. `qdrant`: The vector database running on ports `6333` (REST) and `6334` (gRPC).

### 3. Access Services

- 🌐 **Web Interface**: [http://localhost:8000/](http://localhost:8000/)
- 📡 **API Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- 📊 **Qdrant Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## 🧪 Testing

Run backend unit tests inside the running Docker container:

```bash
docker compose exec app uv run pytest tests/
```

---

## 📂 Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routes & endpoints
│   │   ├── llm/            # LLM provider abstractions & prompt templates
│   │   ├── models/         # SQLAlchemy DB models & Pydantic response schemas
│   │   ├── repositories/   # Data access queries & DB interactions
│   │   ├── retrieval/      # Hybrid retrieval context builder
│   │   ├── services/       # Core business logic & investigation orchestration
│   │   ├── database.py     # SQLAlchemy engine & session management
│   │   ├── main.py         # FastAPI application entrypoint & static file mount
│   │   └── seed.py         # Synthetic dataset generator & DB seeder
│   ├── tests/              # Pytest suite
│   ├── pyproject.toml      # Python dependencies (managed via uv)
│   └── uv.lock             # Dependency lockfile
├── frontend/
│   ├── src/                # React TypeScript components & views
│   └── package.json        # Frontend dependencies (Mantine, React)
├── data/                   # SQLite database storage directory (`app.db`)
├── Dockerfile              # Multi-stage Docker build (Node + Python)
├── docker-compose.yml      # Orchestrates app and qdrant services
├── PLAN.md                 # Complete project roadmap & requirements
└── implementation_step_*.md # Educational step-by-step guides
```

---

## 📡 Available API Endpoints (Current Progress)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status check |
| `POST` | `/api/search` | Semantic search over indexed operational knowledge with optional service and document-type filters |
| `GET` | `/api/incidents` | List all incidents with affected services |
| `GET` | `/api/incidents/{incident_id}` | Get metadata for a specific incident |
| `GET` | `/api/incidents/{incident_id}/timeline` | Get chronological event, deployment, and metric evidence for an incident |
