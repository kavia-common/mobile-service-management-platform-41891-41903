# mobile-service-management-platform-41891-41903

A web application for providing and managing mobile phone services, allowing users to browse, request, and manage various mobile-related services online.

## Containers

### Backend: `mobile_service_backend` (Flask)
- Runs on **port 3001** by default
- REST API under `/api/*`
- Health endpoint: `GET /health`
- Swagger UI: `GET /docs`

See: `mobile_service_backend/README.md` for full API details.

### Frontend: `mobile_service_frontend` (React)
- Runs on **port 3000**
- Will consume backend APIs at `http://localhost:3001` during development.