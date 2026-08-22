import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Azimuth Productions"

EVENTS_URL = "https://azimuthprod.com/agenda/"
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


def parse_card(card):
    row = card.select_one(
        ".elementor-inner-section"
    )

    if row is None:
        return None

    columns = row.select(
        ":scope > .elementor-container > "
        ".elementor-inner-column"
    )

    if len(columns) < 4:
        return None

    artist_element = columns[0].select_one("h4")
    ticket_element = card.select_one(
        "a[href]"
    )

    headliner = (
        clean_text(
            artist_element.get_text(" ", strip=True)
        )
        if artist_element
        else ""
    )
    event_date = parse_date(
        columns[1].get_text(" ", strip=True)
    )
    venue = clean_text(
        columns[2].get_text(" ", strip=True)
    )
    city = clean_text(
        columns[3].get_text(" ", strip=True)
    )
    ticket_url = (
        clean_text(ticket_element.get("href"))
        if ticket_element
        else None
    )
    openers = None

    support_match = re.fullmatch(
        r"(.+?)\s+[–-]\s+"
        r"première partie de\s+"
        r"(.+?)(?:\s+[–-]\s+.*)?",
        venue,
        flags=re.IGNORECASE,
    )

    if support_match:
        venue, main_artist = support_match.groups()
        openers = [headliner]
        headliner = clean_text(main_artist)
        venue = clean_text(venue)

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
        promoters=["Azimuth Productions"],
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

    for page_number in range(1, 101):
        print(
            f"Downloading Azimuth page "
            f"{page_number}..."
        )

        response = session.get(
            EVENTS_URL,
            params={
                "sf_data": "results",
                "sf_paged": page_number,
            },
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )
        cards = soup.select("article")

        if not cards:
            break

        new_events = 0

        for card in cards:
            event = parse_card(card)

            if event is None:
                continue

            key = event_key(event)

            if key not in events_by_key:
                events_by_key[key] = event
                new_events += 1

        if new_events == 0:
            break

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Azimuth Productions ConcertEvent records"
    )

    return events
