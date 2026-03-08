from typing import Any

import httpx

from app.config import Settings
from app.models import ScannerRow


class SupabaseSnapshotRepository:
    def __init__(self, settings: Settings) -> None:
        self._url = settings.supabase_url
        self._key = settings.supabase_key
        self._table = settings.supabase_table

    @property
    def enabled(self) -> bool:
        return bool(self._url and self._key)

    async def save_scan(
        self,
        rows: list[ScannerRow],
        min_change_pct: float,
        min_volume: int,
    ) -> None:
        if not self.enabled or not rows:
            return

        records: list[dict[str, Any]] = [
            {
                "ticker": row.ticker,
                "premarket_change_pct": row.premarket_change_pct,
                "volume": row.volume,
                "last_updated_at": row.last_updated_at.isoformat(),
                "session": row.session,
                "applied_min_change_pct": min_change_pct,
                "applied_min_volume": min_volume,
            }
            for row in rows
        ]

        endpoint = f"{self._url.rstrip('/')}/rest/v1/{self._table}"
        headers = {
            "apikey": self._key,
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(endpoint, headers=headers, json=records)
            response.raise_for_status()
