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
    artists = [
        clean_text(artist)
        for artist in clean_text(value).split("+")
        if clean_text(artist)
    ]

    if not artists:
        return "", None

    openers = [
        artist
        for artist in artists[1:]
        if artist.casefold() not in {
            "guest",
            "guests",
        }
    ]

    return artists[0], openers[:5] or None


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

    for card in cards:
        event = parse_card(card)

        if event is not None:
            events_by_key[event_key(event)] = event

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Base Productions ConcertEvent records"
    )

    return events
