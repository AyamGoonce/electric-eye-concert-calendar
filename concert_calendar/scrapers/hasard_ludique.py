import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import background_image_url, discard_repeated_generic_images
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Le Hasard Ludique"

EVENTS_API_URL = "https://www.lehasardludique.paris/api/events"
SITE_URL = "https://www.lehasardludique.paris/"
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
        r"(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4})",
        clean_text(value),
    )

    if not match:
        return ""

    day_text, month_text, year_text = match.groups()
    year = int(year_text)

    if year < 100:
        year += 2000

    try:
        return date(year, int(month_text), int(day_text)).isoformat()
    except ValueError:
        return ""


def parse_card(card):
    link = card.select_one("a.event_card.concert")

    if link is None:
        return None

    title_element = link.select_one("h3")
    genre_element = link.select_one(".content > div > span")
    headliner = (
        clean_text(title_element.get_text(" ", strip=True))
        if title_element
        else ""
    )
    event_date = next(
        (
            parsed_date
            for element in link.select("strong")
            if (
                parsed_date := parse_date(
                    element.get_text(" ", strip=True)
                )
            )
        ),
        "",
    )
    href = clean_text(link.get("href"))

    if not event_date or not headliner or not href:
        return None

    image_element = link.select_one(".image[style]")
    image_url = background_image_url(
        image_element.get("style") if image_element else None,
        base_url=SITE_URL,
    )

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue="Le Hasard Ludique",
        city="Paris",
        department="75",
        openers=None,
        promoters=None,
        genre=(
            clean_text(genre_element.get_text(" ", strip=True))
            if genre_element
            else None
        ),
        facebook_event_url=None,
        ticket_url=urljoin(SITE_URL, href),
        image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
    )


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
    )


def load_events():
    session = requests.Session()

    print("Downloading Le Hasard Ludique ticketing events...")

    response = session.get(
        EVENTS_API_URL,
        params={
            "offset": 0,
            "limit": 100,
            "ticket_office_page": "true",
        },
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    events_by_key = {}

    for card_html in payload.get("items", []):
        soup = BeautifulSoup(card_html, "html.parser")
        event = parse_card(soup)

        if event is None:
            continue

        events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Le Hasard Ludique ConcertEvent records"
    )

    return discard_repeated_generic_images(events)
