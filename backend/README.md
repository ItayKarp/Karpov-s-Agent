<div align="center">

# AI Chat API

![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1.2-121212?style=for-the-badge&logo=chainlink&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4.1-412991?style=for-the-badge&logo=openai&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cloud-DC382D?style=for-the-badge&logo=redis&logoColor=white)

A production-ready, multi-agent AI chat backend with real-time streaming, persistent memory, and intelligent query routing.

</div>

---

## Features

- **Dual-Agent Orchestration** — An intent classifier routes each query to either a basic or advanced agent based on complexity
- **Streaming Responses** — Real-time token streaming with visible chain-of-thought reasoning
- **Persistent Chat History** — Conversations stored in MongoDB with LLM-generated titles
- **Cross-Session Memory** — Mem0 integration remembers user preferences and context across sessions
- **Web Search & Academic Papers** — Tavily search and arXiv MCP server for research-oriented queries
- **JWT Authentication** — RSA-512 signed access/refresh token flow with rate limiting
- **Redis Caching** — Fast recent-message retrieval and refresh token storage

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | FastAPI |
| AI Orchestration | LangChain + LangChain-MCP-Adapters |
| LLM | OpenAI GPT-4.1 / GPT-4.1-nano |
| Database | MongoDB Atlas via Motor (async) |
| Cache | Redis Cloud Labs via redis-py (async) |
| Memory | Mem0 API |
| Search | Tavily |
| Auth | PyJWT (RS512) + bcrypt |
| Validation | Pydantic v2 |
| Package Manager | uv |

---

## Project Structure

```
app/
├── agents/                 # BasicAgent, AdvancedAgent, shared BaseClass
├── orchestrator/           # Intent classifier + agent orchestrator
├── tools/                  # Tavily search, MCP tool registry
├── services/               # Auth service, title generation service
├── api/
│   ├── routers/            # /chat, /auth/*, /chats endpoints
│   ├── dependencies.py     # Dependency injection providers
│   └── auth_dependencies.py
├── infrastructure/
│   ├── db/                 # MongoDB + Redis client managers
│   └── repositories/       # ChatRepository, AuthRepository
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
- RSA key pair in `certs/` for JWT signing

### Installation

```bash
git clone https://github.com/ItayKarp/LangChain-Exercise1.git
cd LangChain-Exercise1
uv sync
```

### Environment Variables

Create a `.env` file in the project root:

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
```

### Run

```bash
fastapi run app/main.py
# or
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
| `POST` | `/chat` | Send a message to the AI (streaming) | Yes |
| `GET` | `/chats` | List all chats for the current user | Yes |
| `GET` | `/chat/{chat_id}` | Retrieve a full chat with messages | Yes |
| `DELETE` | `/chat/{chat_id}` | Delete a chat | Yes |

---

## Architecture Overview

```
Client
  │
  ▼
FastAPI Router
  │
  ▼
Agent Orchestrator
  │
  ├─► Intent Classifier
  │         │
  │         ├─► BasicAgent   — web search, memory tools  (GPT-4.1-nano)
  │         └─► AdvancedAgent — all tools, higher context (GPT-4.1)
  │
  ▼
Chat Repository
  ├─► MongoDB Atlas  (persistent storage)
  └─► Redis          (message cache, token store)
```
