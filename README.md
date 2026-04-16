<div align="center">

<a href="https://github.com/ItayKarp/Dual-agent">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=3000&pause=1000&color=61DAFB&center=true&vCenter=true&width=600&lines=Karpov's+Agent;LangGraph+AI+Orchestration;RAG+%2B+Similarity+Search;Real-time+Streaming+Responses;Cross-Session+Memory+%26+Web+Search" alt="Typing SVG" />
</a>

<br/>

![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-latest-121212?style=for-the-badge&logo=chainlink&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.4-412991?style=for-the-badge&logo=openai&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cloud-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-FF4785?style=for-the-badge&logo=qdrant&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

A full-stack AI chat application with a React frontend and a multi-agent FastAPI backend.
Features real-time streaming, persistent chat history, RAG-powered similarity search, cross-session memory, and intelligent LangGraph-based query routing.

<br/>

![Demonstration](docs/demonstration.gif)
<br/>
![Demonstration](docs/chats-demonstration.gif)

</div>

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)

---

## Features

| | Feature | Description |
|---|---|---|
| 🔀 | **LangGraph Orchestration** | A stateful `StateGraph` with six nodes — `setup`, `select_tools`, `retrieve_docs`, `basic_agent`, `advanced_agent`, and `finalize` — replaces the old linear orchestrator. Each request flows through the graph with full checkpointing via `MemorySaver`. |
| 🔍 | **Dual Intent Classification** | GPT-5.4-nano runs two parallel classifiers: one routes to BasicAgent or AdvancedAgent based on reasoning power needed; the other decides whether to trigger RAG retrieval from the campus knowledge base. |
| 🔧 | **Dynamic Tool Selection** | Before each agent run, a fast LLM call picks only the tools relevant to the query from a central tool registry. The agent can also call `request_more_tools` mid-run to expand its own toolset if needed. |
| 📚 | **RAG / Similarity Search** | Qdrant vector database stores campus knowledge (grading, financial aid, housing, etc.). On relevant queries, the user's prompt is embedded and the top matching documents are retrieved and injected into the agent's context. |
| ⚡ | **Streaming AI Responses** | Tokens stream in real-time via SSE using `graph.astream_events`. Tool calls and search steps appear as visible chain-of-thought thoughts alongside the response. |
| 💾 | **Persistent Chat History** | Conversations stored in MongoDB with Redis caching and LLM-generated titles. |
| 🧠 | **Cross-Session Memory** | After each response, an LLM extracts long-term user facts via Mem0; relevant memories are semantically retrieved and injected into every new prompt. |
| 🌐 | **Web Search & Academic Papers** | Tavily for web search; arXiv MCP server and fetch MCP server available via dynamic tool selection. |
| 🔭 | **LangSmith Tracing** | Full observability of every graph run, node transition, LLM call, and tool invocation via LangSmith. |
| 📝 | **Markdown Rendering** | AI responses render with full markdown support. |
| 🔐 | **JWT Authentication** | RS512-signed access/refresh token flow with bcrypt password hashing and rate limiting. |

---

## Architecture

<img src="docs/agent-architecture.svg" alt="Architecture Diagram" width="100%"/>

### LangGraph Flow

<img src="docs/Langgraph-Diagram.png" alt="LangGraph Diagram" width="100%"/>

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, React Router 7 |
| Markdown | react-markdown |
| Web Framework | FastAPI |
| AI Orchestration | LangGraph StateGraph + LangChain-MCP-Adapters |
| LLM | OpenAI GPT-5.4 / GPT-5.4-nano |
| Vector Search | Qdrant (async) + OpenAI Embeddings |
| Database | MongoDB Atlas via Motor (async) |
| Cache | Redis Cloud Labs via redis-py (async) |
| Memory | Mem0 API |
| Search | Tavily |
| Observability | LangSmith |
| Auth | JWT (RS512) + bcrypt |
| Package Manager | uv (backend), npm (frontend) |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Hosting | AWS EC2 |

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.14
- [`uv`](https://github.com/astral-sh/uv) package manager
- MongoDB Atlas cluster
- Redis instance
- Qdrant instance (cloud or self-hosted)
- RSA key pair in `backend/certs/` for JWT signing

### Backend

```bash
cd backend
uv venv
source .venv/bin/activate
uv sync
```

<details>
<summary><b>Environment variables</b> — use <code>backend/.env.example</code> and rename to .env</summary>

```env
MONGODB_URI=<your-mongodb-atlas-uri>

OPENAI_API_KEY=<your-openai-key>
TAVILY_API_KEY=<your-tavily-key>
MEM0_API_KEY=<your-mem0-key>

REDIS_HOST=<your-redis-host>
REDIS_PORT=<your-redis-port>
REDIS_USER=default
REDIS_PASS=<your-redis-password>

JWT_ALGORITHM=RS512
JWT_PRIVATE_KEY_PATH=./certs/private_key.pem
JWT_PUBLIC_KEY_PATH=./certs/public_key.pem

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_API_KEY=<your-langsmith-api-key>
LANGSMITH_PROJECT="dual-agent-project"

QDRANT_API_KEY=<your-qdrant-api-key>
QDRANT_URL=<your-qdrant-url>
QDRANT_COLLECTION_NAME=<your-collection-name>
QDRANT_EMBEDDING_MODEL=<your-embedding-model>
```

</details>

```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app expects the backend at `http://localhost:8000`. Update the base URL in `src/api/` if needed.

---

## Deployment

### Docker Compose (local)

Make sure Docker is installed, then from the project root:

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | `http://localhost` |
| Backend | `http://localhost:8000` |

The `docker-compose.yaml` at the project root builds both services from their respective Dockerfiles:
- **Frontend** — multi-stage build: Node compiles the Vite app, Nginx serves the static files
- **Backend** — Python 3.14 slim image with `uv` for fast dependency installation

> The backend reads environment variables from `backend/.env`. Copy `backend/.env.example` to `backend/.env` and fill in your values before running.

---

### CI/CD — GitHub Actions (AWS EC2)

The `.github/workflows/deploy.yaml` pipeline runs automatically on every push to `main`:

```
lint ──┐
       ├──► build ──► deploy (+ health check + rollback)
security ──┘
```

| Job | What it does |
|---|---|
| **lint** | Runs `ruff` on the backend and `eslint` on the frontend |
| **security** | Scans Python deps with `pip-audit` and npm deps with `npm audit` |
| **build** | Verifies both Docker images build successfully |
| **deploy** | SSHs into EC2, pulls latest code, rebuilds containers, runs a health check, and auto-rolls back to the previous commit if the health check fails |

#### Required GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `EC2_HOST` | Your EC2 public IP or DNS |
| `EC2_USER` | `ubuntu` (Ubuntu AMI) or `ec2-user` (Amazon Linux) |
| `EC2_SSH_KEY` | Contents of your `.pem` private key file |
| `ENV_FILE` | Full contents of your `backend/.env` file |

#### EC2 prerequisites

- Docker and Docker Compose installed
- Repository cloned at `~/Dual-agent`
- Ports **80** and **8000** open in the EC2 security group

---

## API Reference

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|:----:|
| `POST` | `/auth/register` | Register a new user | — |
| `POST` | `/auth/login` | Login and receive tokens | — |
| `POST` | `/auth/refresh` | Refresh access token | — |
| `POST` | `/chat` | Send a message (streaming SSE) | ✓ |
| `GET` | `/chats` | List all chats for current user | ✓ |
| `GET` | `/chat/{chat_id}` | Retrieve a full chat with messages | ✓ |
| `DELETE` | `/chat/{chat_id}` | Delete a chat | ✓ |

---

## Project Structure

<details>
<summary><b>Frontend</b></summary>

```
frontend/src/
├── api/          # API calls (auth, chat)
├── components/   # Chat, ChatList
├── context/      # AuthContext
├── hooks/        # useAuthFetch, useAutoScroll
└── pages/        # Home, Login, Register, ForgotPassword
```

</details>

<details>
<summary><b>Backend</b></summary>

```
backend/app/
├── agents/
│   ├── graph/              # LangGraph: state, nodes, edges, graph builder
│   ├── basic_agent.py      # Lightweight agent (GPT-5.4-nano) with dynamic tool access
│   ├── advanced_agent.py   # Powerful agent (GPT-5.4) with dynamic tool access
│   └── base_class.py       # Shared agent base (dynamic tool binding at execute time)
├── orchestrator/           # AgentOrchestrator (entry point for requests)
├── tools/                  # Tool registry, search tools, and request_more_tools meta-tool
├── services/
│   ├── intent_classifier_service.py  # Dual classifier (mode + retrieval routing)
│   ├── streaming_service.py          # SSE stream via graph.astream_events
│   ├── memory_service.py             # Mem0 memory extraction
│   └── title_service.py              # LLM-generated chat titles
├── api/
│   ├── routers/            # /chat, /auth/*, /chats endpoints
│   ├── dependencies.py     # Dependency injection (graph, services, repos)
│   └── auth_dependencies.py
├── infrastructure/
│   ├── db/                 # MongoDB, Redis, Mem0, Qdrant client managers
│   └── repositories/       # ChatRepository, AuthRepository, QdrantRepository
├── core/                   # App config, lifespan, MCP setup
└── models/                 # Pydantic schemas & DTOs
```

</details>
