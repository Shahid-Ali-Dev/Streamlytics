
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlmodel import Session, select
from db import create_db_and_tables, engine
from models import RawEvent, Metric
import os
from dotenv import load_dotenv
import tasks

load_dotenv()

create_db_and_tables()

app = FastAPI(title="Streamlytics", version="0.1")


class IngestEvent(BaseModel):
    event_type: str
    value: float
    metadata: str | None = None


@app.post("/ingest", status_code=201)
def ingest(event: IngestEvent, background_tasks: BackgroundTasks):
    """Ingest a single event, persist immediately and enqueue processing."""
    raw = RawEvent(event_type=event.event_type, value=event.value, metadata=event.metadata, created_at=datetime.utcnow())
    with Session(engine) as session:
        session.add(raw)
        session.commit()
        session.refresh(raw)

    # enqueue Celery task (asynchronously)
    try:
        tasks.process_recent_events.delay(window_minutes=5)
    except Exception:
        # If Celery not available, run synchronously in background thread as fallback
        background_tasks.add_task(tasks.process_recent_events, 5)

    return {"status": "ingested", "id": raw.id}


@app.get("/metrics")
def get_metrics(event_type: str | None = None, since_minutes: int = 60):
    """Return computed metrics optionally filtered by event_type and time window"""
    cutoff = datetime.utcnow() - timedelta(minutes=since_minutes)
    with Session(engine) as session:
        q = Session(engine).exec  # not used, just pattern
        stmt = select(Metric).where(Metric.window_start >= cutoff)
        if event_type:
            stmt = stmt.where(Metric.event_type == event_type)
        metrics = session.exec(stmt).all()
        return [
            {
                "event_type": m.event_type,
                "window_start": m.window_start.isoformat(),
                "window_end": m.window_end.isoformat(),
                "count": m.count,
                "sum": m.sum,
                "avg": m.avg,
            }
            for m in metrics
        ]


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
