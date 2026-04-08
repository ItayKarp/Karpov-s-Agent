<div align="center">

<a href="https://github.com/ItayKarp/Dual-agent">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=3000&pause=1000&color=61DAFB&center=true&vCenter=true&width=600&lines=Karpov's+Agent;Dual-Agent+AI+Orchestration;Real-time+Streaming+Responses;Cross-Session+Memory+%26+Web+Search" alt="Typing SVG" />
</a>

<br/>

![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1.2-121212?style=for-the-badge&logo=chainlink&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4.1-412991?style=for-the-badge&logo=openai&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cloud-DC382D?style=for-the-badge&logo=redis&logoColor=white)

A full-stack AI chat application with a React frontend and a multi-agent FastAPI backend.
Features real-time streaming, persistent chat history, cross-session memory, and intelligent query routing.

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
- [API Reference](#api-reference)
- [Project Structure](#project-structure)

---

## Features

| | Feature | Description |
|---|---|---|
| 🤖 | **Dual-Agent Orchestration** | Intent classifier routes queries to BasicAgent or AdvancedAgent based on complexity |
| ⚡ | **Streaming AI Responses** | Tokens stream in real-time with visible chain-of-thought reasoning |
| 💾 | **Persistent Chat History** | Conversations stored in MongoDB with LLM-generated titles |
| 🧠 | **Cross-Session Memory** | Mem0 remembers user preferences and context across sessions |
| 🔍 | **Web Search & Academic Papers** | Tavily search and arXiv MCP server for research-oriented queries |
| 📝 | **Markdown Rendering** | AI responses render with full markdown support |
| 🔐 | **JWT Authentication** | RSA-512 signed access/refresh token flow with rate limiting |

---

## Architecture

<img src="docs/Karpovs-agent-architecture.svg" alt="Architecture Diagram" width="100%"/>

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, React Router 7 |
| Markdown | react-markdown |
| Web Framework | FastAPI |
| AI Orchestration | LangChain + LangChain-MCP-Adapters |
| LLM | OpenAI GPT-4.1 / GPT-4.1-nano |
| Database | MongoDB Atlas via Motor (async) |
| Cache | Redis Cloud Labs via redis-py (async) |
| Memory | Mem0 API |
| Search | Tavily |
| Auth | JWT (RS512) + bcrypt |
| Package Manager | uv (backend), npm (frontend) |

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.14
- [`uv`](https://github.com/astral-sh/uv) package manager
- MongoDB Atlas cluster
- Redis instance
- RSA key pair in `backend/certs/` for JWT signing

### Backend

```bash
cd backend
uv sync
```

<details>
<summary><b>Environment variables</b> — create <code>backend/.env</code></summary>

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

</details>

```bash
fastapi run app/main.py
# or
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

</details>
