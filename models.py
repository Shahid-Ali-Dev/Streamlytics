from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Integer, String, DateTime, Float


class RawEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(sa_column=Column("event_type", String, index=True))
    value: float = Field(sa_column=Column("value", Float))
    metadata: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime))


class Metric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(sa_column=Column("event_type", String, index=True))
    window_start: datetime = Field(sa_column=Column("window_start", DateTime))
    window_end: datetime = Field(sa_column=Column("window_end", DateTime))
    count: int = Field(default=0)
    sum: float = Field(default=0.0)
    avg: float = Field(default=0.0)
