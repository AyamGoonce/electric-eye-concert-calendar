import re
from datetime import date, datetime, timedelta

import requests

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "L’Olympia Bruno Coquatrix"

EVENTS_API_URL = (
    "https://www.olympiahall.com/wp-json/"
    "df-elastic-search/v1/search-evenements/"
)
REQUEST_TIMEOUT = 30
PAGE_SIZE = 200

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

MUSIC_GENRES = {
    "Blues",
    "Classique",
    "Dancehall",
    "Electro",
    "Folk",
    "Funk",
    "Indie / Folk",
    "Jazz",
    "Metal / Hard Rock",
    "Pop",
    "Rap / Hip-Hop français",
    "Rap / Hip-Hop international",
    "Reggae",
    "RnB",
    "Rock",
    "Soul",
    "Spectacle Musical",
    "Variété française",
    "Variété Internationale",
    "Zouk",
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def parse_date(value):
    try:
        return datetime.strptime(
            clean_text(value),
            "%Y-%m-%d",
        ).date()
    except ValueError:
        return None


def split_support(value):
    artists = [
        clean_text(part)
        for part in re.split(r"\s+\+\s+", clean_text(value))
    ]
    return [artist for artist in artists if artist] or None


def item_genres(item):
    return {
        clean_text(term.get("name"))
        for term in (item.get("terms") or {}).get("genre", [])
        if clean_text(term.get("name"))
    }


def performance_dates(meta):
    begin_date = parse_date(meta.get("begin_date_ymd"))
    end_date = parse_date(meta.get("end_date_ymd"))

    if begin_date is None or end_date is None:
        return []

    if begin_date == end_date:
        return [begin_date]

    excluded = {
        parsed
        for value in clean_text(meta.get("exclude_dates")).split()
        if (parsed := parse_date(value)) is not None
    }
    dates = []
    current = begin_date

    while current <= end_date and len(dates) <= 31:
        if current not in excluded:
            dates.append(current)
        current += timedelta(days=1)

    show_statuses = meta.get("show_statuses") or []

    if len(show_statuses) != len(dates):
        return []

    return dates


def parse_item(item):
    meta = item.get("meta") or {}
    genres = item_genres(item)
    status = clean_text(meta.get("infos_text_status")).casefold()
    headliner = clean_text(item.get("post_title")).strip(" -")

    if not genres.intersection(MUSIC_GENRES):
        return []

    if "annul" in status or not headliner:
        return []

    dates = performance_dates(meta)

    if not dates:
        return []

    openers = split_support(meta.get("artistes_premiere_partie"))
    genre = ", ".join(sorted(genres.intersection(MUSIC_GENRES))) or None
    ticket_url = clean_text(item.get("permalink")) or None

    return [
        ConcertEvent(
            date=event_date.isoformat(),
            headliner=headliner,
            venue="L’Olympia Bruno Coquatrix",
            city="Paris",
            department="75",
            openers=openers,
            promoters=None,
            genre=genre,
            facebook_event_url=None,
            ticket_url=ticket_url,
        )
        for event_date in dates
    ]


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
    )


def load_events():
    session = requests.Session()
    events_by_key = {}

    for page_number in range(1, 21):
        print(f"Downloading L’Olympia page {page_number}...")

        response = session.get(
            EVENTS_API_URL,
            params={
                "lang": "fr",
                "filter_periods[0][begin_date]": date.today().isoformat(),
                "page": page_number,
                "posts_per_page": PAGE_SIZE,
                "keyword": "",
            },
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items", [])

        if not items:
            break

        new_events = 0

        for item in items:
            for event in parse_item(item):
                key = event_key(event)

                if key not in events_by_key:
                    events_by_key[key] = event
                    new_events += 1

        if new_events == 0:
            break

        if page_number >= payload.get("nb_pages", page_number):
            break

    events = list(events_by_key.values())

    print(f"Created {len(events)} L’Olympia ConcertEvent records")

    return events
