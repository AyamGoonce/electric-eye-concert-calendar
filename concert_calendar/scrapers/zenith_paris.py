import re
import unicodedata
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Le Zénith Paris – La Villette"
PROGRAMME_URL = "https://le-zenith.com/"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"}
MONTHS = {"janv": 1, "fevr": 2, "mars": 3, "avr": 4, "mai": 5, "juin": 6, "juil": 7, "aout": 8, "sept": 9, "oct": 10, "nov": 11, "dec": 12}


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def folded(value):
    return "".join(c for c in unicodedata.normalize("NFKD", clean(value)) if not unicodedata.combining(c)).casefold()


def parse_date(value):
    match = re.search(r"\b(\d{1,2})\s+([a-z]+)\.?\s+(20\d{2})\b", folded(value))
    month = MONTHS.get(match.group(2)[:4]) if match else None
    if not match or not month:
        return None
    try:
        return date(int(match.group(3)), month, int(match.group(1)))
    except ValueError:
        return None


def parse_card(card):
    title = card.select_one(".swiper-caption__name")
    date_element = card.select_one(".swiper-caption__date")
    link = card.select_one("a[href*='/shows/']")
    headliner = clean(title.get_text(" ", strip=True)) if title else ""
    event_date = parse_date(date_element.get_text(" ", strip=True) if date_element else "")
    if not event_date or event_date < date.today() or not headliner or not link:
        return None
    image_url = element_image_url(card.select_one("img"), base_url=PROGRAMME_URL)
    return ConcertEvent(date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME, city="Paris", department="75", ticket_url=urljoin(PROGRAMME_URL, clean(link.get("href"))), image_url=image_url, image_source=SOURCE_NAME if image_url else None)


def load_events():
    response = requests.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events = {}
    for card in soup.select(".swiper-home-current-event .swiper-slide"):
        if event := parse_card(card):
            events.setdefault((event.date, event.headliner.casefold(), event.venue.casefold()), event)
    return discard_repeated_generic_images(list(events.values()))
