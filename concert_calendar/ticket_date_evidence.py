"""Conservative date evidence from a venue-linked ticketing page.

The venue's own programme is not an independent source when its date disagrees
with the actual ticket product. Only accept a single, unambiguous seller date,
and only when both the advertised bill and venue match. Never use a calendar
year, a promotional date or another event's ticket to change a performance.
"""
from __future__ import annotations

from datetime import date
import json
import re
import unicodedata

from bs4 import BeautifulSoup


DATE_TIME_RE = re.compile(
    r"(?<!\d)(20\d{2}-\d{2}-\d{2})[ T]\d{2}:\d{2}(?::\d{2})?(?!\d)"
)
ENGLISH_DATE_RE = re.compile(
    r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w*\.?\s+"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+"
    r"(\d{1,2}),?\s+(20\d{2})\b",
    re.IGNORECASE,
)
MONTHS = {
    month.casefold(): i
    for i, month in enumerate(
        ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1
    )
}


def _identity(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").casefold()
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _iso_date(value: str) -> str | None:
    try:
        return date.fromisoformat(value[:10]).isoformat()
    except (TypeError, ValueError):
        return None


def confirmed_ticket_date(html: str, bill: str, venue: str) -> str | None:
    """Return seller date only for an exact bill/venue and one calendar day.

    Date parsing checks structured event data, clock-bearing ISO dates (such
    as Billetweb's calendar export), and English printed dates. Bare dates
    elsewhere on a sales page are deliberately not taken as performance dates.
    """
    soup = BeautifulSoup(html or "", "html.parser")
    page_text = soup.get_text(" ", strip=True)
    if not bill or not venue:
        return None
    if _identity(bill) not in _identity(page_text):
        return None
    if _identity(venue) not in _identity(page_text):
        return None

    candidates: set[str] = set()
    for match in DATE_TIME_RE.finditer(html or ""):
        parsed = _iso_date(match.group(1))
        if parsed:
            candidates.add(parsed)

    for match in ENGLISH_DATE_RE.finditer(page_text):
        month, day, year = match.groups()
        try:
            candidates.add(
                date(int(year), MONTHS[month[:3].casefold()], int(day)).isoformat()
            )
        except ValueError:
            continue

    for element in soup.select("time[datetime]"):
        value = element.get("datetime", "")
        if re.match(r"20\d{2}-\d\d-\d\d[T ]\d\d:\d\d", value):
            parsed = _iso_date(value)
            if parsed:
                candidates.add(parsed)

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (ValueError, TypeError):
            continue

        def walk(data):
            if isinstance(data, list):
                for item in data:
                    yield from walk(item)
            elif isinstance(data, dict):
                if (data.get("@type") in ("Event", "MusicEvent") and
                        _identity(bill) in _identity(data.get("name", ""))):
                    yield data
                if "@graph" in data:
                    yield from walk(data["@graph"])

        for item in walk(payload):
            value = item.get("startDate", "")
            if re.match(r"20\d{2}-\d\d-\d\d[T ]\d\d:\d\d", value):
                parsed = _iso_date(value)
                if parsed:
                    candidates.add(parsed)

    return next(iter(candidates)) if len(candidates) == 1 else None
