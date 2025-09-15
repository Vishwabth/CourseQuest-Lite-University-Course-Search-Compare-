# CourseQuest Lite – University Course Search & Compare

Production-ready sample for the take-home assignment.

## Features

- **PostgreSQL** schema and indexes
- **FastAPI** REST API:
  - `GET /api/courses` with filters & pagination
  - `GET /api/compare?ids=1,2` to compare
  - `POST /api/ingest` (multipart CSV, header `X-Ingest-Token`)
  - `POST /api/ask` rule-based parsing -> uses `/api/courses`
  - `GET /api/meta` distinct departments/levels/delivery modes
- **React (Vite + TS)** Frontend:
  - Search page with filters, pagination and "Add to compare"
  - Compare page (table) from localStorage or URL ids
  - Ask-AI page: shows parsed filters and results
- **Docker Compose** for DB, API, static frontend (nginx)
- **Dev Container** for VS Code (no local Node/Python needed)
- **Tests** for parser
- **Sample CSV** in `sample_data/`

## Quick Start (Docker)

```bash
# From repo root
cp .env.example .env

# Build and run
docker compose up -d --build

# Ingest data (replace token and path if needed)
curl -X POST   -H "X-Ingest-Token: supersecrettoken"   -F "file=@sample_data/courses.csv"   http://localhost:8000/api/ingest
```

Open:
- UI: http://localhost:3000
- API docs: http://localhost:8000/docs

## Dev Container (optional)

1. Install VS Code + Dev Containers extension.
2. Open this folder in VS Code → **Reopen in Container**.
3. Run `docker compose up -d --build` inside the container terminal if not running.

## API Overview

- `GET /api/courses?page=1&page_size=10&department=CS&level=UG&max_fee=50000&min_rating=4&delivery_mode=online&q=data`
- `GET /api/compare?ids=1,2,5`
- `POST /api/ingest` (header: `X-Ingest-Token`)
  - multipart field `file` with your CSV
- `POST /api/ask`
  - body: `{ "question": "UG online courses under 50k fee with rating >= 4 in CS" }`
  - response includes `parsed_filters` and `results`
- `GET /api/meta` returns enums for dropdowns

## Project Structure

```
backend/
frontend/
sample_data/
.devcontainer/
docker-compose.yml
```

## Tests

```bash
# Inside backend container or dev container
cd backend
pytest -q
```

## Notes

- CORS is enabled for origins in `.env`.
- For production you can put the backend behind a reverse proxy and serve frontend via nginx (already used).
