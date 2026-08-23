import re
import unicodedata
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "La Boule Noire"

PROGRAMME_URL = "https://laboule-noire.fr/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 12
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}
FRENCH_MONTHS = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12,
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def normalize(value):
    value = unicodedata.normalize("NFKD", clean_text(value))
    return "".join(character for character in value if not unicodedata.combining(character)).casefold()


def parse_event_date(value):
    normalized = normalize(value).replace("1er", "1")
    date_part = re.split(r"\s+[–-]\s+\d{1,2}(?::|h)", normalized, maxsplit=1)[0]
    numbers = re.findall(r"\b\d{1,4}\b", date_part)

    if len(numbers) != 2:
        return None

    match = re.search(r"\b(\d{1,2})\s+([a-z]+)\s+(20\d{2})\b", date_part)

    if not match:
        return None

    day_text, month_name, year_text = match.groups()
    month = FRENCH_MONTHS.get(month_name)

    if not month:
        return None

    try:
        return datetime(int(year_text), month, int(day_text)).date()
    except ValueError:
        return None


def parse_card(card):
    badge = normalize((card.select_one(".elementor-post__badge") or card).get_text(" ", strip=True))
    title_element = card.select_one(".elementor-post__title a[href]")
    date_element = card.select_one(".elementor-post__excerpt")
    headliner = clean_text(title_element.get_text(" ", strip=True)) if title_element else ""
    event_date = parse_event_date(date_element.get_text(" ", strip=True) if date_element else "")

    if "annul" in badge or "deplace" in badge or not headliner or not event_date:
        return None

    if event_date < date.today():
        return None

    return ConcertEvent(
        date=event_date.isoformat(),
        headliner=headliner,
        venue="La Boule Noire",
        city="Paris",
        department="75",
        openers=None,
        promoters=None,
        genre=None,
        facebook_event_url=None,
        ticket_url=clean_text(title_element.get("href")) or PROGRAMME_URL,
    )


def event_key(event):
    return event.date, event.headliner.casefold(), event.venue.casefold()


def load_events():
    session = requests.Session()
    events_by_key = {}
    seen_pages = set()
    page_url = PROGRAMME_URL

    for page_number in range(1, MAX_PAGES + 1):
        if page_url in seen_pages:
            break

        seen_pages.add(page_url)
        print(f"Downloading La Boule Noire page {page_number}...")
        response = session.get(page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("#programmation .elementor-post__card")

        if not cards:
            break

        for card in cards:
            event = parse_card(card)

            if event is not None:
                events_by_key.setdefault(event_key(event), event)

        anchor = soup.select_one("#programmation .e-load-more-anchor")
        next_page = clean_text(anchor.get("data-next-page")) if anchor else ""

        if not next_page or int(anchor.get("data-page", 0)) >= int(anchor.get("data-max-page", 0)):
            break

        page_url = next_page

    events = list(events_by_key.values())
    print(f"Created {len(events)} La Boule Noire ConcertEvent records")
    return events
