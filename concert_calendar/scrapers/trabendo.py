import re
import unicodedata
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Le Trabendo"
PROGRAMME_URL = "https://www.letrabendo.net/programmation/"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"}
MONTHS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def folded(value):
    return "".join(c for c in unicodedata.normalize("NFKD", clean(value)) if not unicodedata.combining(c)).casefold()


def parse_date(value):
    match = re.search(r"\b(\d{1,2})\s+[―–-]?\s*([a-zéû]+)\s+(20\d{2})\b", folded(value))
    if not match or match.group(2) not in MONTHS:
        return None
    try:
        return date(int(match.group(3)), MONTHS[match.group(2)], int(match.group(1)))
    except ValueError:
        return None


def parse_card(card):
    if not card.select_one(".pastille.concert"):
        return None
    event_date = parse_date(clean((card.select_one(".date-event") or card).get_text(" ", strip=True)))
    title = card.select_one(".name-event")
    headliner = clean(title.get_text(" ", strip=True)) if title else ""
    if not event_date or event_date < date.today() or not headliner:
        return None
    image_url = element_image_url(card.select_one("picture img"), base_url=PROGRAMME_URL)
    href = urljoin(PROGRAMME_URL, clean(card.get("href")))
    return ConcertEvent(date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME, city="Paris", department="75", genre=clean((card.select_one(".style") or card).get_text(" ", strip=True)) or None, ticket_url=href, image_url=image_url, image_source=SOURCE_NAME if image_url else None)


def load_events():
    response = requests.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events = {}
    for card in soup.select("a.event"):
        if event := parse_card(card):
            events.setdefault((event.date, event.headliner.casefold(), event.venue.casefold()), event)
    return discard_repeated_generic_images(list(events.values()))
