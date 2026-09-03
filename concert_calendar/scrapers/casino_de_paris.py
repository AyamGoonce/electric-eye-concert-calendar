from datetime import date, datetime
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Casino de Paris"
PROGRAMME_URL = "https://www.casinodeparis.fr/fr"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
MONTHS = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5,
    "juin": 6, "juillet": 7, "août": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "décembre": 12,
}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _date_time(value):
    match = re.search(
        r"\b(\d{1,2})\s+([A-Za-zÀ-ÿ]+)\s+(\d{4})(?:\s*-\s*(\d{1,2}:\d{2}))?",
        value,
    )
    if not match:
        return None, None
    day, month_name, year, event_time = match.groups()
    month = MONTHS.get(month_name.casefold())
    if not month:
        return None, None
    try:
        event_date = date(int(year), month, int(day))
    except ValueError:
        return None, None
    return event_date, event_time


def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    programmes = [
        anchors.find_next_sibling("div", class_="next-events-content")
        for anchors in soup.select(".js-date-anchors")
    ]
    programmes = [programme for programme in programmes if programme]
    programme = max(programmes, key=lambda node: len(node.select(".card"))) if programmes else None
    if not programme:
        return []
    events = []
    for card in programme.select("li.cards-grid__item > .card"):
        category = card.select_one(".event-title")
        if _clean(category.get_text(" ", strip=True) if category else "").casefold() != "concert":
            continue
        action = card.select_one(".actions")
        action_text = _clean(action.get_text(" ", strip=True) if action else "")
        if re.search(r"\bannul[ée]\b", action_text, re.I):
            continue
        event_date, event_time = _date_time(_clean((card.select_one(".date") or card).get_text(" ", strip=True)))
        title_node = card.select_one("h3.title")
        link = card.select_one("a.js-main-link[href]")
        if not event_date or event_date < cutoff or not title_node or not link:
            continue
        headliner = _clean(title_node.get_text(" ", strip=True))
        if not headliner:
            continue
        sold_out = bool(re.search(r"\bcomplet\b", action_text, re.I))
        image = element_image_url(card.select_one(".image img"), base_url=PROGRAMME_URL)
        events.append(ConcertEvent(
            date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME,
            city="Paris", department="75", ticket_url=urljoin(PROGRAMME_URL, link["href"]),
            ticket_status="sold_out" if sold_out else "tickets", sold_out=sold_out,
            start_time=event_time, image_url=image, image_source=SOURCE_NAME if image else None,
        ))
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading Casino de Paris programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    unique = {}
    for event in parse_events(BeautifulSoup(response.text, "html.parser")):
        unique.setdefault((event.date, event.start_time, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} Casino de Paris ConcertEvent records")
    return result
