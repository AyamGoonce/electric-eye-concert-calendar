from datetime import date
import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Alhambra"
PROGRAMME_URL = "https://www.alhambra-paris.com/"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
MONTHS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
          "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}
MUSIC_CATEGORIES = {
    "rock", "soul", "pop indie", "classique", "musique alternative inde",
    "country", "rai", "rnb pop", "r b soul", "pop country", "indie",
    "gospel", "pop electro", "afrobeat", "post punk", "pop latino", "pop",
    "rock metal", "pop rock", "hard rock metal punk", "musique du monde",
    "jazz", "k pop", "electro", "folk", "jazz blues", "rap hip hop",
    "reggae ska dub", "soul funk", "variete internationale", "variete francaise",
}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _key(value):
    value = unicodedata.normalize("NFKD", _clean(value).casefold())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in value if not unicodedata.combining(c))).strip()


def _parse_date(value):
    match = re.search(r"(\d{1,2})\s+([A-ZÀ-Ÿ]+)\s+(\d{4})", value.upper())
    if not match:
        return None
    day, month_name, year = match.groups()
    month = MONTHS.get(_key(month_name))
    if not month:
        return None
    try:
        return date(int(year), month, int(day))
    except ValueError:
        return None


def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    events = []
    for card in soup.select("#idmodulebillets .billet"):
        category_node = card.select_one(".categorie")
        category = _clean(category_node.get_text(" ", strip=True) if category_node else "")
        if _key(category) not in MUSIC_CATEGORIES:
            continue
        title_link = card.select_one(".bloctitresstitre h2 a[href]")
        date_node = card.select_one("p strong")
        if not title_link or not date_node:
            continue
        event_date = _parse_date(_clean(date_node.get_text(" ", strip=True)))
        if not event_date or event_date < cutoff:
            continue
        headliner = _clean(title_link.get_text(" ", strip=True))
        if not headliner:
            continue
        sold_out = bool(re.search(r"\bCOMPLET\b", card.get_text(" ", strip=True), re.I))
        image = element_image_url(card.select_one(".photo img"), base_url=PROGRAMME_URL)
        events.append(ConcertEvent(
            date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME,
            city="Paris", department="75", genre=category,
            ticket_url=urljoin(PROGRAMME_URL, title_link["href"]),
            ticket_status="sold_out" if sold_out else "tickets", sold_out=sold_out,
            image_url=image, image_source=SOURCE_NAME if image else None,
        ))
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading Alhambra programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    unique = {}
    for event in parse_events(BeautifulSoup(response.text, "html.parser")):
        unique.setdefault((event.date, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} Alhambra ConcertEvent records")
    return result
