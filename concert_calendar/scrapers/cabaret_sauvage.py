from datetime import date, datetime
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Cabaret Sauvage"
PROGRAMME_URL = "https://www.cabaretsauvage.com/agenda"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    pane = soup.select_one('div[data-w-tab="Tab 1 (ALL)"]')
    if not pane:
        return []
    events = []
    for card in pane.select(".post-item-3.w-dyn-item"):
        category_node = card.select_one(".category-link")
        if _clean(category_node.get_text(" ", strip=True) if category_node else "").casefold() != "concert":
            continue
        date_node = card.select_one(".post-date")
        title_node = card.select_one(".work-title")
        detail_link = card.select_one('a[href^="/work/"]')
        if not date_node or not title_node or not detail_link:
            continue
        match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{2})", _clean(date_node.get_text()))
        if not match:
            continue
        try:
            event_date = datetime.strptime(".".join(match.groups()), "%d.%m.%y").date()
        except ValueError:
            continue
        if event_date < cutoff:
            continue
        title = _clean(title_node.get_text(" ", strip=True))
        sold_out = bool(re.search(r"\s*-\s*COMPLET\s*$", title, re.I))
        headliner = _clean(re.sub(r"\s*-\s*COMPLET\s*$", "", title, flags=re.I))
        if not headliner:
            continue
        image = element_image_url(card.select_one("img.image-hover"), base_url=PROGRAMME_URL)
        detail_url = urljoin(PROGRAMME_URL, detail_link["href"])
        events.append(
            ConcertEvent(
                date=event_date.isoformat(),
                headliner=headliner,
                venue=SOURCE_NAME,
                city="Paris",
                department="75",
                ticket_url=detail_url,
                ticket_status="sold_out" if sold_out else None,
                sold_out=sold_out,
                image_url=image,
                image_source=SOURCE_NAME if image else None,
            )
        )
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading Cabaret Sauvage agenda: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    unique = {}
    for event in parse_events(BeautifulSoup(response.text, "html.parser")):
        unique.setdefault((event.date, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} Cabaret Sauvage ConcertEvent records")
    return result
