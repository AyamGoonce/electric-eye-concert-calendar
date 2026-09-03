from datetime import date
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, official_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "La Bellevilloise"
PROGRAMME_URL = "https://www.labellevilloise.com/agenda/"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
CONCERT_CATEGORIES = {"concert", "cafe-concert"}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    events = []
    for card in soup.select("article.c-tile[data-categories]"):
        categories = {item for item in card.get("data-categories", "").split(";") if item}
        if not categories.intersection(CONCERT_CATEGORIES):
            continue
        month_token = next((item for item in categories if re.fullmatch(r"\d{4}-\d{2}", item)), None)
        date_node = card.select_one(".c-tile_date")
        title_node = card.select_one(".c-tile_title")
        detail_link = card.select_one("a.c-link[href]")
        if not month_token or not date_node or not title_node or not detail_link:
            continue
        day_match = re.search(r"\b(\d{1,2})\b", _clean(date_node.get_text(" ", strip=True)))
        if not day_match:
            continue
        year, month = map(int, month_token.split("-"))
        try:
            event_date = date(year, month, int(day_match.group(1)))
        except ValueError:
            continue
        if event_date < cutoff:
            continue
        headliner = _clean(title_node.get_text(" ", strip=True))
        if not headliner:
            continue
        image_node = card.select_one(".c-tile_visual img")
        image = official_image_url(urljoin(PROGRAMME_URL, image_node.get("src", ""))) if image_node else None
        events.append(
            ConcertEvent(
                date=event_date.isoformat(),
                headliner=headliner,
                venue=SOURCE_NAME,
                city="Paris",
                department="75",
                ticket_url=detail_link["href"],
                image_url=image,
                image_source=SOURCE_NAME if image else None,
            )
        )
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading La Bellevilloise agenda: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    unique = {}
    for event in parse_events(BeautifulSoup(response.text, "html.parser")):
        unique.setdefault((event.date, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} La Bellevilloise ConcertEvent records")
    return result
