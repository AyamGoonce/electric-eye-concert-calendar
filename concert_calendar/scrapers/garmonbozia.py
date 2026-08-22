import re

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Garmonbozia"

EVENTS_URL = (
    "https://web.digitick.com/ext/billetterie5/"
    "index.php?site=garmonbozia"
)
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


def parse_lineup(value):
    artists = [
        clean_text(artist)
        for artist in clean_text(value).split("+")
        if clean_text(artist)
    ]

    if not artists:
        return "", None

    return artists[0], artists[1:6] or None


def parse_city(value):
    city = clean_text(value).lstrip("- ").strip()

    if re.fullmatch(
        r"paris(?:\s+\d{1,2})?",
        city,
        flags=re.IGNORECASE,
    ):
        return "Paris"

    return city


def parse_card(card):
    title_element = card.select_one(
        "dd .evenementNom"
    )
    date_element = card.select_one(
        "time[itemprop='startDate']"
    )
    venue_element = card.select_one(
        ".evenementSalleNom"
    )
    city_elements = card.select(
        ".evenementSalleVille"
    )
    genre_element = card.select_one(
        ".evenementSousGenre"
    )
    ticket_element = card.select_one(
        "a.evenementReserver[href]"
    )

    title = (
        clean_text(
            title_element.get_text(" ", strip=True)
        )
        if title_element
        else ""
    )
    headliner, openers = parse_lineup(title)
    event_date = (
        clean_text(date_element.get("datetime"))[:10]
        if date_element
        else ""
    )
    venue = (
        clean_text(
            venue_element.get_text(" ", strip=True)
        )
        if venue_element
        else ""
    )
    city = (
        parse_city(
            city_elements[-1].get_text(" ", strip=True)
        )
        if city_elements
        else ""
    )
    genre = (
        clean_text(
            genre_element.get_text(" ", strip=True)
        )
        if genre_element
        else None
    )
    ticket_url = (
        clean_text(ticket_element.get("href"))
        if ticket_element
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
        promoters=["Garmonbozia"],
        genre=genre or None,
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
        ".evenementListe > dl"
    )

    events_by_key = {}

    for card in cards:
        event = parse_card(card)

        if event is not None:
            events_by_key[event_key(event)] = event

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Garmonbozia ConcertEvent records"
    )

    return events
