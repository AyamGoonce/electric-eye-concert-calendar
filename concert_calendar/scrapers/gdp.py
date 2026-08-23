from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Gérard Drouot Productions"

GDP_EVENTS_URL = "https://www.gdp.fr/fr/agenda"
REQUEST_TIMEOUT = 30
MAX_PAGES = 50

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def normalize_date(value):
    return (value or "").split("T", 1)[0].strip()


def parse_card(card):
    artist_element = card.select_one(".gdpEvtCardName")
    genre_element = card.select_one(".gdpEvtCardGenre")
    date_element = card.select_one(".gdpEvtCardDate")
    city_element = card.select_one(".gdpEvtCardCity")
    venue_element = card.select_one(".gdpEvtCardVenue")
    link_element = card.select_one(".gdpEvtCardName a")

    headliner = (
        artist_element.get_text(" ", strip=True)
        if artist_element
        else ""
    )

    if not headliner:
        return None

    genre = (
        genre_element.get_text(" ", strip=True)
        if genre_element
        else None
    )

    event_date = normalize_date(
        date_element.get("datetime", "").strip()
        if date_element
        else ""
    )

    city = (
        city_element.get_text(" ", strip=True)
        if city_element
        else ""
    )

    venue = (
        venue_element.get_text(" ", strip=True)
        if venue_element
        else ""
    )

    ticket_url = None

    if link_element:
        href = link_element.get("href", "").strip()

        if href:
            ticket_url = urljoin(
                GDP_EVENTS_URL,
                href,
            )

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="",
        promoters=["GDP"],
        genre=genre,
        ticket_url=ticket_url,
    )


def load_events():
    session = requests.Session()
    session.headers.update(HEADERS)

    events = []
    seen = set()

    for page in range(1, MAX_PAGES + 1):
        print(
            f"Downloading {GDP_EVENTS_URL}"
            f"?page={page}..."
        )

        response = session.get(
            GDP_EVENTS_URL,
            params={"page": page},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )
        event_cards = soup.select(
            "div.gdpEvtCardCtnt"
        )

        if not event_cards:
            print(
                f"GDP pagination ended at page "
                f"{page}: no event cards"
            )
            break

        added = 0

        for card in event_cards:
            event = parse_card(card)

            if event is None:
                continue

            key = (
                event.date,
                event.headliner.casefold(),
                event.venue.casefold(),
                event.city.casefold(),
                event.ticket_url or "",
            )

            if key in seen:
                continue

            seen.add(key)
            events.append(event)
            added += 1

        print(
            f"GDP page {page}: "
            f"{len(event_cards)} cards, "
            f"{added} new events"
        )

        # GDP currently paginates in batches of 50.
        # A short page is the final page.
        if len(event_cards) < 50:
            print(
                f"GDP pagination ended at page "
                f"{page}: final short page"
            )
            break

        # Prevent looping forever if GDP ever repeats
        # the same page instead of returning an empty
        # or short final page.
        if added == 0:
            print(
                f"GDP pagination ended at page "
                f"{page}: no new events"
            )
            break

    else:
        raise RuntimeError(
            "GDP pagination exceeded "
            f"{MAX_PAGES} pages"
        )

    print(
        f"Created {len(events)} "
        f"GDP ConcertEvent records"
    )

    return events
