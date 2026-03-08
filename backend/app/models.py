from datetime import datetime

from pydantic import BaseModel, Field


class ScannerRow(BaseModel):
    ticker: str
    premarket_change_pct: float
    volume: int
    last_updated_at: datetime
    session: str = Field(default="premarket")


class HealthResponse(BaseModel):
    status: str
    provider: str
