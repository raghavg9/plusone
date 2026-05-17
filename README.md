# PlusOne

A social coordination layer for events. Instead of replacing ticketing or
discovery platforms, PlusOne embeds into them as a **"Find a Group"** feature:
attendees who don't want to go alone get auto-matched into a small,
compatible group, vet each other via lightweight profiles, and coordinate in
a temporary group chat before the event.

> The emotional promise: *"You'll always have people to go with."*

This repository is an MVP: a FastAPI + SQLite backend with an auto-matching
algorithm, and a React (Vite + TypeScript) frontend that walks a user through
the full flow.

## Architecture

```
backend/   FastAPI service, SQLAlchemy models, SQLite, matching algorithm
frontend/  React + Vite + TypeScript single-page flow
```

### Matching algorithm

When a match request is submitted, `backend/app/matching.py` greedily clusters
all pending requests for that event into compatible groups. A group is valid
only when every member shares a **vibe**, a compatible **age band**, and every
member's **gender preference** (`women_only` / `men_only` / `any`) is
satisfied. A cluster becomes a group once it reaches **3 members** (capped at
**6**); remaining requests stay pending until enough compatible attendees
arrive.

## Running locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api/*` to the backend
on port 8000.

## User flow

1. Create a lightweight profile (bio + Instagram / LinkedIn / Spotify /
   phone-verified for social proof).
2. Paste an event link and choose group preferences (vibe, age band,
   composition, low-pressure, first-timer).
3. Submit — the request enters the matching pool.
4. Once 3+ compatible attendees exist, you're auto-matched into a group.
5. View group members' profiles and social links, then coordinate in the
   temporary group chat.

## API surface

| Method | Path | Purpose |
| ------ | ---- | ------- |
| POST | `/users` | Create a profile |
| POST | `/events` | Register/ingest an event by link (idempotent on URL) |
| GET  | `/events` | List events |
| POST | `/match-requests` | Submit a request; triggers auto-matching |
| GET  | `/match-requests/{id}` | Poll match status |
| GET  | `/groups/{id}` | Group + members + event |
| GET/POST | `/groups/{id}/messages` | Group chat (membership enforced) |

## Scope notes

This is a deliberately minimal MVP. Authentication, real identity
verification, push notifications, and a B2B integration SDK are intentionally
out of scope and would be the natural next steps.
