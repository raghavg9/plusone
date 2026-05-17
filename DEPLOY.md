# Deploying PlusOne to Railway

Railway is a modern deployment platform that makes it easy to ship full-stack apps. This guide will get you from zero to live in ~5 minutes.

## Prerequisites

- [Railway account](https://railway.app) (free tier available)
- GitHub account with access to this repo

## Deploy

### 1. Connect the repo to Railway

1. Go to [railway.app](https://railway.app)
2. Sign in (or sign up with GitHub for easiest auth)
3. Click **"Start a New Project"** → **"Deploy from GitHub"**
4. Search for and select `raghavg9/plusone`
5. Select the branch: **`claude/event-coordination-feature-JQpsO`**
6. Railway auto-detects the Dockerfile and sets up the deployment

### 2. Configure environment

No special env vars needed for the MVP — Railway reads `Dockerfile` and deploys the backend + frontend together.

**Optional:** If you want to customize, add to Railway project:
```
PYTHONUNBUFFERED=1
```

### 3. Deploy

Railway auto-deploys on every push. Once connected, any commit to `claude/event-coordination-feature-JQpsO` triggers a new build (~3–5 min).

You can also manually trigger in the Railway dashboard:
- Click the project
- Find the service
- Click **"Deploy"**

### 4. Get your URL

Once deployed:
1. Click your service in the Railway dashboard
2. Go to **"Deployments"** tab
3. Look for the public URL (e.g., `https://plusone-prod-xxxx.railway.app`)
4. Visit it in your browser — the React frontend loads, and all API calls work automatically

## What's deployed

- **Backend:** FastAPI running on port 8000
- **Frontend:** React SPA served at root (`/`)
- **Database:** SQLite file-based (at `/app/backend/plusone.db`)

The Dockerfile:
1. Builds React in Node container
2. Copies built assets to Python container
3. Runs FastAPI with static file serving

## How it works

All requests go to the FastAPI backend:
- `/api/*` routes hit the API endpoints
- All other routes serve `index.html` (React SPA routing)

Frontend makes requests to the same origin (e.g., `/api/users`), so no CORS issues.

## Scaling notes

**For the MVP:** SQLite is fine. It's file-based and persists per deploy; data survives restarts.

**When you outgrow it:**
- Add PostgreSQL to Railway (1 click in the dashboard)
- Update `backend/app/database.py` to use Postgres connection string from env
- Redeploy

## Troubleshooting

**Deploy fails to build:**
- Check Railway logs: Dashboard → Deployments → click a failed deployment
- Common: `pip install` timeout (retry manually)
- Common: Node/npm version mismatch (Railway uses node 22 by default)

**App crashes after deploy:**
- Check logs in Railway: Deployments → click "View Logs"
- FastAPI should log on startup

**Frontend shows 404 on refresh:**
- The Dockerfile mounts the SPA correctly (handled by `html=True` in StaticFiles)
- If it fails, check the frontend build succeeded in the Dockerfile logs

## Local testing before deploy

```bash
# Build the same Docker image locally
docker build -t plusone:test .
docker run -p 8000:8000 plusone:test

# Visit http://localhost:8000
```

## Next steps

Once live:
- Add authentication (JWT, OAuth)
- Upgrade to Postgres
- Add WebSocket support for real-time chat
- Set up a custom domain in Railway
- Add monitoring / error tracking (Sentry)
