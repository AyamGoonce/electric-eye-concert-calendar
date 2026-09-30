import re
from datetime import date
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Persona Grata"
EVENTS_URL = "https://personagrataagency.com/events/"
REQUEST_TIMEOUT = 30
DICE_SHORT_LINK_SAFETY_CEILING = 50
DICE_SHORT_LINK_ATTEMPTS = 2

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_date(value):
    match = re.fullmatch(
        r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",
        clean_text(value),
    )
    if not match:
        return ""
    month = MONTHS.get(match.group(2).casefold())
    if month is None:
        return ""
    try:
        return date(int(match.group(3)), month, int(match.group(1))).isoformat()
    except ValueError:
        return ""


def split_place(value):
    parts = [clean_text(part) for part in clean_text(value).rsplit(",", 1)]
    return parts[0] if parts else ""


def parse_event_row(row, *, today=None):
    today = today or date.today()
    date_node = row.select_one(".date")
    artist_node = row.select_one(".band")
    venue_node = row.select_one(".venue")
    place_node = row.select_one(".place")
    event_date = parse_date(date_node.get_text(" ", strip=True) if date_node else "")
    headliner = clean_text(artist_node.get_text(" ", strip=True) if artist_node else "")
    venue = clean_text(venue_node.get_text(" ", strip=True) if venue_node else "")
    city = split_place(place_node.get_text(" ", strip=True) if place_node else "")
    if not all((event_date, headliner, venue, city)):
        return None
    if date.fromisoformat(event_date) < today:
        return None

    facebook_url = None
    ticket_url = None
    for link in row.select(".second.ticket a[href]"):
        href = clean_text(link.get("href"))
        if re.match(r"https?://(?:www\.)?facebook\.com/events/\d+/?", href):
            facebook_url = href
        elif href:
            ticket_url = href

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="",
        promoters=None,
        facebook_event_url=facebook_url,
        ticket_url=ticket_url,
        event_type="concert",
        performers=[headliner],
        raw_title=headliner,
    )


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
        event.city.casefold(),
    )


def parse_events(html, *, today=None):
    soup = BeautifulSoup(html, "html.parser")
    events = {}
    # The separate ``block-artist-list-paris`` section repeats a subset of
    # these rows for the client-side Paris filter. Parse the canonical list.
    for row in soup.select(".block-artist-list"):
        event = parse_event_row(row, today=today)
        if event is not None:
            events[event_key(event)] = event
    return list(events.values())


def extract_dice_event_url(html):
    """Extract DICE's structured stable event identity from its event page."""

    soup = BeautifulSoup(html, "html.parser")
    retailer_id = soup.select_one(
        'meta[property="product:retailer_item_id"][content]'
    )
    event_id = clean_text(retailer_id.get("content")) if retailer_id else ""
    if re.fullmatch(r"[0-9a-f]{24}", event_id):
        return f"https://dice.fm/event/{event_id}"

    canonical = soup.select_one('link[rel="canonical"][href]')
    href = clean_text(canonical.get("href")) if canonical else ""
    parsed = urlparse(href)
    if (
        parsed.scheme in {"http", "https"}
        and parsed.netloc.casefold() in {"dice.fm", "www.dice.fm"}
        and re.fullmatch(r"/event/[^/]+/?", parsed.path)
    ):
        return urlunparse((
            "https", "dice.fm", parsed.path.rstrip("/"), "", "", "",
        ))
    return None


def resolve_dice_short_links(events):
    """Resolve bounded first-party redirects into DICE event identifiers."""

    candidates = [
        event
        for event in events
        if urlparse(event.ticket_url or "").netloc.casefold() == "link.dice.fm"
    ]
    for event in candidates[:DICE_SHORT_LINK_SAFETY_CEILING]:
        canonical_fallback = None
        for _attempt in range(DICE_SHORT_LINK_ATTEMPTS):
            try:
                response = requests.get(
                    event.ticket_url,
                    headers=HEADERS,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True,
                )
                response.raise_for_status()
            except requests.RequestException:
                continue
            resolved_url = extract_dice_event_url(response.text)
            if not resolved_url:
                continue
            if re.fullmatch(r"https://dice\.fm/event/[0-9a-f]{24}", resolved_url):
                event.ticket_url = resolved_url
                break
            canonical_fallback = resolved_url
        else:
            if canonical_fallback:
                event.ticket_url = canonical_fallback
    return events


def load_events(today=None):
    response = requests.get(EVENTS_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    events = resolve_dice_short_links(parse_events(response.text, today=today))
    print(f"Created {len(events)} Persona Grata ConcertEvent records")
    return events
