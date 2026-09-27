# Incident Intelligence Platform

A full-stack **AI-assisted incident investigation platform** that helps SREs and software engineers investigate production incidents by combining structured operational data (SQLite) with unstructured operational knowledge (Qdrant vector database) and LLM reasoning (Gemini).

---

## 🏗️ Architecture & Retrieval Overview

```text
                                  ┌──────────────────────────┐
                                  │    React Dashboard UI    │
                                  │   (Mantine / TypeScript) │
                                  └────────────┬─────────────┘
                                               │ HTTP / REST
                                               ▼
                                  ┌──────────────────────────┐
                                  │     FastAPI Backend      │
                                  │  (Python 3.12 / Pydantic)│
                                  └────────────┬─────────────┘
                                               │
               ┌───────────────────────────────┼───────────────────────────────┐
               │                               │                               │
               ▼                               ▼                               ▼
      ┌─────────────────┐             ┌─────────────────┐             ┌─────────────────┐
      │     SQLite      │             │     Qdrant      │             │    Gemini AI    │
      │                 │             │                 │             │                 │
      │ incidents       │             │ embeddings      │             │ prompt reasoning│
      │ services        │             │ runbooks        │             │ grounding check │
      │ deployments     │             │ postmortems     │             │ citations       │
      │ events/metrics  │             │ logs            │             │ output schema   │
      └─────────────────┘             └─────────────────┘             └─────────────────┘
```

### Retrieval System Rationale

1. **SQLite (Structured Retrieval)**:
   - *Why it exists*: Handles deterministic, time-windowed operational queries (e.g. *"What deployments happened within 60 minutes before incident start?"* or *"List all events for checkout-api"*). Vector databases cannot reliably perform SQL joins or timestamp comparisons.
2. **Qdrant (Semantic Retrieval)**:
   - *Why it exists*: Searches written operational knowledge (runbooks, postmortem root cause analyses, system logs, service documentation) by vector similarity (768-dimensional embeddings via `gemini-embedding-001`).
3. **Gemini LLM (Evidence Reasoning Engine)**:
   - *Why it exists*: Synthesizes retrieved structured and semantic evidence into an understandable investigation report (`IncidentAnalysis`). The model reasons **only** over supplied evidence context and cannot invent un-cited facts.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Mantine UI v7, Lucide Icons, Vitest
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Pytest, `uv` package manager
- **Databases**:
  - **SQLite**: Relational DB for structured telemetry and entities
  - **Qdrant**: Vector database for operational document embeddings
- **AI / LLM**: Google Gemini API (`gemini-2.5-flash-lite` / `gemini-embedding-001`)
- **Containerization**: Docker & Docker Compose (Multi-stage build)

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
1. `app`: Multi-stage build running the FastAPI backend and serving the compiled React frontend static assets on port `8000`.
2. `qdrant`: Vector database running on ports `6333` (REST) and `6334` (gRPC).

### 3. Run Knowledge Ingestion

Populate Qdrant with operational runbooks, postmortems, and logs:

```bash
docker compose exec app uv run python -m app.ingestion.index_documents
```

### 4. Access Services

- 🌐 **Web Interface**: [http://localhost:8000/](http://localhost:8000/)
- 📡 **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- 📊 **Qdrant Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## 🔬 Example Incident Investigation

### Scenario: `INC-1042` (Checkout API Elevated Latency)

1. **User Action**: Open dashboard at `http://localhost:8000`, select **`INC-1042`**, and click **Investigate Incident**.
2. **Hybrid Retrieval**:
   - *Structured*: SQLite retrieves `INC-1042` timeline - `deployment v1.8.2` on `checkout-api` at 14:15, `database_connection_exhaustion` event on `postgres-primary` at 14:31, and `connection_count` metric spike to 200.
   - *Semantic*: Qdrant vector search retrieves PostgreSQL runbook chunk explaining connection pool queuing and postmortem on connection leak patterns.
3. **LLM Synthesis**: Gemini processes `InvestigationContext` and produces evidence-grounded JSON analysis:

```json
{
  "summary": "Checkout API experienced latency spikes following deployment v1.8.2 which caused PostgreSQL connection pool exhaustion.",
  "likely_root_cause": "Deployment v1.8.2 introduced unclosed database connections leading to pool exhaustion on postgres-primary.",
  "confidence": 0.88,
  "root_cause_evidence_ids": ["dep-101", "event-203"],
  "timeline": [
    {
      "timestamp": "2026-09-20 14:15",
      "description": "Deployment v1.8.2 released to checkout-api",
      "evidence_ids": ["dep-101"]
    },
    {
      "timestamp": "2026-09-20 14:31",
      "description": "PostgreSQL connection pool exhausted (200/200 connections)",
      "evidence_ids": ["event-203"]
    }
  ],
  "evidence": [
    {
      "evidence_id": "dep-101",
      "description": "Deployment record for checkout-api v1.8.2"
    },
    {
      "evidence_id": "event-203",
      "description": "Critical event: database_connection_exhaustion on postgres-primary"
    }
  ],
  "related_incidents": ["INC-1017"],
  "uncertainties": ["Exact commit author and code diff could not be verified from current telemetry."]
}
```

---

## 🧪 Testing

Run backend (Pytest) and frontend (Vitest) test suites cleanly using Docker:

```bash
# Run all tests (19 backend + 7 frontend)
./test.sh

# Run backend tests only
./test.sh backend

# Run frontend tests only
./test.sh frontend
```

---

## 💡 Key Architectural Design Decisions

1. **Why SQLite for Telemetry & Metadata?**
   - Relational DBs excel at time-window queries, exact foreign key joins (`Service -> Deployment -> Event`), and structured status filters.
2. **Why Qdrant for Written Knowledge?**
   - Vector search enables semantic retrieval across runbooks, logs, and postmortems when exact keyword error strings are unknown or phrased differently.
3. **Why Hybrid Retrieval over Vector-Only Storage?**
   - Storing telemetry in vector databases makes exact time ranges and relationship joins unreliable. Hybrid retrieval keeps structured facts deterministic and uses vector search purely for conceptual knowledge.
4. **Why Strict Evidence Grounding & Citations?**
   - SREs require verifiable proof. The backend validates that every evidence ID cited in the LLM analysis exists in the retrieved context, eliminating AI hallucinations.

---

## 📈 How I Would Scale This (Production Blueprint)

If scaling this POC to a production monitoring system, I would evolve the architecture as follows:

1. **Relational Database**:
   - Migrate SQLite to **PostgreSQL** with **TimescaleDB** extension for high-throughput time-series metric and event ingestion.
2. **Distributed Vector Database**:
   - Run a multi-node **Qdrant Cluster** (or Milvus / Pinecone) with payload indexing on `service_id` and `environment`.
3. **Asynchronous Ingestion Pipeline**:
   - Replace synchronous file indexing with **Kafka** or **RabbitMQ** event streams for real-time log chunking and document indexing.
4. **Horizontal API Scaling**:
   - Deploy FastAPI application pods behind an **Nginx** / **AWS ALB** load balancer in **Kubernetes (EKS/GKE)**.
5. **Caching & Rate Limiting**:
   - Add a **Redis** cache layer for LLM prompt/embedding caching and incident context memoization.
6. **Telemetry & Tracing**:
   - Integrate **OpenTelemetry (OTel)** collectors for distributed tracing across microservices.

---

## 📂 Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routes & endpoints (incidents, search)
│   │   ├── llm/            # LLM provider interface, prompt templates & validation
│   │   ├── models/         # SQLAlchemy ORM models & Pydantic response schemas
│   │   ├── repositories/   # Relational data access layer & timeline queries
│   │   ├── retrieval/      # Hybrid retrieval context builder & semantic search
│   │   ├── services/       # Incident investigation orchestration logic
│   │   ├── database.py     # SQLAlchemy engine & session management
│   │   ├── main.py         # FastAPI application entrypoint & static mounting
│   │   └── seed.py         # Synthetic causal-chain dataset generator
│   ├── knowledge/          # Synthetic operational corpus (runbooks, postmortems, logs)
│   ├── tests/              # Pytest suite (19 unit & integration tests)
│   ├── pyproject.toml      # Backend dependencies (uv)
│   └── uv.lock             # Lockfile
├── frontend/
│   ├── src/                # React components (IncidentList, Timeline, InvestigationPanel)
│   │   ├── components/     # Mantine UI components
│   │   ├── test/           # Vitest setup and unit tests
│   │   └── types.ts        # TypeScript interfaces matching API schemas
│   └── package.json        # Frontend dependencies & Vitest scripts
├── data/                   # Mounted volume for SQLite storage (`app.db`)
├── Dockerfile              # Multi-stage Docker build (node:20-alpine + python:3.12-slim)
├── docker-compose.yml      # Orchestrates app and qdrant services
├── test.sh                 # Unified test runner script
```

---

## 📡 Available API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status check |
| `POST` | `/api/search` | Semantic search over Qdrant knowledge base |
| `GET` | `/api/incidents` | List all production incidents |
| `GET` | `/api/incidents/{incident_id}` | Get metadata for a specific incident |
| `GET` | `/api/incidents/{incident_id}/timeline` | Get chronological telemetry timeline for an incident |
| `POST` | `/api/incidents/{incident_id}/investigate` | Run full hybrid retrieval + Gemini LLM investigation pipeline |
