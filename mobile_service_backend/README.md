# Mobile Service Backend (Flask)

REST API for a mobile service management platform (users, services, orders).

- Runs on port **3001** by default
- Frontend dev server assumed at **http://localhost:3000**
- OpenAPI/Swagger UI available at **/docs**

## Backend-first startup (recommended)

This project is designed to start the backend first (using SQLite by default), then start the frontend after the backend is healthy.

### 1) Start backend (SQLite default)

- Defaults to: `DATABASE_URL=sqlite:///app.db`
- Health endpoint: `GET /health` (fast)

Key environment variables:
- `DATABASE_URL` (default `sqlite:///app.db`)
- `JWT_SECRET` (default `mobilecare_secret` for local/preview only)
- `JWT_TTL_MINUTES` (default `1440`, i.e. 24h)
- `HOST` (default `0.0.0.0`)
- `PORT` (default `3001`)
- `BACKEND_HEALTHCHECK_DISABLED` (default `false`)
  - When `true`, readiness endpoints (`/` and `/health`) return OK immediately and never perform external dependency checks.

### 2) Start frontend after backend is healthy

The frontend `npm start` runs `scripts/wait-for-backend.js` before launching the dev server, polling `${REACT_APP_API_BASE_URL}/health`.

## CORS

CORS is configured to allow the React dev server:

- Allowed origin: `http://localhost:3000`

If you deploy a real frontend, update CORS in `app/__init__.py` to include the deployed origin(s).

## Data storage

This backend uses SQLAlchemy with SQLite by default (`sqlite:///app.db`). The DB layer is isolated in:

- `app/db.py` (engine/session init)
- `app/models.py` (SQLAlchemy models)

To swap to a real DB, set `DATABASE_URL` (e.g., Postgres/MySQL) and restart. No code changes should be required for basic usage.

## Authentication

JWT Bearer tokens are used.

1) `POST /api/auth/signup` or `POST /api/auth/login`
2) Use response `access_token` as:
   - `Authorization: Bearer <token>`

### Dev seeding

`GET /api/dev/seed` seeds:
- Admin user: `admin@example.com` / `admin123`
- A few demo services

## Routes

### Health
- `GET /` – simple health response
- `GET /health` – readiness endpoint (fast)

### Auth
- `POST /api/auth/signup` – create a user account
- `POST /api/auth/login` – login and receive JWT
- `GET /api/auth/me` – get current user profile (requires auth)

### Users (admin)
- `GET /api/users` – list all users (requires admin token)

### Services
- `GET /api/services` – list services (public)

Query params supported:
- `q` (string): search in name/category/description
- `category` (string): exact match filter
- `min_price_cents` / `max_price_cents` (int): price range filter
- `include_inactive` (bool): include inactive services (admin only)

- `GET /api/services/<id>` – get a service (public; only if active)
- `POST /api/services` – create a service (admin only)
- `PATCH /api/services/<id>` – update a service (admin only)
- `DELETE /api/services/<id>` – soft-delete (deactivate) a service (admin only)

### Orders
- `GET /api/orders` – list current user's orders (admin gets all)
- `POST /api/orders` – create an order (requires auth)
- `GET /api/orders/<id>` – get order details (owner or admin)
- `PATCH /api/orders/<id>` – update order status/notes (admin only)
- `POST /api/orders/<id>/cancel` – cancel (owner or admin)

## OpenAPI / Swagger

Swagger UI:
- `GET /docs`

To export the OpenAPI spec:
- Run `python generate_openapi.py`
- Output: `interfaces/openapi.json`

## Notes
- `run.py` is configured to disable debug auto-reload for preview stability.
