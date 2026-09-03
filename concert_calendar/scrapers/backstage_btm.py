import re
import unicodedata
from datetime import date, datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import (
    discard_repeated_generic_images,
    element_image_url,
)
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Backstage By The Mill"
PROGRAMME_URL = "https://www.backstage-btm.com/agenda/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 12
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}
NON_CONCERT_TYPES = {
    "club", "clubbing", "dj", "dj set", "event", "private event", "soiree",
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def folded(value):
    normalized = unicodedata.normalize("NFKD", clean_text(value))
    return "".join(
        character for character in normalized
        if not unicodedata.combining(character)
    ).casefold()


def parse_date(value):
    try:
        return datetime.strptime(clean_text(value), "%d/%m/%Y").date()
    except ValueError:
        return None


def parse_card(card, *, today=None):
    headliner = clean_text(
        (card.select_one(".event-title") or card).get_text(" ", strip=True)
    )
    event_date = parse_date(
        (card.select_one(".event-booking") or card).get_text(" ", strip=True)
    )
    event_type = clean_text(
        (card.select_one(".event-type") or card).get_text(" ", strip=True)
    )
    detail_link = card.select_one(".see-event a[href]")
    cutoff = today or date.today()

    if not headliner or event_date is None or event_date < cutoff:
        return None
    if folded(event_type) in NON_CONCERT_TYPES:
        return None

    detail_url = (
        urljoin(PROGRAMME_URL, clean_text(detail_link.get("href")))
        if detail_link else None
    )
    image_url = element_image_url(
        card.select_one(".visu-event-list img"), base_url=PROGRAMME_URL
    )
    status_text = folded(
        (card.select_one(".statut") or card).get_text(" ", strip=True)
    )
    if "complet" in status_text:
        ticket_status = "sold_out"
    elif "gratuit" in status_text:
        ticket_status = "free"
    else:
        ticket_status = "tickets" if detail_url else None

    return ConcertEvent(
        date=event_date.isoformat(),
        headliner=headliner,
        venue=SOURCE_NAME,
        city="Paris",
        department="75",
        genre=event_type or None,
        ticket_url=detail_url,
        ticket_status=ticket_status,
        sold_out=ticket_status == "sold_out",
        image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
    )


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
        print(f"Downloading Backstage By The Mill agenda: {page_url}")
        response = session.get(page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(".list-all-events > li")
        if not cards:
            break
        for card in cards:
            event = parse_card(card)
            if event is not None:
                key = (event.date, folded(event.headliner), folded(event.venue))
                events.setdefault(key, event)
        page_url = next_page_url(soup, page_url)

    result = discard_repeated_generic_images(list(events.values()))
    print(f"Created {len(result)} Backstage By The Mill ConcertEvent records")
    return result
