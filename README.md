# Streamlytics
Streamlytics is a small, production-minded service for ingesting event streams and computing lightweight analytics (counts, sums, averages) asynchronously. The backend uses FastAPI for API, SQLModel (SQLAlchemy + Pydantic) for persistence, Celery + Redis for background processing, and pandas for aggregation logic.
