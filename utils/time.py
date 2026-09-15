from datetime import datetime, timedelta
from typing import Optional
STEAM_HISTORY_DATE_FMT = "%b %d %Y %H"
STEAM_COOLDOWN_FMT = "%b %d, %Y %H:%M:%S"
def parse_steam_history_date(date_str: str) -> Optional[datetime]:
    try:
        part = date_str.split(":")[0].strip()
        return datetime.strptime(part, STEAM_HISTORY_DATE_FMT)
    except (ValueError, IndexError):
        return None
def parse_steam_cooldown(raw: str) -> Optional[datetime]:
    try:
        raw = raw.replace(" (", " ").replace(")", "")
        return datetime.strptime(raw, STEAM_COOLDOWN_FMT)
    except (ValueError, TypeError):
        return None
def cutoff_days_ago(days: int) -> datetime:
    return datetime.now() - timedelta(days=days)
def utc_timestamp() -> float:
    return datetime.utcnow().timestamp()
