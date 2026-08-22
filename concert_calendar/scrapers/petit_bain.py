import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Petit Bain"

EVENTS_URL = "https://petitbain.org/agenda/"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

FRENCH_MONTHS = {
    "janvier": 1,
    "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12,
}

GENERIC_SUPPORT_NAMES = {
    "guest",
    "guests",
    "support",
    "supports",
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def normalize_for_matching(value):
    translation = str.maketrans(
        "àâäçéèêëîïôöùûüÿ",
        "aaaceeee iioouuuy".replace(" ", ""),
    )
    return clean_text(value).casefold().translate(translation)


def parse_card_date(value, today=None):
    today = today or date.today()
    normalized = normalize_for_matching(value)
    match = re.search(
        r"\b(\d{1,2})\s+([a-z]+)(?:\s+(\d{4}))?\b",
        normalized,
    )

    if not match:
        return ""

    day_text, month_name, year_text = match.groups()
    month = FRENCH_MONTHS.get(month_name)

    if not month:
        return ""

    year = int(year_text) if year_text else today.year

    if not year_text and month < today.month:
        year += 1

    try:
        return date(year, month, int(day_text)).isoformat()
    except ValueError:
        return ""


def parse_card(card, today=None):
    class_names = set(card.get("class", []))

    if "categorie-concerts" not in class_names:
        return None

    if "billetterie-annule" in class_names:
        return None

    event_link = card.select_one("a[href*='/evenement/']")
    date_element = card.select_one("#ladatevtmin")
    artist_elements = card.select(".titevtprog .titartprog")

    artists = [
        clean_text(element.get_text(" ", strip=True))
        for element in artist_elements
    ]
    artists = [
        artist
        for artist in artists
        if artist
        and artist.casefold() not in GENERIC_SUPPORT_NAMES
    ]

    if not artists:
        title_element = card.select_one("#nomsoiree")
        title = (
            clean_text(title_element.get_text(" ", strip=True))
            if title_element
            else ""
        )
        artists = [title] if title else []

    event_date = parse_card_date(
        date_element.get_text(" ", strip=True)
        if date_element
        else "",
        today=today,
    )

    if not event_date or not artists:
        return None

    return ConcertEvent(
        date=event_date,
        headliner=artists[0],
        venue="Petit Bain",
        city="Paris",
        department="75",
        openers=artists[1:] or None,
        promoters=None,
        genre=None,
        facebook_event_url=None,
        ticket_url=(
            clean_text(event_link.get("href"))
            if event_link
            else None
        ),
    )


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
    )


def load_events():
    session = requests.Session()

    print("Downloading Petit Bain agenda...")

    response = session.get(
        EVENTS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    events_by_key = {}

    for card in soup.select(".unevt"):
        event = parse_card(card)

        if event is None:
            continue

        events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Petit Bain ConcertEvent records"
    )

    return events
