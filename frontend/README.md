# Karpov's Agent

![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat&logo=vite&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-7-CA4245?style=flat&logo=reactrouter&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi&logoColor=white)

A modern AI chat application built with React and powered by a FastAPI backend. Supports real-time streaming responses, persistent chat history, and markdown rendering.

---

## Features

- **Streaming AI responses** — tokens stream in real-time as the model generates them
- **Thinking mode** — displays the model's reasoning process before the response
- **Chat history** — persistent conversations stored server-side, browsable from the sidebar
- **Markdown rendering** — AI responses render with full markdown support (bold, lists, code blocks)
- **Authentication** — JWT-based login, registration, and password reset
- **Auto-scroll** — chat window follows the latest message during streaming

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8 |
| Routing | React Router 7 |
| Markdown | react-markdown |
| Backend | FastAPI (Python) |
| Auth | JWT |

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- Backend server running on `http://localhost:8000`

### Frontend

```bash
npm install
npm run dev
```

### Backend

Refer to the backend repository for setup instructions.

---

## Project Structure

```
src/
├── api/          # API calls (auth, chat)
├── components/   # Chat, ChatList
├── context/      # AuthContext
├── hooks/        # useAuthFetch, useAutoScroll
└── pages/        # Home, Login, Register, ForgotPassword
```

---

## Environment

The app expects the backend to be running at `http://localhost:8000`. Update the base URL in `src/api/` if your backend runs elsewhere.
