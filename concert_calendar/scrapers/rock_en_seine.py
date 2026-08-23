from __future__ import annotations

from collections import defaultdict
from datetime import date
import re

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Rock en Seine"
SOURCE_PRIORITY = -10

LINEUP_URL = "https://www.rockenseine.com/programmation/"
TICKET_URL = "https://www.rockenseine.com/billetterie/"
REQUEST_TIMEOUT = 30
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "Chrome/127.0 Safari/537.36"
    ),
}
MONTHS = {
    "janvier": 1,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12,
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_year(soup):
    heading = soup.select_one("h1")
    match = re.search(r"\b(20\d{2})\b", heading.get_text(" ", strip=True) if heading else "")

    if not match:
        raise RuntimeError("Rock en Seine lineup year is unavailable")

    return int(match.group(1))


def parse_card(card, year):
    date_element = card.select_one(".item-date")
    stage_element = card.select_one(".item-stage")
    artist_element = card.select_one("h3")

    if not date_element or not stage_element or not artist_element:
        return None

    date_text = clean_text(date_element.get_text(" ", strip=True))
    date_match = re.search(r"\b(\d{1,2})\s+([A-Za-zÀ-ÿ]+)\b", date_text)
    time_match = re.search(r"\b(\d{1,2}):(\d{2})\b", date_text)

    if not date_match or not time_match:
        return None

    month = MONTHS.get(date_match.group(2).casefold())

    if month is None:
        return None

    try:
        event_date = date(year, month, int(date_match.group(1))).isoformat()
    except ValueError:
        return None

    artist = clean_text(artist_element.get_text(" ", strip=True))
    stage = clean_text(stage_element.get_text(" ", strip=True))
    minutes = int(time_match.group(1)) * 60 + int(time_match.group(2))

    if not artist:
        return None

    return event_date, artist, stage, minutes


def parse_lineup(html):
    soup = BeautifulSoup(html, "html.parser")
    year = parse_year(soup)
    days = defaultdict(list)

    for position, card in enumerate(soup.select(".card-artist")):
        parsed = parse_card(card, year)

        if parsed is None:
            continue

        event_date, artist, stage, minutes = parsed
        days[event_date].append((position, artist, stage, minutes))

    events = []

    for event_date, lineup in sorted(days.items()):
        main_stage = [
            item for item in lineup if "grande scène" in item[2].casefold()
        ]

        if not main_stage:
            print(f"Ambiguous Rock en Seine billing on {event_date}: no Grande Scène")
            continue

        headliner_item = max(main_stage, key=lambda item: item[3])
        ordered = [headliner_item, *[item for item in lineup if item is not headliner_item]]

        events.append(
            ConcertEvent(
                date=event_date,
                headliner=headliner_item[1],
                venue="Rock en Seine",
                city="Saint-Cloud",
                department="92",
                openers=[item[1] for item in ordered[1:]] or None,
                promoters=None,
                genre=None,
                facebook_event_url=None,
                ticket_url=TICKET_URL,
                festival_name="Rock en Seine",
                authoritative_billing=True,
            )
        )

    if not events:
        raise RuntimeError("Rock en Seine returned no authoritative festival days")

    return events


def load_events():
    print(f"Downloading {LINEUP_URL}...")
    response = requests.get(LINEUP_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    events = parse_lineup(response.text)
    print(f"Created {len(events)} Rock en Seine festival-day ConcertEvent records")
    return events
