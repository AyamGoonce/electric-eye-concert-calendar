import re
import unicodedata
from datetime import date
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "La Maroquinerie"

AGENDA_URL = "https://www.lamaroquinerie.fr/fr/agenda/"
RESULTS_URL = "https://www.lamaroquinerie.fr/fr/agenda/results/"
SITE_URL = "https://www.lamaroquinerie.fr/"
REQUEST_TIMEOUT = 30
PAGE_SIZE = 50

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

FRENCH_MONTHS = {
    "janvier": 1,
    "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12,
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def normalize_for_matching(value):
    normalized = unicodedata.normalize("NFKD", clean_text(value))
    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    ).casefold()


def parse_day_month(value):
    match = re.fullmatch(
        r"(\d{1,2})\s+([a-z]+)",
        normalize_for_matching(value),
    )

    if not match:
        return None

    day_text, month_name = match.groups()
    month = FRENCH_MONTHS.get(month_name)

    if not month:
        return None

    return int(day_text), month


def parse_card(card, year):
    title_element = card.select_one(".thumbnail h2")
    date_element = card.select_one("h3.date")
    detail_link = card.select_one("a[href*='/agenda/view/']")
    ticket_link = card.select_one(".booking a[href]")
    booking_text = normalize_for_matching(
        (card.select_one(".booking") or card).get_text(" ", strip=True)
    )
    headliner = (
        clean_text(title_element.get_text(" ", strip=True))
        if title_element
        else ""
    )
    day_month = parse_day_month(
        date_element.get_text(" ", strip=True)
        if date_element
        else ""
    )

    if "annul" in booking_text or "annulation" in normalize_for_matching(headliner):
        return None

    headliner = re.sub(
        r"\s+-\s+(?:COMPLET|REPORTÉ|REPORTE)$",
        "",
        headliner,
        flags=re.IGNORECASE,
    ).strip()

    if not headliner or not day_month:
        return None

    day, month = day_month

    try:
        event_date = date(year, month, day).isoformat()
    except ValueError:
        return None

    if ticket_link and clean_text(ticket_link.get("href")) in {"", "/"}:
        ticket_link = None

    ticket_href = (
        clean_text(ticket_link.get("href"))
        if ticket_link
        else ""
    )
    ticket_hostname = (urlparse(ticket_href).hostname or "").casefold()
    facebook_event_url = (
        ticket_href
        if ticket_hostname == "facebook.com" or ticket_hostname.endswith(".facebook.com")
        else None
    )
    available_link = (
        detail_link
        if facebook_event_url
        else ticket_link or detail_link
    )
    image_url = element_image_url(card.select_one(".thumbnail img"), base_url=SITE_URL)

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue="La Maroquinerie",
        city="Paris",
        department="75",
        openers=None,
        promoters=None,
        genre=None,
        facebook_event_url=facebook_event_url,
        ticket_url=(
            urljoin(SITE_URL, clean_text(available_link.get("href")))
            if available_link
            else AGENDA_URL
        ),
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

    print("Downloading La Maroquinerie agenda...")

    response = session.get(
        AGENDA_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.select_one("ul.infiniteScroll")

    if container is None:
        return []

    total = int(container.get("data-total", 0))
    cards = list(container.select("li.event"))

    for offset in range(PAGE_SIZE, total, PAGE_SIZE):
        print(f"Downloading La Maroquinerie offset {offset}...")

        page_response = session.get(
            RESULTS_URL,
            params={"of": offset},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        page_response.raise_for_status()
        page_soup = BeautifulSoup(page_response.text, "html.parser")
        page_cards = page_soup.select("li.event")

        if not page_cards:
            break

        cards.extend(page_cards)

    events_by_key = {}
    current_year = date.today().year
    previous_month = date.today().month

    for card in cards:
        date_element = card.select_one("h3.date")
        day_month = parse_day_month(
            date_element.get_text(" ", strip=True)
            if date_element
            else ""
        )

        if day_month is None:
            continue

        _, month = day_month

        if month < previous_month:
            current_year += 1

        previous_month = month
        event = parse_card(card, current_year)

        if event is None:
            continue

        events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "La Maroquinerie ConcertEvent records"
    )

    return discard_repeated_generic_images(events)
