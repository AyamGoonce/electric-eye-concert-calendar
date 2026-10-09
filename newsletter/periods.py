"""Reporting periods for Electric Eye newsletters."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")


def reporting_period(frequency: str, *, now: datetime | None = None) -> dict:
    """Return the previous completed weekly or monthly reporting period."""
    current = (now or datetime.now(PARIS)).astimezone(PARIS).date()

    if frequency == "weekly":
        current_monday = current - timedelta(days=current.weekday())
        start = current_monday - timedelta(days=7)
        end = current_monday
        identifier = f"{start.isocalendar().year}-W{start.isocalendar().week:02d}"

    elif frequency == "monthly":
        end = current.replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
        identifier = start.strftime("%Y-%m")

    else:
        raise ValueError(f"Unsupported newsletter frequency: {frequency}")

    return {
        "frequency": frequency,
        "identifier": identifier,
        "start": start.isoformat(),
        "end_exclusive": end.isoformat(),
    }
