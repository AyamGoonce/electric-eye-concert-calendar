import json
import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "La Seine Musicale"
PROGRAMME_URL = "https://www.laseinemusicale.com/programmation/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

# Official programme taxonomy IDs for non-classical music concerts.
INCLUDED_GENRES = {
    "140": "Electro, Techno",
    "133": "Hard Rock, Metal",
    "132": "Jazz, Musiques du monde",
    "168": "K-pop",
    "128": "Pop, Rock",
    "147": "Rap, Hip-Hop, RnB",
    "15": "Soul, Funk",
    "145": "Variété française",
    "151": "Variété internationale",
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def clean_headliner(value):
    """Remove an unnamed ensemble suffix used by the venue as show copy."""

    return re.sub(
        r"\s*&\s*Orchestra$",
        "",
        clean_text(value),
        flags=re.IGNORECASE,
    ).strip()


def parse_event_schema(soup):
    for element in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(element.string or element.get_text())
        except (TypeError, json.JSONDecodeError):
            continue

        candidates = payload if isinstance(payload, list) else [payload]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("@type") == "Event":
                return candidate

    return None


def extract_special_guests(soup, headliner):
    guests = []
    for paragraph in soup.find_all("p"):
        text = clean_text(paragraph.get_text(" ", strip=True)).casefold()
        if "invité spécial" not in text and "invités spéciaux" not in text:
            continue
        for strong in paragraph.find_all("strong"):
            artist = clean_text(strong.get_text(" ", strip=True))
            if artist and artist.casefold() != headliner.casefold() and artist not in guests:
                guests.append(artist)
    return guests or None


def parse_detail(html, detail_url, raw_genres):
    soup = BeautifulSoup(html, "html.parser")
    schema = parse_event_schema(soup)
    if not schema:
        return []

    headliner = clean_headliner(schema.get("name"))
    if not headliner:
        return []

    offers = schema.get("offers") or {}
    if isinstance(offers, list):
        offers = next((item for item in offers if isinstance(item, dict)), {})
    ticket_url = clean_text(offers.get("url")) or detail_url
    image_url = schema.get("image")
    if isinstance(image_url, list):
        image_url = next((item for item in image_url if isinstance(item, str)), None)

    meetings = {}
    for element in soup.select("[data-meeting-date]"):
        value = clean_text(element.get("data-meeting-date"))
        match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}):\d{2}", value)
        if not match:
            continue
        event_date, start_time = match.groups()
        href_element = element if element.name == "a" else element.find("a", href=True)
        meeting_url = clean_text(href_element.get("href")) if href_element else ""
        meetings[(event_date, start_time)] = meeting_url or ticket_url

    if not meetings:
        start = clean_text(schema.get("startDate"))
        match = re.match(r"(\d{4}-\d{2}-\d{2})(?:T(\d{2}:\d{2}))?", start)
        if match:
            meetings[(match.group(1), match.group(2))] = ticket_url

    genre = ", ".join(sorted(raw_genres)) or None
    openers = extract_special_guests(soup, headliner)
    events = []
    for (event_date, start_time), meeting_url in meetings.items():
        if event_date < date.today().isoformat():
            continue
        events.append(
            ConcertEvent(
                date=event_date,
                headliner=headliner,
                venue="La Seine Musicale",
                city="Boulogne-Billancourt",
                department="92",
                openers=openers,
                genre=genre,
                ticket_url=meeting_url,
                start_time=start_time,
                image_url=image_url,
                image_source=SOURCE_NAME if image_url else None,
                authoritative_billing=bool(openers),
            )
        )
    return events


def event_key(event):
    return (event.date, event.headliner.casefold(), event.venue.casefold())


def load_events():
    session = requests.Session()
    session.headers.update(HEADERS)
    cards = {}

    for genre_id, genre_name in INCLUDED_GENRES.items():
        for page in range(1, MAX_PAGES + 1):
            print(f"Downloading La Seine Musicale genre {genre_id}, page {page}...")
            response = session.get(
                PROGRAMME_URL,
                params=[("genre[]", genre_id), ("paged", str(page))],
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            page_cards = soup.select("a.card.card--alt[href]")
            if not page_cards:
                break
            for card in page_cards:
                detail_url = urljoin(PROGRAMME_URL, card.get("href"))
                cards.setdefault(detail_url, set()).add(genre_name)
            if len(page_cards) < 16:
                break
        else:
            raise RuntimeError("La Seine Musicale pagination exceeded safety limit")

    events_by_key = {}
    for index, (detail_url, raw_genres) in enumerate(cards.items(), start=1):
        print(f"Reading La Seine Musicale event {index}/{len(cards)}...")
        response = session.get(detail_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        for event in parse_detail(response.text, detail_url, raw_genres):
            events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())
    print(f"Created {len(events)} La Seine Musicale ConcertEvent records")
    return events
