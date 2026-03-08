from abc import ABC, abstractmethod

from app.models import ScannerRow


class MarketDataProvider(ABC):
    @abstractmethod
    async def fetch_premarket_rows(self, limit: int) -> list[ScannerRow]:
        raise NotImplementedError
