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
MAX_DIAGNOSTICS = 200
_DIAGNOSTICS = []


def _diagnostic_priority(*, title, series_name, venue_data, co_headliners, openers):
    venue_text = clean_text((venue_data or {}).get("name"))
    haystack = f"{title} {series_name or ''} {venue_text}".casefold()
    priority = 0
    if series_name:
        priority += 5
    if re.search(r"\b(?:festival|programme|series)\b", haystack):
        priority += 4
    if re.search(r"\b(?:main room|grande salle|petite salle|club|hall|room\s*\d*|stage|double show|\d(?:er|e|nd|st)\s+set)\b", haystack):
        priority += 4
    if co_headliners or openers:
        priority += 2
    if re.search(r"\s[+&/]\s|\b(?:with|feat\.?|featuring)\b", title, re.I):
        priority += 1
    return priority

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

FESTIVAL_SUFFIX_RE = re.compile(
    r"\s+—\s+(?P<series>(?=[^—]*(?:\b20\d{2}\b|\bparis\b|\bpitchfork\b))"
    r"[^—]+\b(?:festival|programme|series)\b[^—]*)\s*$",
    re.IGNORECASE,
)
NAMED_GUEST_RE = re.compile(
    r"\s*\+\s*(?:very\s+)?special\s+guests?\s*:\s*(?P<name>.+?)\s*$|"
    r"\s*\+\s*guest\s*:\s*(?P<guest>.+?)\s*$",
    re.IGNORECASE,
)
PARIS_PRESENTATION_SUFFIX_RE = re.compile(
    r",\s*en\s+concert\s+à\s+Paris\s*!?\s*$",
    re.IGNORECASE,
)
PASS_PREFIX_RE = re.compile(
    r"^pass\s+(?:1|2)\s+jours?\s+[^:]+:\s*",
    re.IGNORECASE,
)


def normalize_presentation_wrapper(title):
    """Remove only the reviewed DICE presentation/pass wrapper structures."""

    title = clean_text(title)
    title = PARIS_PRESENTATION_SUFFIX_RE.sub("", title).strip()
    return PASS_PREFIX_RE.sub("", title).strip()


def split_festival_suffix(title):
    """Separate a recognized DICE festival/programme suffix from performers."""

    match = FESTIVAL_SUFFIX_RE.search(clean_text(title))
    if not match:
        return clean_text(title), None
    performer_title = clean_text(title[:match.start()])
    series_name = clean_text(match.group("series"))
    if not performer_title or not series_name:
        return clean_text(title), None
    return performer_title, series_name


def parse_named_guest(title):
    """Parse only explicitly labelled named guests as support acts."""

    match = NAMED_GUEST_RE.search(clean_text(title))
    if not match:
        return clean_text(title), None
    guest = clean_text(match.group("name") or match.group("guest"))
    performer = clean_text(title[:match.start()])
    return performer, [guest] if performer and guest else None


EXPLICIT_SUPPORT_RE = re.compile(
    r"^(.+?)\s*\|\s*(?:1(?:er|re|ère|e)\s+partie|première\s+partie|en\s+première\s+partie)\s*:\s*(.+)$",
    re.IGNORECASE,
)


def parse_explicit_support_title(title):
    match = EXPLICIT_SUPPORT_RE.match(clean_text(title))
    if not match:
        return clean_text(title), None
    support = clean_text(match.group(2))
    return clean_text(match.group(1)), [support] if support else None


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
        r"^guests?\s+(?:surprise|suprise)$",
    )

    # Preserve the existing explicit "1ère partie" representation; it is
    # descriptive billing metadata, not an artist placeholder to rewrite.
    if any(re.fullmatch(non_artist_patterns[0], component, flags=re.IGNORECASE) for component in components):
        return title, None

    components = [
        component for component in components
        if not any(
            re.fullmatch(pattern, component, flags=re.IGNORECASE)
            for pattern in non_artist_patterns
        )
    ]

    if len(components) < 2:
        return components[0] if components else title, None

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


def get_diagnostics():
    ranked = sorted(
        enumerate(_DIAGNOSTICS),
        key=lambda item: (-item[1].get("diagnostic_priority", 0), item[0]),
    )
    return [item[1] for item in ranked[:MAX_DIAGNOSTICS]]


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
    dates = data.get("dates") or {}
    start_date = dates.get("event_start_date")
    announced_at = dates.get("announcement_date")
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
    performer_title, series_name = split_festival_suffix(event_name)
    performer_title = normalize_presentation_wrapper(performer_title)
    performer_title, named_guest_openers = parse_named_guest(performer_title)
    performer_title = normalize_presentation_wrapper(performer_title)
    performer_title, explicit_support = parse_explicit_support_title(performer_title)
    headliner, openers = parse_explicit_billing(performer_title)

    if explicit_support:
        openers = explicit_support
    elif named_guest_openers:
        openers = named_guest_openers

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

    diagnostic_priority = _diagnostic_priority(
        title=event_name,
        series_name=series_name,
        venue_data=venue_data,
        co_headliners=co_headliners,
        openers=openers,
    )
    if diagnostic_priority:
        _DIAGNOSTICS.append({
            "source_event_id": event_id,
            "listing_url": EVENTS_URL,
            "detail_url": f"https://dice.fm/event/{event_id}",
            "raw_event_title": event_name,
            "raw_performer_array": data.get("artists") or data.get("performers"),
            "raw_venue": venue,
            "raw_venue_id": venue_data.get("id"),
            "raw_room": venue_data.get("room") or venue_data.get("space") or venue_data.get("stage"),
            "raw_parent_venue": venue_data.get("parent_name") or venue_data.get("parentVenue"),
            "raw_address": venue_data.get("address"),
            "raw_city": city,
            "series_name": series_name,
            "parser_billing_path": "explicit_title_billing" if openers else "neutral_cobill",
            "parsed_headliner": headliner,
            "parsed_co_headliners": co_headliners,
            "parsed_openers": openers,
            "final_date": event_date,
            "final_venue": venue,
            "start_time": start_date.split("T", 1)[1][:5] if "T" in start_date else None,
            "diagnostic_priority": diagnostic_priority,
        })

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
    _DIAGNOSTICS.clear()
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
