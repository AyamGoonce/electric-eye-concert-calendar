import re

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Radical Production"

EVENTS_URL = "https://radical-production.fr/concerts/"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


MONTHS = {
    "janv.": 1,
    "févr.": 2,
    "mars": 3,
    "avr.": 4,
    "mai": 5,
    "juin": 6,
    "juil.": 7,
    "août": 8,
    "sept.": 9,
    "oct.": 10,
    "nov.": 11,
    "déc.": 12,
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def parse_date(value):
    """
    Convert Radical dates such as '28 août 2026'
    or '04 sept. 2026' into YYYY-MM-DD.
    """

    value = clean_text(value).casefold()
    parts = value.split()

    if len(parts) != 3:
        return ""

    day, month, year = parts

    month_number = MONTHS.get(month)

    if month_number is None:
        return ""

    try:
        day_number = int(day)
        year_number = int(year)
    except ValueError:
        return ""

    return (
        f"{year_number:04d}-"
        f"{month_number:02d}-"
        f"{day_number:02d}"
    )


def find_ticket_url(card):
    link = card.select_one(
        ".concert-card__link[href]"
    )

    if not link:
        return None

    href = clean_text(link.get("href"))

    return href or None


def parse_card(card):
    date_element = card.select_one(
        ".concert-card__date"
    )
    artist_element = card.select_one(
        ".concert-card__title"
    )
    city_element = card.select_one(
        ".concert-card__place_m"
    )
    venue_element = card.select_one(
        ".concert-card__event"
    )

    event_date = (
        parse_date(
            date_element.get_text(" ", strip=True)
        )
        if date_element
        else ""
    )

    headliner = (
        clean_text(
            artist_element.get_text(" ", strip=True)
        )
        if artist_element
        else ""
    )

    city = (
        clean_text(
            city_element.get_text(" ", strip=True)
        )
        if city_element
        else ""
    )

    venue = (
        clean_text(
            venue_element.get_text(" ", strip=True)
        )
        if venue_element
        else ""
    )

    if not event_date:
        return None

    if not headliner:
        return None

    if not city:
        return None

    if not venue:
        return None

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="",
        openers=None,
        promoters=["Radical Production"],
        genre=None,
        facebook_event_url=None,
        ticket_url=find_ticket_url(card),
    )


def load_events():
    print(f"Downloading {EVENTS_URL}...")

    response = requests.get(
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
        ".concert-card"
    )

    events = []

    for card in cards:
        event = parse_card(card)

        if event is not None:
            events.append(event)

    print(
        f"Created {len(events)} "
        "Radical Production ConcertEvent records"
    )

    return events
