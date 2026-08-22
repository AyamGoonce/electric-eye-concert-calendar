import html
import json
import re

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "VeryShow"

EVENTS_URL = "https://verygroup.fr/concerts-et-billetterie/"
LIVEWIRE_UPDATE_URL = "https://verygroup.fr/livewire/update"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def unwrap_livewire(value):
    """
    Convert Livewire's synthesized values into normal Python values.
    """

    if isinstance(value, list):
        if (
            len(value) == 2
            and isinstance(value[1], dict)
            and value[1].get("s") in {"arr", "obj"}
        ):
            return unwrap_livewire(value[0])

        return [
            unwrap_livewire(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: unwrap_livewire(item)
            for key, item in value.items()
        }

    return value


def clean_text(value):
    """
    Decode HTML entities and normalize whitespace.
    """

    if value is None:
        return ""

    value = html.unescape(str(value))
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def parse_date(value):
    """
    Convert DD/MM/YYYY into YYYY-MM-DD.
    """

    value = clean_text(value)

    match = re.fullmatch(
        r"(\d{1,2})/(\d{1,2})/(\d{4})",
        value,
    )

    if not match:
        return ""

    day, month, year = match.groups()

    return (
        f"{int(year):04d}-"
        f"{int(month):02d}-"
        f"{int(day):02d}"
    )


def parse_city(value):
    """
    Remove VeryShow's trailing department/country code.

    Examples:
        PARIS (75) -> PARIS
        MENNECY (91) -> MENNECY
        ANVERS (BE) -> ANVERS
    """

    value = clean_text(value)

    value = re.sub(
        r"\s*\([^)]*\)\s*$",
        "",
        value,
    )

    return value.strip()


def get_headliner(post):
    """
    Prefer VeryShow's explicit artist-name field.
    """

    artist_titles = post.get("artists_titles") or []

    if isinstance(artist_titles, list):
        for artist in artist_titles:
            artist = clean_text(artist)

            if artist:
                return artist

    title = clean_text(post.get("title"))

    if " – " in title:
        return title.split(" – ", 1)[0].strip()

    if " - " in title:
        return title.split(" - ", 1)[0].strip()

    return title


def get_openers(post):
    """
    Extract VeryShow's explicit first-part artists while rejecting
    obviously malformed URL fragments.
    """

    first_parts = post.get("first_part_artists")

    if not first_parts:
        return None

    if not isinstance(first_parts, list):
        return None

    openers = []

    for item in first_parts:
        if not isinstance(item, dict):
            continue

        name = clean_text(item.get("name"))

        if not name:
            continue

        normalized = name.casefold()

        if (
            normalized in {"http", "https", "http:", "https:"}
            or normalized.startswith("www.")
            or "." in name
            or "/" in name
            or "_" in name
        ):
            continue

        if name not in openers:
            openers.append(name)

    return openers[:5] or None


def post_to_event(post):
    """
    Convert one VeryShow concert record into ConcertEvent.
    """

    headliner = get_headliner(post)
    event_date = parse_date(post.get("date"))
    city = parse_city(post.get("city"))
    venue = clean_text(post.get("concert_hall"))
    ticket_url = clean_text(post.get("link")) or None

    if ticket_url and not re.match(
        r"^https?://",
        ticket_url,
        flags=re.IGNORECASE,
    ):
        ticket_url = None

    if not headliner:
        return None

    if not event_date:
        return None

    if not city:
        return None

    if not venue:
        return None

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue,
        city=city,
        department="",
        openers=get_openers(post),
        promoters=["VeryShow"],
        genre=None,
        facebook_event_url=None,
        ticket_url=ticket_url,
    )


def find_filter_snapshot(soup):
    """
    Return the raw Livewire snapshot for filter-concerts.
    """

    for element in soup.find_all(attrs={"wire:snapshot": True}):
        raw_snapshot = element.get("wire:snapshot")

        if not raw_snapshot:
            continue

        try:
            snapshot = json.loads(raw_snapshot)
        except json.JSONDecodeError:
            continue

        memo = snapshot.get("memo") or {}

        if memo.get("name") == "filter-concerts":
            return raw_snapshot

    return None


def get_initial_state(session):
    """
    Download the VeryShow page and return CSRF token + snapshot.
    """

    response = session.get(
        EVENTS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    csrf_element = soup.find(
        "meta",
        attrs={"name": "csrf-token"},
    )

    if not csrf_element:
        raise RuntimeError(
            "Could not find VeryShow CSRF token"
        )

    csrf = csrf_element.get("content")

    snapshot_raw = find_filter_snapshot(soup)

    if not snapshot_raw:
        raise RuntimeError(
            "Could not find VeryShow concert snapshot"
        )

    snapshot = json.loads(snapshot_raw)

    return csrf, snapshot_raw, snapshot


def go_to_next_page(
    session,
    csrf,
    snapshot_raw,
):
    """
    Call VeryShow's Livewire goToPage() method once.
    """

    payload = {
        "_token": csrf,
        "components": [
            {
                "snapshot": snapshot_raw,
                "updates": {},
                "calls": [
                    {
                        "path": "",
                        "method": "goToPage",
                        "params": [],
                    }
                ],
            }
        ],
    }

    response = session.post(
        LIVEWIRE_UPDATE_URL,
        json=payload,
        headers={
            **HEADERS,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Livewire": "true",
            "X-CSRF-TOKEN": csrf,
            "Referer": EVENTS_URL,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    data = response.json()

    components = data.get("components") or []

    if not components:
        raise RuntimeError(
            "VeryShow Livewire response contained no components"
        )

    component = components[0]

    new_snapshot_raw = component.get("snapshot")

    if not new_snapshot_raw:
        raise RuntimeError(
            "VeryShow Livewire response contained no snapshot"
        )

    new_snapshot = json.loads(new_snapshot_raw)

    return new_snapshot_raw, new_snapshot


def extract_posts(snapshot):
    """
    Extract and unwrap all concert records from a snapshot.
    """

    data = snapshot.get("data") or {}
    posts = unwrap_livewire(data.get("posts") or [])

    if not isinstance(posts, list):
        return []

    return [
        post
        for post in posts
        if isinstance(post, dict)
    ]


def load_events():
    session = requests.Session()

    csrf, snapshot_raw, snapshot = get_initial_state(
        session
    )

    data = snapshot.get("data") or {}

    try:
        total_pages = int(data.get("totalPages") or 1)
    except (TypeError, ValueError):
        total_pages = 1

    current_page = int(
        data.get("currentPage") or 1
    )

    print(
        f"Downloading VeryShow page "
        f"{current_page}/{total_pages}..."
    )

    while current_page < total_pages:
        snapshot_raw, snapshot = go_to_next_page(
            session,
            csrf,
            snapshot_raw,
        )

        data = snapshot.get("data") or {}

        try:
            new_page = int(
                data.get("currentPage") or current_page
            )
        except (TypeError, ValueError):
            new_page = current_page

        if new_page <= current_page:
            raise RuntimeError(
                "VeryShow pagination did not advance"
            )

        current_page = new_page

        print(
            f"Downloading VeryShow page "
            f"{current_page}/{total_pages}..."
        )

    posts = extract_posts(snapshot)

    events = []
    seen_ids = set()

    for post in posts:
        post_id = post.get("id")

        if post_id is not None:
            if post_id in seen_ids:
                continue

            seen_ids.add(post_id)

        event = post_to_event(post)

        if event is not None:
            events.append(event)

    print(
        f"Created {len(events)} "
        "VeryShow ConcertEvent records"
    )

    return events
