from typing import List, Tuple
import pandas as pd
from datetime import datetime, timedelta
from models import RawEvent
from sqlmodel import Session, select
from db import engine


def load_events_since(minutes: int = 10) -> pd.DataFrame:
    """Load events from DB for the last `minutes` minutes into a DataFrame."""
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    with Session(engine) as session:
        stmt = select(RawEvent).where(RawEvent.created_at >= cutoff)
        rows = session.exec(stmt).all()
        data = [
            {"id": r.id, "event_type": r.event_type, "value": r.value, "created_at": r.created_at}
            for r in rows
        ]
    if not data:
        return pd.DataFrame(columns=["id", "event_type", "value", "created_at"])
    df = pd.DataFrame(data)
    return df


def compute_time_window_metrics(df: pd.DataFrame, window_minutes: int = 5) -> List[Tuple[str, datetime, datetime, int, float, float]]:
    """Group events by event_type and time window (window_minutes) and compute count, sum, avg."""
    if df.empty:
        return []

    # Round down timestamp to window start
    df["window_start"] = df["created_at"].dt.floor(f"{window_minutes}T")
    df["window_end"] = df["window_start"] + pd.Timedelta(minutes=window_minutes)

    grouped = df.groupby(["event_type", "window_start", "window_end"]).agg(
        count=("value", "count"),
        sum=("value", "sum"),
        avg=("value", "mean")
    ).reset_index()

    results = []
    for _, row in grouped.iterrows():
        results.append(
            (row["event_type"], row["window_start"].to_pydatetime(), row["window_end"].to_pydatetime(), int(row["count"]), float(row["sum"]), float(row["avg"]))
        )
    return results
