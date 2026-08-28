import re
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Le Trianon"
PROGRAMME_URL = "https://www.letrianon.fr/fr/programmation/"
REQUEST_TIMEOUT = 30
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

FRENCH_MONTHS = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
}
REVIEWED_BILLING = {
    "SAAZBUZZ JAZZ FESTIVAL": {
        "headliner": "SAAZBUZZ JAZZ FESTIVAL | 2nd édition",
    },
    "JAMES BAKER": {
        "headliner": "James Baker - Romy Tour",
    },
    "HASAN HATES RONNY | RONNY HATES HASAN": {
        "headliner": "Hasan Minhaj",
        "co_headliners": ["Ronny Chieng"],
    },
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_french_date(value):
    match = re.search(
        r"\b(\d{1,2})\s+(" + "|".join(FRENCH_MONTHS) + r")\s+(\d{4})\b",
        clean_text(value).casefold(),
    )
    if not match:
        return None
    return date(int(match.group(3)), FRENCH_MONTHS[match.group(2)], int(match.group(1)))


def parse_detail(session, url):
    response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    text = clean_text(soup.get_text(" ", strip=True))
    match = re.search(r"\b(?:à|a)\s+(\d{1,2})h(\d{2})\b", text, re.IGNORECASE)
    start_time = f"{int(match.group(1)):02d}:{match.group(2)}" if match else None
    return {"start_time": start_time}


def parse_card(card, session):
    title = card.select_one(".titre")
    date_node = card.select_one(".date")
    link = card.select_one("a.link[href]")
    image = card.select_one("img[src]")
    headliner = clean_text(title.get_text(" ", strip=True)) if title else ""
    event_date = parse_french_date(date_node.get_text(" ", strip=True) if date_node else "")
    detail_url = clean_text(link.get("href")) if link else ""
    if not headliner or not event_date or event_date < date.today() or not detail_url:
        return None

    classes = {clean_text(value).casefold() for value in card.get("class", [])}
    ticket_status = "cancelled" if "cancel" in classes else None
    sold_out = "full" in classes
    try:
        detail = parse_detail(session, detail_url)
    except requests.RequestException as exc:
        print(f"Le Trianon detail fetch failed for {detail_url}: {exc}")
        detail = {}

    image_url = clean_text(image.get("src")) if image else None
    billing = REVIEWED_BILLING.get(headliner, {})
    canonical_headliner = billing.get("headliner", headliner)
    return ConcertEvent(
        date=event_date.isoformat(),
        headliner=canonical_headliner,
        venue="Le Trianon",
        city="Paris",
        department="75",
        promoters=None,
        co_headliners=billing.get("co_headliners"),
        facebook_event_url=None,
        ticket_url=detail_url,
        sold_out=sold_out,
        ticket_status=ticket_status,
        start_time=detail.get("start_time"),
        image_url=image_url or None,
        image_source=SOURCE_NAME if image_url else None,
        event_title=headliner if canonical_headliner != headliner else None,
    )


def event_key(event):
    return event.date, event.headliner.casefold(), event.venue.casefold()


def load_events():
    session = requests.Session()
    print("Downloading Le Trianon programme...")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events_by_key = {}
    for card in soup.select(".bloc_extrait.evenement"):
        event = parse_card(card, session)
        if event:
            events_by_key.setdefault(event_key(event), event)
    events = list(events_by_key.values())
    print(f"Created {len(events)} Le Trianon ConcertEvent records")
    return events
