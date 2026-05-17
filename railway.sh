#!/bin/bash
set -e

echo "Installing Python dependencies..."
cd /app/backend
pip install --no-cache-dir -r requirements.txt

echo "Building frontend..."
cd /app/frontend
npm install --legacy-peer-deps
npm run build

echo "Starting FastAPI server..."
cd /app
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
