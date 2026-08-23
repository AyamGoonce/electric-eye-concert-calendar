import json
import re
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "La Cigale"

PROGRAMME_URL = "https://lacigale.fr/programmation/"
REQUEST_TIMEOUT = 30
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()



def parse_detail_metadata(session, url):
    """Read structured event metadata from La Cigale JSON-LD."""

    response = session.get(
        url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    def walk(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue

        for item in walk(payload):
            event_type = item.get("@type")
            types = event_type if isinstance(event_type, list) else [event_type]

            if "Event" not in types and "MusicEvent" not in types:
                continue

            performers = item.get("performer") or []
            if isinstance(performers, dict):
                performers = [performers]

            performer_names = [
                clean_text(performer.get("name"))
                for performer in performers
                if isinstance(performer, dict)
                and clean_text(performer.get("name"))
            ]

            image = item.get("image")
            if isinstance(image, list):
                image = image[0] if image else None
            if isinstance(image, dict):
                image = image.get("url")

            return {
                "event_title": clean_text(item.get("name")),
                "performers": performer_names,
                "start_date": clean_text(item.get("startDate")),
                "image_url": clean_text(image),
            }

    return {}

def parse_card(card, session):
    event_type = clean_text(card.get("data-type")).casefold()
    genre = clean_text(card.get("data-genre"))
    card_text = clean_text(card.get_text(" ", strip=True)).casefold()
    title_element = card.select_one(".artiste-event__title")
    link = card.select_one("a.artiste-event__link[href]")
    headliner = clean_text(title_element.get_text(" ", strip=True)) if title_element else ""

    if event_type not in {"concert", "festival"}:
        return []

    if re.search(r"humour|one man show|theatre|conf[ée]rence", genre, re.IGNORECASE):
        return []

    if "annul" in card_text or not headliner or not link:
        return []

    event_dates = []

    for value in clean_text(card.get("data-date")).split():
        try:
            parsed = datetime.strptime(value, "%Y%m%d").date()
        except ValueError:
            continue

        if parsed >= date.today():
            event_dates.append(parsed)

    if event_type == "festival" and len(event_dates) > 1:
        return []

    detail_url = clean_text(link.get("href")) or PROGRAMME_URL

    detail = {}
    try:
        detail = parse_detail_metadata(session, detail_url)
    except requests.RequestException as exc:
        print(f"La Cigale detail fetch failed for {detail_url}: {exc}")

    performers = detail.get("performers") or []
    structured_headliner = performers[0] if performers else headliner
    structured_openers = performers[1:] or None

    start_time = None
    start_date = detail.get("start_date") or ""
    if "T" in start_date:
        start_time = start_date.split("T", 1)[1][:5]

    return [
        ConcertEvent(
            date=event_date.isoformat(),
            headliner=structured_headliner,
            venue="La Cigale",
            city="Paris",
            department="75",
            openers=structured_openers,
            promoters=None,
            genre=genre or None,
            facebook_event_url=None,
            ticket_url=detail_url,
            event_title=(
                detail.get("event_title")
                if detail.get("event_title")
                and detail.get("event_title").casefold()
                != structured_headliner.casefold()
                else None
            ),
            image_url=detail.get("image_url") or None,
            image_source="La Cigale" if detail.get("image_url") else None,
            start_time=start_time,
        )
        for event_date in event_dates
    ]


def event_key(event):
    return event.date, event.headliner.casefold(), event.venue.casefold()


def load_events():
    session = requests.Session()
    print("Downloading La Cigale programme...")
    response = session.get(
        PROGRAMME_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events_by_key = {}

    for card in soup.select(".artiste-event__item"):
        for event in parse_card(card, session):
            events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())
    print(f"Created {len(events)} La Cigale ConcertEvent records")
    return events
