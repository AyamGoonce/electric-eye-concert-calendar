from datetime import date
import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Stade de France"
PROGRAMME_URL = "https://www.stadefrance.com/fr/billetteries/concerts"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
MONTHS = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12,
}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _key(value):
    value = unicodedata.normalize("NFKD", _clean(value).casefold())
    return "".join(character for character in value if not unicodedata.combining(character))


def _dates(value):
    text = _key(value)
    year_match = re.search(r"\b(20\d{2})\b", text)
    month_match = re.search(r"\b(" + "|".join(MONTHS) + r")\s+20\d{2}\b", text)
    if not year_match or not month_match:
        return []
    year = int(year_match.group(1))
    month = MONTHS[month_match.group(1)]
    prefix = text[:month_match.start()]
    days = [int(value) for value in re.findall(r"\b(\d{1,2})\b", prefix)]
    result = []
    for day in days:
        try:
            result.append(date(year, month, day))
        except ValueError:
            continue
    return list(dict.fromkeys(result))


def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    events = []
    for card in soup.select("li.event-agenda-card"):
        title_node = card.select_one(".event-agenda-card__title")
        date_node = card.select_one(".event-agenda-card__date")
        event_link = card.select_one(".event-agenda-card__title a[href]")
        if not title_node or not date_node or not event_link:
            continue
        title = _clean(title_node.get_text(" ", strip=True))
        actions = card.select(".event-agenda-card__actions a[href]")
        primary = actions[0] if actions else event_link
        action_text = _key(primary.get_text(" ", strip=True))
        sold_out = "complet" in action_text or "epuise" in action_text
        not_on_sale = "etre alerte" in action_text
        image = element_image_url(
            card.select_one(".event-agenda-card__media img"), base_url=PROGRAMME_URL
        )
        for event_date in _dates(date_node.get_text(" ", strip=True)):
            if event_date < cutoff:
                continue
            events.append(ConcertEvent(
                date=event_date.isoformat(), headliner=title, venue=SOURCE_NAME,
                city="Saint-Denis", department="93",
                ticket_url=urljoin(PROGRAMME_URL, primary["href"]),
                ticket_status=(
                    "sold_out" if sold_out else "not_on_sale" if not_on_sale else "tickets"
                ),
                sold_out=sold_out, image_url=image,
                image_source=SOURCE_NAME if image else None,
            ))
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading Stade de France concert programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    unique = {}
    for event in parse_events(BeautifulSoup(response.text, "html.parser")):
        unique.setdefault((event.date, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} Stade de France ConcertEvent records")
    return result
