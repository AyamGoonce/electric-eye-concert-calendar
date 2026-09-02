import re
import unicodedata
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import (
    discard_repeated_generic_images,
    element_image_url,
)
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Café de la Danse"
PROGRAMME_URL = "https://www.cafedeladanse.com/programmation/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 5
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
NON_MUSIC_CATEGORIES = {
    "conference",
    "danse",
    "enfants",
    "humour",
    "jeune public",
    "spectacle",
    "theatre",
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def clean_headliner(value):
    value = clean_text(value)
    return re.sub(
        r"\brelease[-‐‑‒–—]party\b",
        "Release Party",
        value,
        flags=re.IGNORECASE,
    )


def folded(value):
    normalized = unicodedata.normalize("NFKD", clean_text(value))
    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    ).casefold()


def parse_date(value):
    match = re.fullmatch(
        r"(\d{1,2})\s+(" + "|".join(FRENCH_MONTHS) + r")\s+(20\d{2})",
        folded(value),
    )
    if not match:
        return None
    day, month_name, year = match.groups()
    try:
        return date(int(year), FRENCH_MONTHS[month_name], int(day))
    except ValueError:
        return None


def parse_time(value):
    match = re.fullmatch(r"(\d{1,2})\s*h\s*(\d{2})", folded(value))
    if not match:
        return None
    hour, minute = (int(part) for part in match.groups())
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"


def category_names(card):
    return [
        clean_text(element.get_text(" ", strip=True))
        for element in card.select(".gt-location li a")
        if clean_text(element.get_text(" ", strip=True))
    ]


def is_music_event(categories):
    if not categories:
        return True
    return not all(folded(category) in NON_MUSIC_CATEGORIES for category in categories)


def ticket_details(card, detail_url):
    label_link = card.select_one(".gt-label a[href]")
    label = folded(label_link.get_text(" ", strip=True)) if label_link else ""
    price = folded(
        (card.select_one(".gt-price") or card).get_text(" ", strip=True)
    )

    if "complet" in label or "sold out" in label:
        status = "sold_out"
    elif "gratuit" in label or re.fullmatch(r"gratuit(?:e)?", price):
        status = "free"
    elif label in {"ticket", "tickets", "billet", "billets"}:
        status = "tickets"
    else:
        status = None

    ticket_url = (
        urljoin(PROGRAMME_URL, clean_text(label_link.get("href")))
        if label_link
        else detail_url
    )
    return ticket_url, status


def parse_card(card, *, today=None):
    title_link = card.select_one(".gt-title a[href]")
    headliner = clean_headliner(
        title_link.get_text(" ", strip=True)
    ) if title_link else ""
    event_date = parse_date(
        clean_text((card.select_one(".gt-date") or card).get_text(" ", strip=True))
    )
    categories = category_names(card)
    cutoff = today or date.today()

    if not headliner or event_date is None or event_date < cutoff:
        return None
    if not is_music_event(categories):
        return None

    detail_url = urljoin(PROGRAMME_URL, clean_text(title_link.get("href")))
    ticket_url, ticket_status = ticket_details(card, detail_url)
    image_url = element_image_url(
        card.select_one(".gt-image img"),
        base_url=PROGRAMME_URL,
    )

    return ConcertEvent(
        date=event_date.isoformat(),
        headliner=headliner,
        venue=SOURCE_NAME,
        city="Paris",
        department="75",
        genre=", ".join(categories) or None,
        ticket_url=ticket_url,
        ticket_status=ticket_status,
        sold_out=ticket_status == "sold_out",
        start_time=parse_time(
            clean_text((card.select_one(".gt-time") or card).get_text(" ", strip=True))
        ),
        image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
    )


def event_key(event):
    return event.date, folded(event.headliner), folded(event.venue)


def next_page_url(soup, current_url):
    link = soup.select_one("link[rel='next'][href], a.next[href], a[rel='next'][href]")
    return urljoin(current_url, clean_text(link.get("href"))) if link else None


def load_events():
    session = requests.Session()
    events = {}
    visited = set()
    page_url = PROGRAMME_URL

    for _ in range(MAX_PAGES):
        if not page_url or page_url in visited:
            break
        visited.add(page_url)
        print(f"Downloading Café de la Danse programme: {page_url}")
        response = session.get(page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(".gt-event-style-4")
        if not cards:
            break

        for card in cards:
            event = parse_card(card)
            if event is not None:
                events.setdefault(event_key(event), event)

        page_url = next_page_url(soup, page_url)

    result = discard_repeated_generic_images(list(events.values()))
    print(f"Created {len(result)} Café de la Danse ConcertEvent records")
    return result
