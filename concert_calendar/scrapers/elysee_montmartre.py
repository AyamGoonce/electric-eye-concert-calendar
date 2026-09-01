import re
import unicodedata
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Élysée Montmartre"
PROGRAMME_URL = "https://www.elyseemontmartre.com/fr/programmation/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 6
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"}
MONTHS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def folded(value):
    return "".join(c for c in unicodedata.normalize("NFKD", clean(value)) if not unicodedata.combining(c)).casefold()


def parse_dates(value):
    normalized = folded(value)
    year_match = re.search(r"\b(20\d{2})\b", normalized)
    if not year_match:
        return []
    result = []
    for day, month_name in re.findall(r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\b", normalized):
        try:
            result.append(date(int(year_match.group(1)), MONTHS[month_name], int(day)))
        except ValueError:
            pass
    return result


def parse_card(card):
    title = card.select_one("a.link[href][title]")
    headliner = clean(title.get("title")) if title else ""
    dates = parse_dates(clean((card.select_one(".date") or card).get_text(" ", strip=True)))
    image_url = element_image_url(card.select_one(".visuel img"), base_url=PROGRAMME_URL)
    if not title or not headliner:
        return []
    return [ConcertEvent(date=d.isoformat(), headliner=headliner, venue=SOURCE_NAME, city="Paris", department="75", ticket_url=clean(title.get("href")), image_url=image_url, image_source=SOURCE_NAME if image_url else None) for d in dates if d >= date.today()]


def load_events():
    events = {}
    session = requests.Session()
    for page in range(1, MAX_PAGES + 1):
        url = PROGRAMME_URL if page == 1 else urljoin(PROGRAMME_URL, f"page/{page}/")
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(".bloc_extrait.evenement")
        if not cards:
            break
        for card in cards:
            for event in parse_card(card):
                events.setdefault((event.date, event.headliner.casefold(), event.venue.casefold()), event)
        if not soup.select_one("link[rel='next']"):
            break
    return discard_repeated_generic_images(list(events.values()))
