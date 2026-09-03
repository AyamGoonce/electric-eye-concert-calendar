import re
from datetime import date, datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import (
    discard_repeated_generic_images,
    element_image_url,
)
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Glazart"
PROGRAMME_URL = (
    "https://www.glazart.com/agenda-concerts/portfolio-category/concert/"
)
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
TITLE_RE = re.compile(
    r"^(\d{2}\.\d{2}\.\d{2})\s*[–—-]\s*Concert\s*:\s*(.+)$",
    re.IGNORECASE,
)


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_card(card, *, today=None):
    link = None
    match = None
    for candidate in card.select("a.item-link[href]"):
        candidate_match = TITLE_RE.match(
            clean_text(candidate.get_text(" ", strip=True))
        )
        if candidate_match:
            link = candidate
            match = candidate_match
            break
    if not match:
        return None
    try:
        event_date = datetime.strptime(match.group(1), "%d.%m.%y").date()
    except ValueError:
        return None
    if event_date < (today or date.today()):
        return None
    headliner = clean_text(match.group(2))
    if not headliner:
        return None
    detail_url = urljoin(PROGRAMME_URL, link.get("href"))
    image_url = element_image_url(card.select_one("img"), base_url=PROGRAMME_URL)
    if image_url and "blank-admat" in image_url.casefold():
        image_url = None
    return ConcertEvent(
        date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME,
        city="Paris", department="75", ticket_url=detail_url,
        ticket_status="tickets", image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
    )


def load_events():
    session = requests.Session()
    print(f"Downloading Glazart concert programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events = {}
    for card in soup.select(".portfolio-item[data-terms~='concert']"):
        event = parse_card(card)
        if event is not None:
            events.setdefault((event.date, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(events.values()))
    print(f"Created {len(result)} Glazart ConcertEvent records")
    return result
