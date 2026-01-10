# Mobile Service Backend (Flask)

## Backend-first startup (recommended)

This project is designed to start the backend first (using SQLite by default), then start the frontend after the backend is healthy.

### 1) Start backend (SQLite default)
- Defaults to: `DATABASE_URL=sqlite:///app.db`
- Health endpoint: `GET /health` (fast)

Key environment variables:
- `DATABASE_URL` (default `sqlite:///app.db`)
- `JWT_SECRET` (default `mobilecare_secret` for local/preview only)
- `HOST` (default `0.0.0.0`)
- `PORT` (default `3001`)
- `BACKEND_HEALTHCHECK_DISABLED` (default `false`)
  - When `true`, readiness endpoints (`/` and `/health`) return OK immediately and never perform external dependency checks.

### 2) Start frontend after backend is healthy
The frontend `npm start` runs `scripts/wait-for-backend.js` before launching the dev server, polling `${REACT_APP_API_BASE_URL}/health`.

## Notes
- `run.py` is configured to disable debug auto-reload for preview stability.
