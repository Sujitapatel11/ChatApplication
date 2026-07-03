# FirstChat 💬

A production-ready, real-time messaging application built with modern technologies and clean architecture.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Tailwind CSS |
| Backend | FastAPI + Python 3.12 |
| Database | PostgreSQL 16 |
| Cache / Pub-Sub | Redis 7 |
| Real-time | WebSockets |
| Auth | JWT (access + refresh tokens) |
| File Storage | Cloudinary |
| Push Notifications | Firebase Cloud Messaging |
| Deployment | Docker + Docker Compose |
| API Docs | Swagger / OpenAPI |

---

## Features

- ✅ Register / Login / Logout with JWT + Refresh Token rotation
- ✅ Email OTP verification & password reset
- ✅ 1-to-1 and Group chats
- ✅ Send text, images, video, audio, documents, voice notes, GIFs
- ✅ Message reply, forward, edit, delete (for me / for everyone)
- ✅ Pin & star messages
- ✅ Read receipts (single ✓ → double ✓ → blue ✓✓)
- ✅ Typing indicators
- ✅ Online / last-seen presence
- ✅ Auto-reconnect WebSocket with exponential backoff
- ✅ Status / Stories (24-hour expiry)
- ✅ Voice & video call signalling
- ✅ Push notifications (FCM)
- ✅ Block & report users
- ✅ Admin panel (dashboard, ban users, manage reports)
- ✅ Dark mode / light mode
- ✅ Mobile-first responsive design
- ✅ Rate limiting
- ✅ Structured logging

---

## Project Structure

```
chatApplication/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # REST route handlers
│   │   ├── core/               # Config, security, dependencies, logging
│   │   ├── db/
│   │   │   ├── models/         # SQLAlchemy ORM models
│   │   │   └── repositories/   # Data access layer
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic (email, media, notifications, WS)
│   │   └── tests/              # Pytest integration tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── hooks/              # React hooks (auth, websocket, typing)
│   │   ├── pages/              # Page-level components
│   │   ├── services/           # API service layer (axios)
│   │   ├── types/              # TypeScript interfaces
│   │   └── utils/              # Formatting, storage helpers
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

---

## Quick Start (Docker)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running

### 1. Clone and configure

```bash
cd chatApplication
cp backend/.env backend/.env.local   # edit with your real values
```

### 2. Start everything

```bash
docker compose up --build
```

### 3. Open the app

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1 |
| API Docs (Swagger) | http://localhost:8000/api/docs |
| API Docs (ReDoc) | http://localhost:8000/api/redoc |

---

## Local Development (without Docker)

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start Postgres and Redis (or use Docker for just those)
docker compose up postgres redis -d

# Run the dev server
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

### Backend (backend/.env)

| Variable | Description | Required |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async URL | ✅ |
| `REDIS_URL` | Redis connection URL | ✅ |
| `SECRET_KEY` | JWT signing key (32+ chars) | ✅ |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary account | For media upload |
| `FCM_SERVER_KEY` | Firebase key | For push notifications |
| `SMTP_USER` / `SMTP_PASSWORD` | Email credentials | For OTP emails |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Get JWT tokens |
| POST | `/api/v1/auth/refresh` | Rotate refresh token |
| POST | `/api/v1/auth/logout` | Revoke refresh token |
| POST | `/api/v1/auth/verify-email` | Verify OTP |
| POST | `/api/v1/auth/forgot-password` | Send reset OTP |
| POST | `/api/v1/auth/reset-password` | Set new password |
| GET | `/api/v1/auth/me` | Current user profile |
| GET | `/api/v1/users/search?q=` | Search users |
| POST | `/api/v1/users/{id}/block` | Block user |
| POST | `/api/v1/users/{id}/report` | Report user |
| GET | `/api/v1/chats` | List chats |
| POST | `/api/v1/chats/direct` | Start 1-to-1 chat |
| POST | `/api/v1/chats/group` | Create group |
| GET | `/api/v1/chats/{id}/messages` | Message history |
| POST | `/api/v1/chats/{id}/messages` | Send message |
| POST | `/api/v1/chats/{id}/messages/media` | Send file |
| POST | `/api/v1/calls` | Initiate call |
| GET | `/api/v1/statuses` | Status feed |
| GET | `/api/v1/notifications` | Notifications |
| GET | `/api/v1/admin/dashboard` | Admin stats |

Full docs at **http://localhost:8000/api/docs** after starting.

---

## WebSocket Events

Connect: `ws://localhost:8000/ws?token=<access_token>`

| Direction | Event | Payload |
|---|---|---|
| Client → Server | `typing` | `{chat_id, is_typing}` |
| Client → Server | `subscribe_chat` | `{chat_id}` |
| Client → Server | `presence_ping` | `{}` |
| Server → Client | `new_message` | `{chat_id, message_id, ...}` |
| Server → Client | `message_edited` | `{chat_id, message_id, content}` |
| Server → Client | `message_deleted` | `{chat_id, message_id}` |
| Server → Client | `message_read` | `{chat_id, message_id, reader_id}` |
| Server → Client | `typing` | `{chat_id, user_id, is_typing}` |
| Server → Client | `presence` | `{user_id, online}` |
| Server → Client | `incoming_call` | `{call_id, call_type, caller_id, ...}` |

---

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx aiosqlite anyio
pytest app/tests/ -v
```

---

## Security Notes

- JWT secrets must be ≥32 random characters in production
- SMTP credentials should use App Passwords (not your main password)
- Cloudinary and Firebase keys should be environment-specific
- The `SECRET_KEY` default in `.env` is for development only — change it before deploying

---

## Scaling to 1M Users

The architecture supports horizontal scaling:

1. **Multiple backend instances** behind a load balancer (nginx/Traefik)
2. **Redis Pub/Sub** for cross-instance WebSocket message routing (replace the in-process `ConnectionManager`)
3. **PostgreSQL read replicas** for heavy read workloads
4. **Cloudinary CDN** handles media delivery automatically
5. **Redis caching** for user presence, unread counts
6. **Database connection pooling** via PgBouncer

---

## License

MIT
