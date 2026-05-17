# Deploying PlusOne to Railway

This is a monorepo (FastAPI backend + React frontend). Railway requires **two separate services** — deploy them independently, then link them together.

## Prerequisites

- [Railway account](https://railway.app) (free tier available)
- GitHub access to `raghavg9/plusone`

## Deploy Backend

### 1. Create a new Railway project for the backend

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"** → **"Deploy from GitHub"**
3. Select `raghavg9/plusone`
4. Select branch: `claude/event-coordination-feature-JQpsO`
5. In the config step, set:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. Click **"Deploy"** — Railway builds and deploys the FastAPI backend

### 2. Get the backend URL

Once deployed:
1. Go to the Railway service dashboard
2. Look for the **"Public Domain"** (e.g., `https://plusone-backend-prod-xxxx.railway.app`)
3. Test it: visit `https://plusone-backend-prod-xxxx.railway.app/health` — should return `{"status":"ok"}`
4. **Copy this URL** — you'll need it for the frontend

## Deploy Frontend

### 1. Create a second Railway project for the frontend

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"** → **"Deploy from GitHub"**
3. Select `raghavg9/plusone` again
4. Select branch: `claude/event-coordination-feature-JQpsO`
5. In the config step, set:
   - **Root directory:** `frontend`
   - **Build command:** `npm install && npm run build`
   - **Start command:** `npm run preview`

6. **Add environment variable:**
   - **Key:** `VITE_API_URL`
   - **Value:** Paste the backend URL from above (e.g., `https://plusone-backend-prod-xxxx.railway.app`)

7. Click **"Deploy"** — Railway builds and deploys the React SPA

### 2. Get the frontend URL

Once deployed:
1. Go to the Railway frontend service dashboard
2. Look for the **"Public Domain"** (e.g., `https://plusone-frontend-prod-xxxx.railway.app`)
3. **Visit it in your browser** — you should see the PlusOne app

## How it works

- **Frontend** (React SPA) at `https://plusone-frontend-prod-xxxx.railway.app`
  - Makes requests to `/api/*`
  - Vite's preview mode proxies them to `VITE_API_URL` (the backend)

- **Backend** (FastAPI) at `https://plusone-backend-prod-xxxx.railway.app`
  - Handles all API requests
  - Stores SQLite database at `/app/backend/plusone.db` (survives restarts)

## Auto-deploy on push

Any push to `claude/event-coordination-feature-JQpsO` triggers rebuilds:
- Backend service rebuilds from `backend/` 
- Frontend service rebuilds from `frontend/`

Both redeploy automatically.

## Scaling notes

**SQLite works for the MVP** — it's file-based and persists per service.

**To upgrade to PostgreSQL later:**
1. In Railway, add a new PostgreSQL service to the backend project
2. Railway auto-provides a `DATABASE_URL` env var
3. Update `backend/app/database.py` to use it
4. Redeploy

## Troubleshooting

**Frontend shows 404 or can't reach the API:**
- Check that `VITE_API_URL` env var is set correctly in the frontend Railway service
- Visit `VITE_API_URL/health` manually in your browser — should work

**Backend works locally but fails on Railway:**
- Check Railway logs: Dashboard → Deployments → click failed deployment
- Common: missing `requirements.txt` (should be at `backend/requirements.txt`)
- Common: port binding issue (Railway sets `$PORT` env var; make sure you use it)

**Import errors in backend:**
- Make sure `backend/app/__init__.py` exists (it should be empty)
- Check all Python imports are relative (`from .database import ...`)

## Next steps

Once both are live and working:
- Add authentication (JWT, OAuth, session cookies)
- Enable WebSocket for real-time chat
- Upgrade to PostgreSQL for production data
- Set up custom domains
- Add error tracking (Sentry)
- Enable CORS properly (limit origins to your domain)
