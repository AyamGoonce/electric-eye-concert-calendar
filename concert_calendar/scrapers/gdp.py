from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Gérard Drouot Productions"

GDP_EVENTS_URL = "https://www.gdp.fr/fr/agenda"
REQUEST_TIMEOUT = 30


def load_events():
    print(f"Downloading {GDP_EVENTS_URL}...")

    response = requests.get(
        GDP_EVENTS_URL,
        timeout=REQUEST_TIMEOUT,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Safari/537.36"
            )
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    event_cards = soup.select("div.gdpEvtCardCtnt")

    events = []

    for card in event_cards:
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

        genre = (
            genre_element.get_text(" ", strip=True)
            if genre_element
            else None
        )

        date = (
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
                ticket_url = urljoin(GDP_EVENTS_URL, href)

        if not headliner:
            continue

        event = ConcertEvent(
            date=date,
            headliner=headliner,
            venue=venue,
            city=city,
            department="",
            promoters=["GDP"],
            genre=genre,
            ticket_url=ticket_url,
        )

        events.append(event)

    print(f"Created {len(events)} GDP ConcertEvent records")

    return events
