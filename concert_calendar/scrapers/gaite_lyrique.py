import re
import unicodedata
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "La Gaîté Lyrique"
AGENDA_URL = "https://www.gaite-lyrique.net/agenda/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 7
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"}
MONTHS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def folded(value):
    return "".join(c for c in unicodedata.normalize("NFKD", clean(value)) if not unicodedata.combining(c)).casefold()


def parse_date(value):
    match = re.search(r"\b(\d{1,2})\s+([a-z]+)\s+(20\d{2})\b", folded(value))
    if not match or match.group(2) not in MONTHS:
        return None
    try:
        return date(int(match.group(3)), MONTHS[match.group(2)], int(match.group(1)))
    except ValueError:
        return None


def parse_card(card):
    categories = {folded(a.get_text(" ", strip=True)) for a in card.select(".event-categories a")}
    if "musique" not in categories:
        return None
    date_group = card.find_parent("li", class_="events-date")
    heading = date_group.select_one(":scope > h2.events-date-title") if date_group else None
    event_date = parse_date(heading.get_text(" ", strip=True) if heading else "")
    title = card.select_one(".event-title a[href]")
    headliner = clean(title.get_text(" ", strip=True)) if title else ""
    if not event_date or event_date < date.today() or not headliner:
        return None
    image_url = element_image_url(card.select_one(".media img"), base_url=AGENDA_URL)
    return ConcertEvent(date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME, city="Paris", department="75", ticket_url=clean(title.get("href")), image_url=image_url, image_source=SOURCE_NAME if image_url else None)


def load_events():
    events = {}
    session = requests.Session()
    for page in range(1, MAX_PAGES + 1):
        url = AGENDA_URL if page == 1 else urljoin(AGENDA_URL, f"page/{page}/")
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("article.event")
        if not cards:
            break
        for card in cards:
            if event := parse_card(card):
                events.setdefault((event.date, event.headliner.casefold(), event.venue.casefold()), event)
    return discard_repeated_generic_images(list(events.values()))
