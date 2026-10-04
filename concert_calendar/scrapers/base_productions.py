import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Base Productions"

EVENTS_URL = "https://www.base-productions.com/concerts/"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def parse_date(value):
    match = re.fullmatch(
        r"(\d{1,2})/(\d{1,2})/(\d{4})",
        clean_text(value),
    )

    if not match:
        return ""

    day, month, year = match.groups()

    try:
        return date(
            int(year),
            int(month),
            int(day),
        ).isoformat()
    except ValueError:
        return ""


def parse_lineup(value):
    """A listing title alone does not establish individual artists or roles."""
    return clean_text(value), None


def normalized_artist(value):
    value = clean_text(value).casefold()
    value = re.sub(r"^the\s+", "", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def detail_performers(html, title):
    """
    Confirm a spaced-'+' bill from explicit artist headings on the official
    Base Productions detail page. The title supplies display names/order;
    page headings are evidence only.
    """
    components = [
        clean_text(part)
        for part in re.split(r"\s+\+\s+", title or "")
        if clean_text(part)
    ]
    if len(components) < 2:
        return []

    soup = BeautifulSoup(html or "", "html.parser")
    evidenced = {
        normalized_artist(tag.get_text(" ", strip=True))
        for tag in soup.select("div.col-12.col-md-7 strong")
        if clean_text(tag.get_text(" ", strip=True))
    }

    if not evidenced:
        return []

    if all(normalized_artist(component) in evidenced for component in components):
        return components

    return []


def split_venue_city(value):
    value = clean_text(value)

    if " - " not in value:
        return "", ""

    venue, city = value.rsplit(" - ", 1)
    city = re.sub(
        r"\s*\([^)]*\)\s*$",
        "",
        city,
    )

    return clean_text(venue), clean_text(city)


def parse_card(card):
    detail_link = card.select_one(
        "a[href]:not(:has(img))"
    )
    paragraphs = card.select("p")

    title = (
        clean_text(
            detail_link.get_text(" ", strip=True)
        )
        if detail_link
        else ""
    )
    headliner, openers = parse_lineup(title)
    event_date = (
        parse_date(
            paragraphs[0].get_text(" ", strip=True)
        )
        if paragraphs
        else ""
    )
    location = (
        paragraphs[1].get_text(" ", strip=True)
        if len(paragraphs) > 1
        else ""
    )
    venue, city = split_venue_city(location)
    ticket_url = (
        clean_text(detail_link.get("href"))
        if detail_link
        else None
    )

    if not event_date:
        return None

    if not headliner:
        return None

    if not venue:
        return None

    if not city:
        return None

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="",
        openers=openers,
        promoters=["Base Productions"],
        genre=None,
        facebook_event_url=None,
        ticket_url=ticket_url or None,
    )


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
        event.city.casefold(),
    )


def load_events():
    session = requests.Session()

    print(f"Downloading {EVENTS_URL}...")

    response = session.get(
        EVENTS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )
    cards = soup.select(
        ".liste_concerts "
        ".wpgb-content-1.row > "
        ".col-12.col-md-3"
    )

    events_by_key = {}
    detail_cache = {}

    for card in cards:
        event = parse_card(card)

        if event is None:
            continue

        if (
            event.ticket_url
            and re.search(r"\s+\+\s+", event.headliner or "")
        ):
            if event.ticket_url not in detail_cache:
                try:
                    detail_response = session.get(
                        event.ticket_url,
                        headers=HEADERS,
                        timeout=REQUEST_TIMEOUT,
                    )
                    detail_response.raise_for_status()
                except requests.RequestException:
                    detail_cache[event.ticket_url] = []
                else:
                    detail_cache[event.ticket_url] = detail_performers(
                        detail_response.text,
                        event.headliner,
                    )

            performers = detail_cache.get(event.ticket_url) or []
            if performers:
                event.performers = performers
                event.raw_title = event.headliner

        events_by_key[event_key(event)] = event

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Base Productions ConcertEvent records"
    )

    return events
