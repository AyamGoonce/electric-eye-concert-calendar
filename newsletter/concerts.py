"""Read-only extraction of new concerts for Electric Eye newsletters."""

from datetime import date, datetime
import re
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")
EVENT_ID = re.compile(r"^[0-9a-f]{16}$")
CALENDAR_URL = (
    "https://www.electriceyerock.com"
    "/p/paris-area-concert-calendar.html"
)


def extract_concerts(events, period, publication_date, as_of=None):
    """Select newly discovered concerts that have not yet taken place.

    events: final published calendar records, not raw scraper events.
    period: reporting period with start and end_exclusive dates.
    publication_date: newsletter publication date (YYYY-MM-DD).
    as_of: optional later date used to hide expired archived entries.
    """
    cutoff = max(
        date.fromisoformat(publication_date),
        date.fromisoformat(as_of) if as_of else date.fromisoformat(publication_date),
    )
    start = date.fromisoformat(period["start"])
    end = date.fromisoformat(period["end_exclusive"])

    output = []
    seen = set()

    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Invalid published calendar record")

        event_id = event.get("i")
        if not isinstance(event_id, str) or not EVENT_ID.fullmatch(event_id):
            raise ValueError("Published calendar record has an invalid public ID")

        first_seen = event.get("fs")
        if not first_seen or first_seen.startswith("1970-01-01"):
            continue

        discovered = datetime.fromisoformat(
            first_seen.replace("Z", "+00:00")
        )
        if discovered.tzinfo is None:
            raise ValueError("Concert discovery timestamp lacks timezone")

        discovery_date = discovered.astimezone(PARIS).date()
        if not start <= discovery_date < end:
            continue

        concert_date = date.fromisoformat(event["d"])
        if concert_date < cutoff or event_id in seen:
            continue

        seen.add(event_id)

        output.append({
            "id": event_id,
            "artist": event.get("h", ""),
            "title": event.get("et") or event.get("h", ""),
            "date": concert_date.isoformat(),
            "time": event.get("st"),
            "venue": event.get("v", ""),
            "city": event.get("c", ""),
            "image": event.get("im"),
            "first_seen": discovered.isoformat(),
            "url": f"{CALENDAR_URL}#event-{event_id}",
        })

    output.sort(
        key=lambda item: (
            item["date"],
            item["artist"].casefold(),
            item["venue"].casefold(),
            item["id"],
        )
    )

    return output
