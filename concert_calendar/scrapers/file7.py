import re

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "File7"

PROGRAMME_URL = "https://file7.com/fr/programme/programme.html"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def clean_text(value):
    if not value:
        return ""

    value = value.replace("\u200b", "")
    return re.sub(r"\s+", " ", value).strip()


def split_bill(value):
    value = re.sub(
        r"^(?:Soirées Fan Club|Café-Concert)\s*:\s*",
        "",
        clean_text(value),
        flags=re.IGNORECASE,
    )
    artists = [
        clean_text(part)
        for part in re.split(r"\s*\+\s*", value)
    ]
    artists = [artist for artist in artists if artist]

    if not artists:
        return "", None

    return artists[0], artists[1:] or None


def parse_card(card):
    link = card.select_one("a[href]")
    artist_element = card.select_one(".artistes")

    if link is None or artist_element is None:
        return None

    detail_url = clean_text(link.get("href"))
    date_match = re.search(
        r"/(\d{2})-(\d{2})-(\d{4})-\d{2}h\d{2}-",
        detail_url,
    )
    headliner, openers = split_bill(
        artist_element.get_text(" ", strip=True)
    )

    if not date_match or not headliner:
        return None

    day, month, year = date_match.groups()

    return ConcertEvent(
        date=f"{year}-{month}-{day}",
        headliner=headliner,
        venue="File7",
        city="Magny-le-Hongre",
        department="77",
        openers=openers,
        promoters=None,
        genre=None,
        facebook_event_url=None,
        ticket_url=detail_url,
    )


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
    )


def load_events():
    session = requests.Session()

    print("Downloading File7 concert programme...")

    response = session.get(
        PROGRAMME_URL,
        params={"filtre1": 4},
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    events_by_key = {}

    for card in soup.select(".zone_grille .bloc_show"):
        event = parse_card(card)

        if event is None:
            continue

        events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())

    print(f"Created {len(events)} File7 ConcertEvent records")

    return events
