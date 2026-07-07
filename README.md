# FirstChat — Real-Time Messaging Platform

> A production-grade, full-stack real-time chat application built with modern technologies. Supports one-to-one and group messaging, live presence tracking, and WebSocket-powered instant communication.

![Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)
![Stack](https://img.shields.io/badge/Frontend-React%2018-61DAFB?style=flat-square&logo=react)
![Stack](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=flat-square&logo=postgresql)
![Stack](https://img.shields.io/badge/Cache-Redis-DC382D?style=flat-square&logo=redis)
![Stack](https://img.shields.io/badge/Deployed-Railway%20%2B%20Vercel-black?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Live Demo

| Service | URL |
|---|---|
| 🌐 Frontend | https://chatapplication-git-main-sujitapatel786-7035s-projects.vercel.app |
| 📡 Backend API | https://chatapplication-production-ee70.up.railway.app/api/v1 |
| 📖 API Docs | https://chatapplication-production-ee70.up.railway.app/api/docs |

---

## Overview

FirstChat is a scalable, real-time messaging platform designed with clean architecture principles. It delivers instant messaging between users through persistent WebSocket connections, with automatic reconnection, live presence indicators, and a modern WhatsApp-inspired interface.

Built as a commercial-grade SaaS foundation — the codebase is structured to support feature extensions, multi-tenancy, and horizontal scaling without architectural changes.

---

## Key Features

### Messaging
- ✅ One-to-one direct messaging
- ✅ Group chat with multiple participants
- ✅ Real-time message delivery via WebSockets
- ✅ Edit message
- ✅ Delete message — for self or for everyone
- ✅ Message history with cursor-based pagination

### Users & Authentication
- ✅ Secure registration and login
- ✅ JWT access tokens + refresh token rotation
- ✅ User profile with display name and bio
- ✅ User search by username

### Real-Time
- ✅ Typing indicators
- ✅ Online / offline presence
- ✅ Instant message push to all chat members
- ✅ Auto-reconnect with exponential backoff (up to 5 retries)
- ✅ Live presence broadcast across all connected users

### Infrastructure
- ✅ Fully containerised with Docker
- ✅ One-command local setup (`docker compose up --build`)
- ✅ Deployed on Railway (backend) + Vercel (frontend)
- ✅ PostgreSQL via Supabase (cloud-hosted, free tier)
- ✅ Redis-ready (plug in Upstash when needed)

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 18 + TypeScript | UI framework |
| Styling | Tailwind CSS | Utility-first CSS |
| HTTP Client | Axios | REST API calls |
| Real-time | Native WebSocket API | Live messaging |
| Backend | FastAPI (Python 3.12) | REST + WebSocket server |
| ORM | SQLAlchemy 2.0 (async) | Database layer |
| Database | PostgreSQL 16 | Persistent storage |
| Cache | Redis 7 (optional) | Presence / pub-sub |
| Auth | JWT (python-jose) | Stateless authentication |
| Password | bcrypt (passlib) | Secure hashing |
| Deployment | Docker + Docker Compose | Containerisation |
| Backend Host | Railway | Cloud backend |
| Frontend Host | Vercel | CDN + static hosting |
| Database Host | Supabase | Managed PostgreSQL |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENT                           │
│              React 18 + TypeScript + Tailwind           │
│         Hosted on Vercel (global CDN, free tier)        │
└───────────────────┬─────────────────┬───────────────────┘
                    │ REST API         │ WebSocket (wss://)
                    ▼                 ▼
┌─────────────────────────────────────────────────────────┐
│                       BACKEND                           │
│              FastAPI + Python 3.12                      │
│          Hosted on Railway (auto-scaling)               │
└──────────┬──────────────────────────┬───────────────────┘
           │ SQLAlchemy async          │ Optional
           ▼                          ▼
┌──────────────────┐       ┌──────────────────────┐
│   PostgreSQL     │       │       Redis           │
│   (Supabase)     │       │   (Upstash — when     │
│   Free 500 MB    │       │    needed at scale)   │
└──────────────────┘       └──────────────────────┘
```

### Design Principles

- **Clean Architecture** — strict separation between API layer, business logic, and data access
- **Repository Pattern** — all database queries isolated in repository classes
- **Dependency Injection** — FastAPI `Depends()` for testable, swappable components
- **Async First** — fully async Python with `asyncpg` and SQLAlchemy async engine
- **Environment-driven config** — no hardcoded values; all config via environment variables

---

## Project Structure

```
ChatApplication/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── auth.py       # Register, login, profile
│   │   │           ├── users.py      # Search, view profiles
│   │   │           ├── chats.py      # Create DM / group chats
│   │   │           └── messages.py   # Send, edit, delete messages
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic settings
│   │   │   ├── security.py           # JWT + bcrypt
│   │   │   └── dependencies.py       # FastAPI DI providers
│   │   ├── db/
│   │   │   ├── models/               # SQLAlchemy ORM models
│   │   │   └── repositories/         # Data access layer
│   │   ├── services/
│   │   │   └── websocket_manager.py  # Connection hub
│   │   └── main.py                   # App entrypoint + WS handler
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── railway.toml
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── hooks/
│   │   │   ├── useAuth.ts            # Auth state management
│   │   │   └── useWebSocket.ts       # WS connection + events
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx         # Register + login UI
│   │   │   └── ChatPage.tsx          # Main chat interface
│   │   └── services/
│   │       └── api.ts                # Axios instance
│   ├── vercel.json
│   └── package.json
│
├── docker-compose.yml                # Full local stack
└── README.md
```

---

## Database Schema

```
users
  id · username · email · password_hash
  display_name · bio · profile_picture
  online · last_seen · is_active

chats
  id · is_group · name · created_at

chat_members
  id · chat_id → chats · user_id → users
  role (owner / admin / member) · joined_at

messages
  id · chat_id → chats · sender_id → users
  content · message_type · deleted_for_everyone
  replied_to_id → messages · created_at
```

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Create a new account |
| `POST` | `/api/v1/auth/login` | Authenticate and receive JWT tokens |
| `GET` | `/api/v1/auth/me` | Get current user profile |
| `PATCH` | `/api/v1/auth/me` | Update display name or bio |

### Users

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/users/search?q=` | Search users by username |
| `GET` | `/api/v1/users/{id}` | Get a user's public profile |

### Chats

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/chats` | List all chats for current user |
| `POST` | `/api/v1/chats/direct` | Open or create a direct message chat |
| `POST` | `/api/v1/chats/group` | Create a group chat |
| `GET` | `/api/v1/chats/{id}` | Get chat details and members |

### Messages

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/chats/{id}/messages` | Paginated message history |
| `POST` | `/api/v1/chats/{id}/messages` | Send a message |
| `PATCH` | `/api/v1/chats/{id}/messages/{msg_id}` | Edit message content |
| `DELETE` | `/api/v1/chats/{id}/messages/{msg_id}` | Delete message |

Full interactive documentation: **`/api/docs`** (Swagger UI)

---

## WebSocket Protocol

**Connection:** `wss://your-backend.railway.app/ws?token=<access_token>`

### Client → Server

| Event | Payload | Description |
|---|---|---|
| `typing` | `{ chat_id, is_typing }` | Broadcast typing status |

### Server → Client

| Event | Payload | Description |
|---|---|---|
| `new_message` | `{ id, chat_id, content, sender, created_at }` | New message received |
| `message_edited` | `{ chat_id, message_id, content }` | Message was edited |
| `message_deleted` | `{ chat_id, message_id }` | Message was deleted |
| `typing` | `{ chat_id, user_id, is_typing }` | Someone is typing |
| `presence` | `{ user_id, online }` | User came online / went offline |

---

## Local Development

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/Sujitapatel11/ChatApplication.git
cd ChatApplication

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your database credentials

# Start the full stack
docker compose up --build
```

### Access

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1 |
| Swagger Docs | http://localhost:8000/api/docs |

### Without Docker

```bash
# Backend
cd backend
pip install -r requirements.txt
docker compose up postgres redis -d   # just the DB services
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## Deployment

### Stack

| Layer | Platform | Cost |
|---|---|---|
| Frontend | Vercel | Free |
| Backend | Railway | Free ($5 credit/month) |
| Database | Supabase | Free (500 MB) |
| Cache | Upstash Redis | Free when added |

### Backend — Railway

1. Connect GitHub repo on [railway.app](https://railway.app)
2. Set **Root Directory** = `backend`
3. Set **Builder** = `Dockerfile`
4. Add environment variables (see below)
5. Generate domain

### Frontend — Vercel

1. Import GitHub repo on [vercel.com](https://vercel.com)
2. Set **Root Directory** = `frontend`
3. Add environment variables (see below)
4. Deploy

### Environment Variables

**Railway (Backend)**

| Variable | Value |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` |
| `SECRET_KEY` | Random 32+ character string |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` |
| `FRONTEND_URL` | Your Vercel URL |
| `ENVIRONMENT` | `production` |

**Vercel (Frontend)**

| Variable | Value |
|---|---|
| `VITE_API_BASE_URL` | `https://your-app.railway.app/api/v1` |
| `VITE_WS_BASE_URL` | `wss://your-app.railway.app` |

---

## Scaling Roadmap

| Users | Infrastructure |
|---|---|
| 0 – 1,000 | Railway free tier + Supabase free tier |
| 1,000 – 10,000 | Add Upstash Redis, upgrade Railway plan |
| 10,000 – 100,000 | Migrate to Hetzner VPS ($6/mo), add nginx load balancer |
| 100,000+ | Kubernetes, Redis Pub/Sub for cross-instance WS, PostgreSQL read replicas |

---

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx aiosqlite
pytest app/tests/ -v
```

---

## Contributing

1. Fork the repository
2. Create a feature branch — `git checkout -b feature/my-feature`
3. Commit your changes — `git commit -m "feat: add my feature"`
4. Push to the branch — `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

**Sujit Patel**
GitHub: [@Sujitapatel11](https://github.com/Sujitapatel11)
