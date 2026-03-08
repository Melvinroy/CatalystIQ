from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


def is_premarket_window(now_utc: datetime | None = None) -> bool:
    now = now_utc or datetime.now(tz=ZoneInfo("UTC"))
    et_now = now.astimezone(ET)
    start_minutes = 4 * 60
    end_minutes = 9 * 60 + 30
    current_minutes = et_now.hour * 60 + et_now.minute
    return start_minutes <= current_minutes < end_minutes
