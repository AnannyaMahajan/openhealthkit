from datetime import UTC, datetime


def utc_now() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


def format_iso(dt: datetime) -> str:
    """Format datetime to ISO 8601 string with UTC timezone offset."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.isoformat()


def parse_iso(iso_str: str) -> datetime:
    """Parse ISO 8601 string to timezone-aware UTC datetime."""
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt

