from datetime import date, timedelta
import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Le Dôme de Paris"
PROGRAMME_URL = "https://www.ledomedeparis.com/fr/spectacles/a-laffiche"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
MONTHS = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5,
    "juin": 6, "juillet": 7, "aout": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "decembre": 12,
}
STATUS_ONLY_TITLES = {"concert reporte", "concert annule", "spectacle reporte", "spectacle annule"}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _key(value):
    value = unicodedata.normalize("NFKD", _clean(value).casefold())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in value if not unicodedata.combining(c))).strip()


def _dates(value):
    normalized = _key(value)
    single = re.search(r"\b(\d{1,2})\s+([a-z]+)\s+(\d{4})\b", normalized)
    ranged = re.search(
        r"\bdu\s+(\d{1,2})(?:\s+([a-z]+))?\s+au\s+(\d{1,2})\s+([a-z]+)\s+(\d{4})\b",
        normalized,
    )
    try:
        if ranged:
            start_day, start_month_name, end_day, end_month_name, year = ranged.groups()
            end_month = MONTHS[end_month_name]
            start_month = MONTHS[start_month_name] if start_month_name else end_month
            start = date(int(year), start_month, int(start_day))
            end = date(int(year), end_month, int(end_day))
            if end < start or (end - start).days > 31:
                return []
            return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]
        if single:
            day, month_name, year = single.groups()
            return [date(int(year), MONTHS[month_name], int(day))]
    except (KeyError, ValueError):
        pass
    return []


def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    events = []
    for content in soup.select(".spectacle-content"):
        paragraph = content.select_one("p")
        title_link = content.select_one("h4 a[href]")
        if not paragraph or not title_link:
            continue
        parts = list(paragraph.stripped_strings)
        if not parts or _key(parts[0]) != "concert":
            continue
        headliner = _clean(title_link.get_text(" ", strip=True))
        if not headliner or _key(headliner) in STATUS_ONLY_TITLES:
            continue
        card = content.parent
        image = element_image_url(card.select_one("a.illus-img img"), base_url=PROGRAMME_URL)
        ticket_url = urljoin(PROGRAMME_URL, title_link["href"])
        for event_date in _dates(" ".join(parts[1:])):
            if event_date < cutoff:
                continue
            events.append(ConcertEvent(
                date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME,
                city="Paris", department="75", ticket_url=ticket_url,
                ticket_status="tickets", image_url=image,
                image_source=SOURCE_NAME if image else None,
            ))
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading Le Dôme de Paris programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    unique = {}
    for event in parse_events(BeautifulSoup(response.text, "html.parser")):
        unique.setdefault((event.date, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} Le Dôme de Paris ConcertEvent records")
    return result
