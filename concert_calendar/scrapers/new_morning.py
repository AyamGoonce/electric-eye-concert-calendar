import re
from datetime import date, datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "New Morning"

PROGRAMME_URL = "https://www.newmorning.com/"
REQUEST_TIMEOUT = 30
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}
EVENT_PATH_PATTERN = re.compile(r"^(\d{8})-\d+-.+\.html$")


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_card(link):
    href = clean_text(link.get("href"))
    match = EVENT_PATH_PATTERN.match(href)

    if not match:
        return None

    try:
        event_date = datetime.strptime(match.group(1), "%Y%m%d").date()
    except ValueError:
        return None

    if event_date < date.today():
        return None

    card = link.find_parent("div", class_="bg-white")
    title_element = card.select_one("h3") if card else None
    headliner = clean_text(title_element.get_text(" ", strip=True)) if title_element else ""

    if not headliner:
        return None

    return ConcertEvent(
        date=event_date.isoformat(),
        headliner=headliner,
        venue="New Morning",
        city="Paris",
        department="75",
        openers=None,
        promoters=None,
        genre=None,
        facebook_event_url=None,
        ticket_url=urljoin(PROGRAMME_URL, href),
    )


def event_key(event):
    return event.date, event.headliner.casefold(), event.venue.casefold()


def load_events():
    session = requests.Session()
    print("Downloading New Morning programme...")
    response = session.get(
        PROGRAMME_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events_by_key = {}

    for link in soup.select("a[href]"):
        event = parse_card(link)

        if event is not None:
            events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())
    print(f"Created {len(events)} New Morning ConcertEvent records")
    return events
