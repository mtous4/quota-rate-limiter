import math
from datetime import datetime, timezone

def parse_iso_timestamp(ts_str: str) -> datetime:
    """
    Parses a UTC ISO 8601 timestamp with milliseconds and trailing 'Z'.
    Example: '2026-09-01T10:00:00.000Z'
    """
    if ts_str.endswith("Z"):
        clean_ts = ts_str[:-1] + "+00:00"
    else:
        clean_ts = ts_str
    return datetime.fromisoformat(clean_ts).astimezone(timezone.utc)

def get_minute_window_key(dt: datetime) -> str:
    """
    Returns calendar UTC minute key: 'YYYY-MM-DDTHH:mm'
    Protects: Rule R1 (wall-clock calendar minute alignment).
    """
    return f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}T{dt.hour:02d}:{dt.minute:02d}"

def get_hour_window_key(dt: datetime) -> str:
    """
    Returns calendar UTC hour key: 'YYYY-MM-DDTHH'
    Protects: Rule R1 (wall-clock calendar hour alignment).
    """
    return f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}T{dt.hour:02d}"

def calculate_retry_after(dt: datetime, reason: str) -> int | None:
    """
    Calculates whole seconds from request timestamp until the binding window resets,
    rounded up (ceiling).
    Protects: Rule R8.
    - 'requests_per_minute' -> seconds to next calendar minute boundary.
    - 'tokens_per_hour' -> seconds to next calendar hour boundary.
    - 'both' -> the later boundary (next calendar hour boundary).
    - Otherwise -> None.
    """
    if reason == "requests_per_minute":
        ms_into_minute = dt.second * 1000 + dt.microsecond // 1000
        ms_remaining = 60000 - ms_into_minute
        return math.ceil(ms_remaining / 1000)
    elif reason in ("tokens_per_hour", "both"):
        ms_into_hour = (dt.minute * 60 + dt.second) * 1000 + dt.microsecond // 1000
        ms_remaining = 3600000 - ms_into_hour
        return math.ceil(ms_remaining / 1000)
    return None
