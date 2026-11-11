from datetime import datetime, date, timedelta
import json
import time
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
import re
import unicodedata

import requests

from concert_calendar.models import ConcertEvent
from concert_calendar.event_titles import is_non_artist_event_title


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
ESSAIM_MAIN_ROOM_VENUE_ID = "15305"
_DIAGNOSTICS = []
_LAST_LOAD_METADATA = {"path": "primary", "fallback_source": None}



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
    """Reject clearly non-musical DICE browse entries, not vaguely named acts."""
    normalized = unicodedata.normalize("NFKD", title or "")
    normalized = "".join(
        character for character in normalized
        if not unicodedata.combining(character)
    ).casefold()
    normalized = " ".join(normalized.split())

    # Reviewed false positives in DICE's nominal music:gig browse inventory.
    # Avoid broad rules against cabarets, screenings or afterworks: some
    # actually feature live music, and their titles alone are inconclusive.
    non_concert_patterns = (
        r"\bviewing(?:s)? parties\b",
        r"^blind[\s-]?test(?:\s+with\b|$)",
        r"\bspeed[\s-]?dating\b",
        r"\bgenerated nightmares\b.*\bexhibition\b",
        r"^la rentree de cheries-cheris$",
        r"^novemberfest by paname brewing company$",
        # Festival admission products are not individually billed concerts.
        r"^ici demain festival\s*#?\d+\s*-\s*pass\s+",
    )

    return (
        is_non_artist_event_title(title)
        or any(re.search(pattern, normalized) for pattern in non_concert_patterns)
    )


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


def parse_explicit_support_title(title):
    title = clean_text(title)
    match = re.match(
        r"^(.+?)\s*\|\s*(?:1(?:ère|ere|re|er|e)|première)\s+partie\s*:\s*(.+)$",
        title, re.IGNORECASE,
    )
    return (clean_text(match[1]), [clean_text(match[2])]) if match else (title, None)


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

    return title, None


def parse_neutral_cobill(title):
    """A title alone does not establish individual artists or support roles."""
    if re.search(r"\([^)]*[+•][^)]*\)", title):
        return clean_text(title), None
    # Anonymous guest placeholders are not artist identities. This does not
    # split or assign roles to any of the remaining named text.
    title = re.sub(r"\s+\+\s+guests?(?:\s+(?:surprise|suprise))?\s*$", "", clean_text(title), flags=re.I)
    return title, None


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
    raw_venue = clean_text(venue_data.get("name"))
    venue_id = clean_text(venue_data.get("id"))
    city = clean_text((venue_data.get("city") or {}).get("name"))

    if not raw_venue or not city:
        return None

    venue = (
        "Essaim – Main Room"
        if venue_id == ESSAIM_MAIN_ROOM_VENUE_ID
        else raw_venue
    )

    try:
        event_date = datetime.fromisoformat(start_date).date().isoformat()
    except (TypeError, ValueError):
        return None

    event_name = headliner
    performer_title, series_name = split_festival_suffix(event_name)
    performer_title = normalize_presentation_wrapper(performer_title)
    performer_title, named_guest_openers = parse_named_guest(performer_title)
    performer_title = normalize_presentation_wrapper(performer_title)
    headliner, openers = parse_explicit_billing(performer_title)
    headliner, explicit_support = parse_explicit_support_title(headliner)

    if named_guest_openers:
        openers = named_guest_openers
    if explicit_support:
        openers = list(dict.fromkeys([*(openers or []), *explicit_support]))

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
            "raw_venue": raw_venue,
            "raw_venue_id": venue_id,
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
        raw_title=event_name,
        performers=list(dict.fromkeys(
            clean_text(item.get('name')) for item in (data.get('artists') or data.get('performers') or [])
            if isinstance(item, dict) and clean_text(item.get('name'))
        )) or None,
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
        # Multiple sets on the same date at the same venue must survive DICE
        # source deduplication so the later performance-aware reconciler can
        # assess them. A shared artist/venue/day is not a complete event key.
        event.start_time or "",
    )


def _load_api_events():
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

        # A page can consist entirely of duplicates or non-concert records
        # while a later cursor still contains new concerts. Only an exhausted
        # or repeated cursor ends enumeration, not an empty *new* count.
        next_cursor = payload.get("next_page_cursor")

        if not next_cursor:
            break
        if next_cursor in seen_cursors:
            raise requests.RequestException(
                "DICE API pagination cursor repeated before inventory exhaustion"
            )

        seen_cursors.add(next_cursor)
        cursor = next_cursor
    else:
        # A capped catalogue is not a complete primary inventory. Fail into
        # the explicitly incomplete browse fallback rather than publishing a
        # truncated snapshot as a healthy successful API scrape.
        raise requests.RequestException(
            f"DICE API pagination exceeded {MAX_PAGES} pages with more records"
        )

    events = list(events_by_key.values())

    print(f"Created {len(events)} DICE ConcertEvent records")

    return events

def get_load_metadata():
    """Expose limited public-page fallback without claiming full catalogue health."""
    return dict(_LAST_LOAD_METADATA)


def extract_public_browse_events(html, *, allow_empty=False):
    """Read DICE's anonymous, server-rendered Next.js event inventory.

    This response contains only the initial browse batch. Its cursor cannot
    be used as proof that the full catalogue has been enumerated.
    """
    match = re.search(
        r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        html, flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise ValueError("DICE public browse page has no __NEXT_DATA__ payload")
    payload = json.loads(match.group(1))
    page_props = (payload.get("props") or {}).get("pageProps") or {}
    raw = page_props.get("events")
    if not isinstance(raw, list) or (not raw and not allow_empty):
        raise ValueError("DICE public browse page returned no usable event inventory")
    events_by_key = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        event = parse_event(item)
        if event is not None:
            events_by_key.setdefault(event_key(event), event)
    if not events_by_key and raw and not allow_empty:
        raise ValueError("DICE public browse page returned no parseable concerts")
    return list(events_by_key.values()), bool(page_props.get("nextCursor"))


# The public browse page serves a capped first batch. Partitioning by event
# date retrieves more concerts without relying on the blocked unified_search API.
# Keep requests bounded and serial to avoid placing unnecessary load on DICE.
PUBLIC_BROWSE_DAYS = 385
PUBLIC_WINDOW_DAYS = 7
PUBLIC_MAX_REQUESTS = 95
PUBLIC_REQUEST_PAUSE_SECONDS = 0.15
PUBLIC_GIG_PAGE = EVENTS_URL


def _public_browse_windows(today, *, horizon=PUBLIC_BROWSE_DAYS):
    end = today + timedelta(days=horizon - 1)
    start = today
    while start <= end:
        stop = min(end, start + timedelta(days=PUBLIC_WINDOW_DAYS - 1))
        yield start, stop
        start = stop + timedelta(days=1)


def _load_public_browse_events(*, today=None):
    """Recover DICE gig listings using bounded public date partitions.

    Pages can still omit concerts or have other hidden server limits. This
    method must ALWAYS report incomplete inventory to source retention.
    """
    today = today or datetime.now(ZoneInfo("Europe/Paris")).date()
    session = requests.Session()
    session.headers.update({
        "User-Agent": HEADERS["User-Agent"],
        "Accept": "text/html",
    })
    by_key = {}
    visits = 0
    saturated = 0
    unavailable = 0
    additional_pages = False

    def visit(url):
        nonlocal visits
        if visits >= PUBLIC_MAX_REQUESTS:
            return None
        if visits:
            time.sleep(PUBLIC_REQUEST_PAUSE_SECONDS)
        visits += 1
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return extract_public_browse_events(response.text, allow_empty=True)

    def merge(events):
        for event in events:
            if date.fromisoformat(event.date) >= today:
                by_key.setdefault(event_key(event), event)

    # The popular city page contains additional concerts not present in the
    # gig listing. It is curated and does not establish complete coverage.
    city_page = EVENTS_URL.split("/music/gig")[0]
    try:
        result = visit(city_page)
        if result:
            merge(result[0])
            additional_pages |= result[1]
    except (requests.RequestException, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"DICE public city page unavailable: {type(error).__name__}: {error}", flush=True)

    def load_window(start, end):
        nonlocal unavailable, saturated, additional_pages
        if visits >= PUBLIC_MAX_REQUESTS:
            saturated += 1
            return
        url = PUBLIC_GIG_PAGE + "?" + urlencode({
            "from": start.isoformat(), "until": end.isoformat(),
        })
        try:
            result = visit(url)
            if result is None:
                saturated += 1
                return
            events, has_more = result
        except (requests.RequestException, ValueError, KeyError, json.JSONDecodeError) as error:
            unavailable += 1
            print(
                f"DICE public partition unavailable {start}..{end}: "
                f"{type(error).__name__}: {error}", flush=True,
            )
            return
        # Only admit records dated within the requested partition: this
        # detects pages that ignore query parameters rather than silently
        # counting the first browse batch repeatedly.
        relevant = [
            event for event in events
            if start <= date.fromisoformat(event.date) <= end
        ]
        if len(relevant) != len(events):
            print(
                f"DICE partition {start}..{end}: "
                f"{len(events) - len(relevant)} events outside requested dates",
                flush=True,
            )
        merge(relevant)
        if has_more and start < end:
            middle = start + timedelta(days=(end - start).days // 2)
            load_window(start, middle)
            load_window(middle + timedelta(days=1), end)
        elif has_more:
            # Even one day may contain more listings than a single browse
            # page returns. A saturated day must not be considered complete.
            saturated += 1
            additional_pages = True

    for start, end in _public_browse_windows(today):
        load_window(start, end)

    if not by_key:
        raise ValueError("DICE public browse discovery returned no concerts")
    print(
        f"DICE public browse discovery | records={len(by_key)} | requests={visits} "
        f"| unavailable_partitions={unavailable} | saturated_partitions={saturated}"
        + " | partial_public_inventory=true",
        flush=True,
    )
    return list(by_key.values()), bool(additional_pages or saturated or unavailable)


def load_events():
    """Prefer the complete API; on access failure use a clearly partial SSR batch."""
    _DIAGNOSTICS.clear()
    _LAST_LOAD_METADATA.clear()
    _LAST_LOAD_METADATA.update({"path": "primary", "fallback_source": None})
    try:
        return _load_api_events()
    except requests.RequestException as primary_error:
        try:
            events, has_more = _load_public_browse_events()
        except (requests.RequestException, ValueError, KeyError, TypeError, json.JSONDecodeError) as fallback_error:
            raise RuntimeError(
                f"DICE API unavailable ({type(primary_error).__name__}: {primary_error}); "
                f"public browse fallback unavailable ({type(fallback_error).__name__}: {fallback_error})"
            ) from fallback_error
        _LAST_LOAD_METADATA.update({
            "path": "fallback",
            "fallback_source": "DICE public Paris browse page (initial server-rendered batch)",
            "incomplete": True,
        })
        print(
            f"DICE API unavailable: {type(primary_error).__name__}: {primary_error}; "
            f"using {len(events)} public browse records as an incomplete fallback"
            + (" (additional pages exist)" if has_more else ""),
            flush=True,
        )
        return events
