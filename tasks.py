import os
from celery import Celery
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlmodel import Session, select
from models import RawEvent, Metric
from db import engine
from analytics import compute_time_window_metrics, load_events_since

load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app = Celery("streamlytics", broker=CELERY_BROKER_URL)


@celery_app.task
def process_recent_events(window_minutes: int = 5):
    """
    Periodic or on-demand: load recent events and compute metrics, upsert into Metric table.
    """
    df = load_events_since(minutes=window_minutes * 4)  # lookback some windows
    rows = compute_time_window_metrics(df, window_minutes=window_minutes)
    if not rows:
        return {"status": "no_data"}

    # upsert metrics
    with Session(engine) as session:
        for event_type, ws, we, count, s, avg in rows:
            # check existing metric for same event_type & window_start
            stmt = select(Metric).where(Metric.event_type == event_type, Metric.window_start == ws)
            existing = session.exec(stmt).first()
            if existing:
                existing.count = count
                existing.sum = s
                existing.avg = avg
                existing.window_end = we
                session.add(existing)
            else:
                m = Metric(event_type=event_type, window_start=ws, window_end=we, count=count, sum=s, avg=avg)
                session.add(m)
        session.commit()

    return {"status": "ok", "rows": len(rows)}
