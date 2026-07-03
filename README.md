# FirstChat 💬

A real-time messaging application built with FastAPI, React, WebSockets, PostgreSQL and Redis.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Tailwind CSS |
| Backend | FastAPI + Python 3.12 |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Real-time | WebSockets |
| Auth | JWT (access + refresh tokens) |
| Deployment | Docker + Docker Compose |
| API Docs | Swagger / OpenAPI |

---

## Features

- ✅ Register & Login with JWT tokens
- ✅ 1-to-1 Direct Messaging
- ✅ Group Chats
- ✅ Send & receive text messages in real time
- ✅ Edit message
- ✅ Delete message (for me / for everyone)
- ✅ Typing indicators
- ✅ Online / Offline presence
- ✅ Auto-reconnect WebSocket with exponential backoff
- ✅ Search users
- ✅ User profile (display name, bio)
- ✅ Fully Dockerized (one command to run)

---

## Project Structure

```
chatApplication/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # auth, users, chats, messages
│   │   ├── core/               # config, security, dependencies
│   │   ├── db/
│   │   │   ├── models/         # User, Chat, ChatMember, Message
│   │   │   └── repositories/   # data access layer
│   │   ├── services/           # WebSocket connection manager
│   │   └── tests/              # integration tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── hooks/              # useAuth, useWebSocket
│   │   ├── pages/              # LoginPage, ChatPage
│   │   └── services/           # axios API client
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

---

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running

### Run with Docker

```bash
git clone https://github.com/Sujitapatel11/ChatApplication.git
cd ChatApplication
docker compose up --build
```

### Open the app

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1 |
| Swagger Docs | http://localhost:8000/api/docs |

---

## Local Development (without Docker)

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start Postgres and Redis via Docker
docker compose up postgres redis -d

# Copy env file and run
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env`:

| Variable | Description | Required |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async connection string | ✅ |
| `REDIS_URL` | Redis connection URL | ✅ |
| `SECRET_KEY` | JWT signing key (32+ chars) | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | ✅ |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | ✅ |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Get JWT tokens |
| GET | `/api/v1/auth/me` | Current user profile |
| PATCH | `/api/v1/auth/me` | Update profile |
| GET | `/api/v1/users/search?q=` | Search users by username |
| GET | `/api/v1/users/{id}` | Get user profile |
| GET | `/api/v1/chats` | List all chats |
| POST | `/api/v1/chats/direct` | Start a 1-to-1 chat |
| POST | `/api/v1/chats/group` | Create a group chat |
| GET | `/api/v1/chats/{id}` | Get chat details |
| GET | `/api/v1/chats/{id}/messages` | Get message history |
| POST | `/api/v1/chats/{id}/messages` | Send a message |
| PATCH | `/api/v1/chats/{id}/messages/{msg_id}` | Edit a message |
| DELETE | `/api/v1/chats/{id}/messages/{msg_id}` | Delete a message |

Full interactive docs at **http://localhost:8000/api/docs**

---

## WebSocket

Connect: `ws://localhost:8000/ws?token=<access_token>`

| Direction | Event | Payload |
|---|---|---|
| Client → Server | `typing` | `{ chat_id, is_typing }` |
| Server → Client | `new_message` | `{ id, chat_id, content, sender, ... }` |
| Server → Client | `message_edited` | `{ chat_id, message_id, content }` |
| Server → Client | `message_deleted` | `{ chat_id, message_id }` |
| Server → Client | `typing` | `{ chat_id, user_id, is_typing }` |
| Server → Client | `presence` | `{ user_id, online }` |

---

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx aiosqlite
pytest app/tests/ -v
```

---

## License

MIT
