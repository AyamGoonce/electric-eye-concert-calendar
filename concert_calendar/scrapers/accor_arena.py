import re
from html import unescape
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Accor Arena"

API_URL = "https://www.accorarena.com/api-cms/custom/event/v2/list"
BASE_URL = "https://www.accorarena.com/fr/"
REQUEST_TIMEOUT = 30
PAGE_LIMIT = 100
MAX_PAGES = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
    "Accept": "application/json",
}


def clean_text(value):
    return re.sub(r"\s+", " ", unescape(value or "")).strip()


def french_translation(item):
    return next(
        (
            translation
            for translation in item.get("translations", [])
            if translation.get("language") == "fr"
        ),
        {},
    )


def is_music_event(item, translation):
    """Use explicit programme metadata, without treating sports as concerts."""

    return bool(
        clean_text(translation.get("category")).casefold() == "concert"
        or clean_text(item.get("spotify"))
    )


def split_artist_names(value):
    names = [
        clean_text(name).strip(" .;:")
        for name in re.split(r"\s+(?:\+|&|et)\s+|\s*[•;,]\s*", value)
    ]
    return [name for name in names if name]


def extract_explicit_support(description, headliner):
    """Extract only artists inside an explicit support-billing sentence."""

    soup = BeautifulSoup(description or "", "html.parser")
    headliner_identity = clean_text(headliner).casefold()
    support = []

    for paragraph in soup.select("p"):
        text = clean_text(paragraph.get_text(" ", strip=True))
        normalized = text.casefold()
        if not re.search(
            r"\b(?:premi(?:è|e)res? parties?|en premi(?:è|e)re partie|"
            r"support|opening act|special guests?|invit(?:é|e)s? sp(?:é|e)ciaux)\b",
            normalized,
        ) and not re.search(
            r"\baccompagn(?:é|ée|és|ées)s?\s+de\b", normalized
        ):
            continue

        candidates = [clean_text(node.get_text(" ", strip=True)) for node in paragraph.select("strong, b")]
        candidates = [
            value for value in candidates
            if value
            and value.casefold() not in {headliner_identity, "accor arena"}
            and not re.fullmatch(r"\d+\s+concerts?", value, flags=re.IGNORECASE)
        ]

        if not candidates:
            patterns = (
                r"premi(?:è|e)res? parties?\s*:\s*(.+)$",
                r"(?:avec|with)\s+(.+?)\s+en premi(?:è|e)re partie\b",
                r"^(.+?)\s+en assurera la premi(?:è|e)re partie\b",
                r"accompagn(?:é|e)s? de\s+(.+?)\s+en invit(?:é|e)s? sp(?:é|e)ciaux\b",
                r"accompagn(?:é|ée|és|ées)s?\s+de\s+(.+?)(?:\s*[!.]|$)",
                r"(?:support|opening act|special guests?)\s*:\s*(.+)$",
            )
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    candidates = split_artist_names(match.group(1))
                    break

        for candidate in candidates:
            candidate = clean_text(candidate)
            if (
                candidate
                and len(candidate) <= 100
                and candidate.casefold() != headliner_identity
                and candidate.casefold() not in {name.casefold() for name in support}
            ):
                support.append(candidate)

    return support or None


def parse_item(item):
    translation = french_translation(item)
    if not translation or not is_music_event(item, translation):
        return []

    headliner = clean_text(translation.get("title") or item.get("artist_reference"))
    room = item.get("room") or {}
    venue = clean_text(room.get("full_name"))
    sessions = item.get("sessions") or []
    ticket_url = clean_text(translation.get("url_event")) or None
    genre = clean_text(translation.get("sub_category")) or None
    openers = extract_explicit_support(translation.get("description"), headliner)
    image = item.get("presentation_event") or item.get("list_image") or {}
    image_filename = clean_text(image.get("filename_disk"))
    image_url = (
        urljoin(BASE_URL, f"/uploads/aha/originals/{image_filename}")
        if image_filename
        else None
    )

    if not headliner or not venue:
        return []

    events = []
    for session in sessions:
        session_date = clean_text(session.get("date"))
        if not re.match(r"^\d{4}-\d{2}-\d{2}", session_date):
            continue
        start_time = (
            session_date[11:16]
            if re.match(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}", session_date)
            else None
        )
        events.append(ConcertEvent(
            date=session_date[:10],
            headliner=headliner,
            venue=venue,
            city="Paris",
            department="75",
            openers=list(openers) if openers else None,
            promoters=None,
            genre=genre,
            facebook_event_url=None,
            ticket_url=ticket_url,
            authoritative_billing=bool(openers),
            start_time=start_time,
            image_url=image_url,
            image_source=SOURCE_NAME if image_url else None,
        ))

    return events


def event_key(event):
    return event.date, event.headliner.casefold(), event.venue.casefold()


def load_events():
    session = requests.Session()
    events_by_key = {}

    for page in range(1, MAX_PAGES + 1):
        print(f"Downloading Accor Arena page {page}...")
        response = session.get(
            API_URL,
            params={
                "page": page,
                "limit": PAGE_LIMIT,
                "language": "fr",
                "room": "accor-arena",
            },
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        items = response.json().get("data") or []

        for item in items:
            for event in parse_item(item):
                events_by_key.setdefault(event_key(event), event)

        if len(items) < PAGE_LIMIT:
            break
    else:
        raise RuntimeError("Accor Arena pagination exceeded its safety bound")

    events = list(events_by_key.values())
    print(f"Created {len(events)} Accor Arena ConcertEvent records")
    return events
