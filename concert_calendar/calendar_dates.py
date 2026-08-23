from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


PARIS = ZoneInfo("Europe/Paris")


def quick_date_range(mode: str, now: datetime) -> tuple[str, str] | None:
    """Mirror the renderer's documented Paris-local quick-date semantics."""

    current = now.astimezone(PARIS).date()
    if mode == "tonight":
        start = end = current
    elif mode == "week":
        start = current - timedelta(days=current.weekday())
        end = start + timedelta(days=6)
    elif mode == "weekend":
        if current.weekday() == 6:
            start = current - timedelta(days=2)
        else:
            start = current + timedelta(days=4 - current.weekday())
        end = start + timedelta(days=2)
    elif mode in {"", "all"}:
        return None
    else:
        raise ValueError(f"Unknown quick-date mode: {mode}")
    return start.isoformat(), end.isoformat()
