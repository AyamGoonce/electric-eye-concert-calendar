import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent

GDP_EVENTS_URL = "https://www.gdp.fr/fr/agenda"


def load_events():
    print(f"Downloading {GDP_EVENTS_URL}...")

    response = requests.get(GDP_EVENTS_URL, timeout=30)
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

        headliner = artist_element.get_text(" ", strip=True) if artist_element else ""
        genre = genre_element.get_text(" ", strip=True) if genre_element else None
        date = date_element.get("datetime", "") if date_element else ""
        city = city_element.get_text(" ", strip=True) if city_element else ""
        venue = venue_element.get_text(" ", strip=True) if venue_element else ""

        ticket_url = None
        if link_element:
            href = link_element.get("href", "").strip()
            if href:
                if href.startswith("/"):
                    ticket_url = f"https://www.gdp.fr{href}"
                else:
                    ticket_url = href

        events.append(
            ConcertEvent(
                date=date,
                headliner=headliner,
                venue=venue,
                city=city,
                department="",
                promoters=["GDP"],
                genre=genre,
                ticket_url=ticket_url,
            )
        )

    print(f"Created {len(events)} ConcertEvent records")

    return events