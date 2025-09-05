# Streamlytics

Streamlytics is a lightweight real-time ingestion + analytics demo written in Python.
It demonstrates an industry-style stack: **FastAPI** (HTTP API), **SQLModel/SQLite** (persistence),
**Celery + Redis** (background processing) and **pandas** for aggregation logic.

> This project is a demo for local/dev use. For production, replace SQLite with Postgres and tune Celery/Redis.

---

## Features
- `POST /ingest` — ingest events (type, value, metadata)
- Asynchronous aggregation via Celery (time-window metrics)
- `GET /metrics` — query aggregated metrics (count / sum / avg)
- Lightweight analytics implemented with `pandas`
- Docker Compose for easy local setup (Redis + web + worker)

---

## Requirements
- Docker & Docker Compose (recommended) **or**
- Python 3.10+ + Redis (for Celery) installed locally

---

## Quick start (Docker)
1. Build and start:
```bash
docker compose up --build
