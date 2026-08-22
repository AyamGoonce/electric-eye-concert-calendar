import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Zouave"

EVENTS_URL = "https://www.zouave.net/concerts/"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

MONTHS = {
    "janvier": 1,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12,
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def parse_date(value):
    parts = clean_text(value).casefold().split()

    if len(parts) != 3:
        return ""

    day, month_name, year = parts
    month = MONTHS.get(month_name)

    if month is None:
        return ""

    try:
        return date(
            int(year),
            month,
            int(day),
        ).isoformat()
    except ValueError:
        return ""


def parse_city(value):
    city = clean_text(value)
    city = re.sub(
        r"\s*\([^)]*\)\s*$",
        "",
        city,
    )

    return city.strip()


def is_cancelled(card):
    text = clean_text(
        card.get_text(" ", strip=True)
    ).casefold()

    return bool(
        re.search(r"\bannul[ée]e?\b", text)
    )


def parse_card(card):
    if is_cancelled(card):
        return None

    date_element = card.select_one(
        ".concert-date"
    )
    artist_element = card.select_one(
        ".concert-lien .title-concert"
    )
    city_element = card.select_one(
        ".concert-ville"
    )
    venue_element = card.select_one(
        ".concert-salle"
    )
    ticket_element = card.select_one(
        "a.lien-ticket[href]"
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
        parse_city(
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
    ticket_url = (
        clean_text(ticket_element.get("href"))
        if ticket_element
        else None
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
        promoters=["Zouave"],
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
    events_by_key = {}
    visited_pages = set()
    page_url = EVENTS_URL

    while (
        page_url
        and page_url not in visited_pages
        and len(visited_pages) < 100
    ):
        visited_pages.add(page_url)

        print(f"Downloading {page_url}...")

        response = session.get(
            page_url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )
        cards = soup.select(
            "article.container-concerts"
        )

        for card in cards:
            event = parse_card(card)

            if event is not None:
                events_by_key[event_key(event)] = event

        next_link = soup.select_one(
            "nav.pagination a.next[href]"
        )

        if next_link:
            next_href = clean_text(
                next_link.get("href")
            )
            page_url = (
                urljoin(page_url, next_href)
                if next_href
                else None
            )
        else:
            page_url = None

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Zouave ConcertEvent records"
    )

    return events
