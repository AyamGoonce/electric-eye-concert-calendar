import re
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "La Cigale"

PROGRAMME_URL = "https://lacigale.fr/programmation/"
REQUEST_TIMEOUT = 30
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_card(card):
    event_type = clean_text(card.get("data-type")).casefold()
    genre = clean_text(card.get("data-genre"))
    card_text = clean_text(card.get_text(" ", strip=True)).casefold()
    title_element = card.select_one(".artiste-event__title")
    link = card.select_one("a.artiste-event__link[href]")
    headliner = clean_text(title_element.get_text(" ", strip=True)) if title_element else ""

    if event_type not in {"concert", "festival"}:
        return []

    if re.search(r"humour|one man show|theatre|conf[ée]rence", genre, re.IGNORECASE):
        return []

    if "annul" in card_text or not headliner or not link:
        return []

    event_dates = []

    for value in clean_text(card.get("data-date")).split():
        try:
            parsed = datetime.strptime(value, "%Y%m%d").date()
        except ValueError:
            continue

        if parsed >= date.today():
            event_dates.append(parsed)

    if event_type == "festival" and len(event_dates) > 1:
        return []

    return [
        ConcertEvent(
            date=event_date.isoformat(),
            headliner=headliner,
            venue="La Cigale",
            city="Paris",
            department="75",
            openers=None,
            promoters=None,
            genre=genre or None,
            facebook_event_url=None,
            ticket_url=clean_text(link.get("href")) or PROGRAMME_URL,
        )
        for event_date in event_dates
    ]


def event_key(event):
    return event.date, event.headliner.casefold(), event.venue.casefold()


def load_events():
    session = requests.Session()
    print("Downloading La Cigale programme...")
    response = session.get(
        PROGRAMME_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events_by_key = {}

    for card in soup.select(".artiste-event__item"):
        for event in parse_card(card):
            events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())
    print(f"Created {len(events)} La Cigale ConcertEvent records")
    return events
