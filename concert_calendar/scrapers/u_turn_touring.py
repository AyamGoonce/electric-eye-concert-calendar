import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "U-Turn Touring"
SHOWS_URL = "https://www.uturntouring.com/shows/"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_date(value):
    match = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", clean_text(value))
    if not match:
        return ""
    month = MONTHS.get(match.group(2).casefold())
    if month is None:
        return ""
    try:
        return date(int(match.group(3)), month, int(match.group(1))).isoformat()
    except ValueError:
        return ""


def split_location(value):
    text = clean_text(value)
    if " — " not in text:
        return "", text
    city, venue = text.split(" — ", 1)
    return clean_text(city).rstrip(","), clean_text(venue)


def parse_show_row(row, *, today=None):
    today = today or date.today()
    date_node = row.select_one(".show-full-date")
    artist_node = row.select_one(".show-full-name")
    venue_node = row.select_one(".show-full-venue")
    event_date = parse_date(date_node.get_text(" ", strip=True) if date_node else "")
    headliner = clean_text(artist_node.get_text(" ", strip=True) if artist_node else "")
    city, venue = split_location(
        venue_node.get_text(" ", strip=True) if venue_node else ""
    )
    if not all((event_date, headliner, city, venue)):
        return None
    if date.fromisoformat(event_date) < today:
        return None
    ticket = row.select_one("a.ticket-btn[href]")
    ticket_url = clean_text(ticket.get("href")) if ticket else None
    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="",
        promoters=None,
        ticket_url=ticket_url or SHOWS_URL,
        ticket_status="tickets" if ticket_url else None,
        event_type="concert",
        performers=[headliner],
        raw_title=headliner,
    )


def parse_events(html, *, today=None):
    soup = BeautifulSoup(html, "html.parser")
    events = {}
    for row in soup.select(".show-full-row"):
        event = parse_show_row(row, today=today)
        if event:
            key = (
                event.date, event.headliner.casefold(), event.venue.casefold(),
                event.city.casefold(),
            )
            events[key] = event
    return list(events.values())


def load_events(today=None):
    response = requests.get(SHOWS_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    events = parse_events(response.text, today=today)
    print(f"Created {len(events)} U-Turn Touring ConcertEvent records")
    return events
