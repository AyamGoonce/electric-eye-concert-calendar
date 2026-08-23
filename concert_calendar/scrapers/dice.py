from datetime import datetime
import re
import unicodedata

import requests

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "DICE"
SOURCE_PRIORITY = 100

EVENTS_URL = (
    "https://dice.fm/browse/"
    "paris-5b23e8a0e63cc224a4c36a2d/music/gig"
)
API_URL = "https://api.dice.fm/unified_search"
REQUEST_TIMEOUT = 30
PAGE_SIZE = 24
MAX_PAGES = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US",
    "Content-Type": "application/json",
    "Referer": EVENTS_URL,
    "X-Api-Timestamp": "2025-04-16",
    "X-Client-Timezone": "Europe/Paris",
}

SEARCH_BODY = {
    "count": PAGE_SIZE,
    "lat": 48.864716,
    "lng": 2.349014,
    "tag": "music:gig",
}


def clean_text(value):
    if not value:
        return ""

    return " ".join(str(value).split())


def is_non_concert_listing(title):
    normalized = unicodedata.normalize("NFKD", title)
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    ).casefold()

    return bool(re.search(r"\bviewing(?:s)? parties\b", normalized))


SERIES_PREFIXES = {
    "le beau dimanche",
}


def parse_explicit_billing(title):
    """Return reviewed title-embedded billing without guessing arbitrary titles."""

    title = clean_text(title)
    prefix, separator, remainder = title.partition(":")
    has_reviewed_structure = False

    if separator and prefix.strip().casefold() in SERIES_PREFIXES:
        title = remainder.strip()
        has_reviewed_structure = True

    without_series_suffix, suffix_count = re.subn(
        r"\s*\[(?:opening\s+des\s+)?afters(?:\s+jazz\s+à\s+la\s+villette)?\s*#\d+\]\s*$",
        "",
        title,
        flags=re.IGNORECASE,
    )

    if suffix_count:
        title = without_series_suffix.strip()
        has_reviewed_structure = True

    if not has_reviewed_structure:
        return title, None

    components = [
        clean_text(value)
        for value in re.split(r"\s+(?:\+|•)\s+", title)
    ]

    if len(components) < 2:
        return title, None

    return components[0], components[1:]


def parse_neutral_cobill(title):
    """Split explicit equal-billing artist lists without inventing support hierarchy."""

    title = clean_text(title)
    components = [
        clean_text(value)
        for value in re.split(r"\s+(?:\+|•)\s+", title)
    ]

    if len(components) < 2:
        return title, None

    non_artist_patterns = (
        r"^1(?:er|re|ère|e)\s+partie$",
        r"^(?:guest|guests)$",
        r"^(?:support|supports)$",
        r"^(?:special guest|special guests)$",
        r"^(?:opening act|opening acts)$",
        r"^(?:tba|to be announced)$",
    )

    for component in components:
        if any(
            re.fullmatch(pattern, component, flags=re.IGNORECASE)
            for pattern in non_artist_patterns
        ):
            return title, None

    return components[0], components[1:]


def parse_mardi_jazz_lineup(description):
    """Extract the reviewed Mardi Jazz! musician bill from its DICE description."""

    performers = []

    for raw_line in (description or "").splitlines():
        line = clean_text(raw_line)

        if "•" not in line:
            continue

        name, _, role = line.partition("•")
        name = clean_text(name)
        role = clean_text(role)

        if not name or not role:
            continue

        role_normalized = role.casefold()

        if not any(
            token in role_normalized
            for token in (
                "saxophone",
                "guitare",
                "trompette",
                "piano",
                "contrebasse",
                "batterie",
            )
        ):
            continue

        performers.append(name)

    return performers


def extract_events(payload):
    events = []

    for section in payload.get("sections") or []:
        for item in section.get("items") or []:
            event = item.get("event")

            if event:
                events.append(event)

        events.extend(section.get("events") or [])

    return events


def fetch_dice_detail_description(event_id):
    url = f"https://dice.fm/event/{event_id}"

    response = requests.get(
        url,
        headers={"User-Agent": HEADERS["User-Agent"]},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    match = re.search(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        response.text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return ""

    try:
        import json
        payload = json.loads(match.group(1))
    except (json.JSONDecodeError, TypeError):
        return ""

    if (
        isinstance(payload, dict)
        and clean_text(payload.get("name")).casefold() == "mardi jazz!"
    ):
        return payload.get("description") or ""

    return ""


def parse_event(data):
    event_id = clean_text(data.get("id"))
    headliner = clean_text(data.get("name"))
    start_date = (data.get("dates") or {}).get("event_start_date")
    venues = data.get("venues") or []

    if (
        not event_id
        or not headliner
        or is_non_concert_listing(headliner)
        or not start_date
        or not venues
    ):
        return None

    venue_data = venues[0]
    venue = clean_text(venue_data.get("name"))
    city = clean_text((venue_data.get("city") or {}).get("name"))

    if not venue or not city:
        return None

    try:
        event_date = datetime.fromisoformat(start_date).date().isoformat()
    except (TypeError, ValueError):
        return None

    event_name = headliner
    headliner, openers = parse_explicit_billing(headliner)

    series_name = None

    if event_name.casefold() == "mardi jazz!":
        try:
            description = fetch_dice_detail_description(event_id)
            lineup = parse_mardi_jazz_lineup(description)
        except requests.RequestException:
            lineup = []

        if lineup:
            series_name = event_name
            headliner = lineup[0]
            openers = lineup[1:] or None

    co_headliners = None
    if not openers:
        headliner, co_headliners = parse_neutral_cobill(headliner)

    images = data.get("images") or {}
    image_url = clean_text(images.get("square")) or None

    start_time = None
    if "T" in start_date:
        start_time = start_date.split("T", 1)[1][:5]

    raw_status = clean_text(data.get("status")).casefold()
    ticket_status = {
        "on-sale": "tickets",
        "sold-out": "sold_out",
        "cancelled": "cancelled",
        "postponed": "postponed",
    }.get(raw_status)

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="",
        openers=openers,
        co_headliners=co_headliners,
        promoters=None,
        genre=None,
        facebook_event_url=None,
        ticket_url=f"https://dice.fm/event/{event_id}",
        sold_out=(raw_status == "sold-out"),
        ticket_status=ticket_status,
        start_time=start_time,
        image_url=image_url,
        image_source="DICE" if image_url else None,
        event_title=event_name if (openers or co_headliners or series_name) else None,
        series_name=series_name,
    )


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
        event.city.casefold(),
    )


def load_events():
    session = requests.Session()
    session.headers.update(HEADERS)
    events_by_key = {}
    cursor = None
    seen_cursors = set()

    for page_number in range(1, MAX_PAGES + 1):
        body = dict(SEARCH_BODY)

        if cursor:
            body["cursor"] = cursor

        print(f"Downloading DICE concert page {page_number}...")

        response = session.post(
            API_URL,
            json=body,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        source_events = extract_events(payload)
        new_events = 0

        for source_event in source_events:
            event = parse_event(source_event)

            if event is None:
                continue

            key = event_key(event)

            if key not in events_by_key:
                events_by_key[key] = event
                new_events += 1

        next_cursor = payload.get("next_page_cursor")

        if (
            not source_events
            or not next_cursor
            or next_cursor in seen_cursors
            or new_events == 0
        ):
            break

        seen_cursors.add(next_cursor)
        cursor = next_cursor

    events = list(events_by_key.values())

    print(f"Created {len(events)} DICE ConcertEvent records")

    return events
