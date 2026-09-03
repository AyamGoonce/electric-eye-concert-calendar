from datetime import date
import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent

SOURCE_NAME = "Adidas Arena"
PROGRAMME_URL = "https://www.adidasarena.com/programmation"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
MONTHS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}

def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()

def _key(value):
    value = unicodedata.normalize("NFKD", _clean(value).casefold())
    return "".join(c for c in value if not unicodedata.combining(c))

def _dates(value):
    text = _key(value)
    year_match = re.search(r"\b(20\d{2})\b", text)
    if not year_match:
        return []
    year = int(year_match.group(1))
    ranged = re.search(r"(?:du\s+)?(\d{1,2})(?:\s+([a-z]+))?\s+(?:&|au)\s+(\d{1,2})\s+([a-z]+)", text)
    single = re.search(r"\b(\d{1,2})\s+([a-z]+)\s+20\d{2}\b", text)
    try:
        if ranged:
            day1, month1, day2, month2 = ranged.groups()
            second_month = MONTHS[month2]
            first_month = MONTHS[month1] if month1 else second_month
            return [date(year, first_month, int(day1)), date(year, second_month, int(day2))]
        if single:
            day, month = single.groups()
            return [date(year, MONTHS[month], int(day))]
    except (KeyError, ValueError):
        pass
    return []

def _time(value):
    match = re.search(r"\b(\d{1,2})h(\d{2})\b", _key(value))
    return f"{int(match.group(1)):02d}:{match.group(2)}" if match else None

def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    events = []
    for card in soup.select(".app-programmation-card.concert"):
        type_node = card.select_one(".type")
        title_node = card.select_one("h2")
        date_node = card.select_one(".date")
        link = card.select_one("a.app-programmation-card__cta[href]")
        if (_clean(type_node.get_text(" ", strip=True) if type_node else "").casefold() != "concert" or not title_node or not date_node or not link):
            continue
        title = _clean(title_node.get_text(" ", strip=True))
        date_text = _clean(date_node.get_text(" ", strip=True))
        image = element_image_url(card.select_one(".app-programmation-card__visual img"), base_url=PROGRAMME_URL)
        sold_out = "complet" in _key(card.get_text(" ", strip=True))
        for event_date in dict.fromkeys(_dates(date_text)):
            if event_date >= cutoff:
                events.append(ConcertEvent(date=event_date.isoformat(), headliner=title, venue=SOURCE_NAME, city="Paris", department="75", start_time=_time(date_text), ticket_url=urljoin(PROGRAMME_URL, link["href"]), ticket_status="sold_out" if sold_out else "tickets", sold_out=sold_out, image_url=image, image_source=SOURCE_NAME if image else None))
    return events

def load_events():
    session = requests.Session()
    print(f"Downloading Adidas Arena programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    unique = {}
    for event in parse_events(BeautifulSoup(response.text, "html.parser")):
        unique.setdefault((event.date, event.start_time, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} Adidas Arena ConcertEvent records")
    return result
