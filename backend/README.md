<div align="center">

# AI Chat API

![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-latest-121212?style=for-the-badge&logo=chainlink&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4.1-412991?style=for-the-badge&logo=openai&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cloud-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-FF4785?style=for-the-badge&logo=qdrant&logoColor=white)

A production-ready, multi-agent AI chat backend with real-time streaming, persistent memory, RAG-powered similarity search, and intelligent LangGraph-based query routing.

</div>

---

## Features

- **LangGraph Orchestration** — A stateful `StateGraph` with six nodes (`setup`, `select_tools`, `retrieve_docs`, `basic_agent`, `advanced_agent`, `finalize`) replaces the old linear orchestrator, with full checkpointing via `MemorySaver`
- **Dual Intent Classification** — GPT-5.4-nano runs two parallel classifiers: one routes to BasicAgent or AdvancedAgent based on reasoning power needed; the other decides whether to trigger RAG retrieval
- **Dynamic Tool Selection** — Before each agent run, a fast LLM call picks only the tools relevant to the query from a central tool registry. The agent can also call `request_more_tools` mid-run to expand its own toolset if needed
- **RAG / Similarity Search** — Qdrant vector database stores campus knowledge; relevant documents are retrieved and injected into the agent's context
- **Streaming Responses** — Real-time token streaming via SSE using `graph.astream_events`, with visible chain-of-thought reasoning
- **Persistent Chat History** — Conversations stored in MongoDB with LLM-generated titles and Redis caching
- **Cross-Session Memory** — Mem0 integration extracts and retrieves long-term user facts across sessions
- **Web Search & Academic Papers** — Tavily search, arXiv MCP server, and fetch MCP server available via dynamic tool selection
- **JWT Authentication** — RSA-512 signed access/refresh token flow with rate limiting
- **LangSmith Tracing** — Full observability of every graph run, node transition, LLM call, and tool invocation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | FastAPI |
| AI Orchestration | LangGraph StateGraph + LangChain-MCP-Adapters |
| LLM | OpenAI GPT-5.4 / GPT-5.4-nano |
| Vector Search | Qdrant (async) + OpenAI Embeddings |
| Database | MongoDB Atlas via Motor (async) |
| Cache | Redis Cloud Labs via redis-py (async) |
| Memory | Mem0 API |
| Search | Tavily |
| Observability | LangSmith |
| Auth | PyJWT (RS512) + bcrypt |
| Validation | Pydantic v2 |
| Package Manager | uv |

---

## Project Structure

```
app/
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
│   ├── dependencies.py     # Dependency injection providers
│   └── auth_dependencies.py
├── infrastructure/
│   ├── db/                 # MongoDB, Redis, Mem0, Qdrant client managers
│   └── repositories/       # ChatRepository, AuthRepository, QdrantRepository
├── core/                   # App config, lifespan, MCP setup
└── models/                 # Pydantic schemas & DTOs
```

---

## Getting Started

### Prerequisites

- Python 3.14
- [`uv`](https://github.com/astral-sh/uv) package manager
- MongoDB Atlas cluster
- Redis instance
- Qdrant instance (cloud or self-hosted)
- RSA key pair in `certs/` for JWT signing

### Installation

```bash
uv venv
source .venv/bin/activate
uv sync
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

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

### Run

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## API Reference

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| `POST` | `/auth/register` | Register a new user | No |
| `POST` | `/auth/login` | Login and receive tokens | No |
| `POST` | `/auth/refresh` | Refresh access token | No |
| `POST` | `/chat` | Send a message to the AI (streaming SSE) | Yes |
| `GET` | `/chats` | List all chats for the current user | Yes |
| `GET` | `/chat/{chat_id}` | Retrieve a full chat with messages | Yes |
| `DELETE` | `/chat/{chat_id}` | Delete a chat | Yes |

---

## Architecture Overview

```
START
  └─► setup           (parallel: intent classify + memory retrieve)
        └─► select_tools   (LLM picks relevant tools from registry)
              └─► retrieve_docs  (Qdrant similarity search if needed)
                    ├─► basic_agent    (GPT-5.4-nano, dynamically bound tools)
                    └─► advanced_agent (GPT-5.4, dynamically bound tools)
                          └─► finalize (parallel: LLM title + Mem0 memory update)
                                └─► END
```
