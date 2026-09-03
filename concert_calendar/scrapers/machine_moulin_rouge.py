from datetime import date, datetime
import re

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "La Machine du Moulin Rouge"
PROGRAMME_URL = "https://www.lamachinedumoulinrouge.com/agenda/"
REQUEST_TIMEOUT = 30
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36"
    )
}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    events = []
    for card in soup.select("article.evenement-item"):
        classes = set(card.get("class") or [])
        category = _clean(
            (card.select_one("#tyevtagenda") or card).get_text(" ", strip=True)
        ).casefold()
        if "typevt-concert" not in classes and category != "concert":
            continue

        time_node = card.select_one("time[datetime]")
        title_node = card.select_one(".titevtagenda")
        detail_link = card.select_one("a.lkagenavt[href]")
        if not time_node or not title_node or not detail_link:
            continue
        try:
            starts_at = datetime.fromisoformat(time_node["datetime"])
        except (ValueError, TypeError):
            continue
        if starts_at.date() < cutoff:
            continue
        headliner = _clean(title_node.get_text(" ", strip=True))
        if not headliner:
            continue

        sold_out = "billetterie-complet" in classes
        image = element_image_url(card.select_one(".evenement-image img"), base_url=PROGRAMME_URL)
        events.append(
            ConcertEvent(
                date=starts_at.date().isoformat(),
                headliner=headliner,
                venue=SOURCE_NAME,
                city="Paris",
                department="75",
                ticket_url=detail_link["href"],
                ticket_status="sold_out" if sold_out else "tickets",
                sold_out=sold_out,
                start_time=starts_at.strftime("%H:%M"),
                image_url=image,
                image_source=SOURCE_NAME if image else None,
            )
        )
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading La Machine du Moulin Rouge agenda: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    unique = {}
    for event in parse_events(BeautifulSoup(response.text, "html.parser")):
        unique.setdefault((event.date, event.start_time, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(unique.values()))
    print(f"Created {len(result)} La Machine du Moulin Rouge ConcertEvent records")
    return result
