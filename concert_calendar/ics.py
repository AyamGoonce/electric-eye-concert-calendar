from __future__ import annotations

from datetime import date, timedelta
import re

from concert_calendar.event_state import canonical_event_identity
from concert_calendar.models import ConcertEvent


def escape_ics(value: str) -> str:
    return (value or "").replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


def build_ics(event: ConcertEvent, *, generated_at: str = "20260823T120000Z") -> str:
    day = date.fromisoformat(event.date[:10])
    if event.start_time:
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", event.start_time):
            raise ValueError("Invalid reliable event start time")
        start = f"DTSTART;TZID=Europe/Paris:{day:%Y%m%d}T{event.start_time.replace(':', '')}00"
        end = None
    else:
        start = f"DTSTART;VALUE=DATE:{day:%Y%m%d}"
        end = f"DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}"
    description = ""
    if event.festival_name:
        description = "Festival lineup: " + ", ".join([event.headliner, *(event.openers or [])])
    elif event.openers:
        description = "With " + ", ".join(event.openers)
    if event.ticket_url:
        description += ("\n" if description else "") + event.ticket_url
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//Electric Eye//Concert Calendar//EN", "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT", f"UID:{canonical_event_identity(event)[:16]}@electriceyerock.com",
        f"DTSTAMP:{generated_at}", start,
    ]
    if end:
        lines.append(end)
    lines.extend([
        "SUMMARY:" + escape_ics(event.headliner),
        "LOCATION:" + escape_ics(event.venue + ("" if event.city.casefold() == "paris" else ", " + event.city)),
        "DESCRIPTION:" + escape_ics(description), "END:VEVENT", "END:VCALENDAR", "",
    ])
    return "\r\n".join(lines)
