import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import official_image_url, discard_repeated_generic_images
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Corida"

EVENTS_URL = "https://corida.fr/concerts"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
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
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def parse_date(value):
    """
    Convert a French date such as '31 octobre 2026'
    into YYYY-MM-DD.
    """

    value = clean_text(value).casefold()
    parts = value.split()

    if len(parts) != 3:
        return ""

    day, month, year = parts

    month_number = MONTHS.get(month)

    if month_number is None:
        return ""

    try:
        day_number = int(day)
        year_number = int(year)
    except ValueError:
        return ""

    return (
        f"{year_number:04d}-"
        f"{month_number:02d}-"
        f"{day_number:02d}"
    )


def split_venue_city(value):
    """
    Corida stores venue and city together, e.g.
    'Salle Pleyel, Paris'.
    """

    value = clean_text(value)

    if "," not in value:
        return value, ""

    venue, city = value.rsplit(",", 1)

    return venue.strip(), city.strip()


def clean_ticket_url(url):
    if not url:
        return None

    parts = urlsplit(url)

    query = []

    for key, value in parse_qsl(
        parts.query,
        keep_blank_values=True,
    ):
        lower_key = key.casefold()

        if (
            lower_key == "_gl"
            or lower_key == "_fplc"
            or lower_key.startswith("_ga")
            or lower_key.startswith("_gcl")
        ):
            continue

        query.append((key, value))

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query, doseq=True),
            parts.fragment,
        )
    )


def find_ticket_url(show):
    link = show.select_one(
        ".extra-info a[href]"
    )

    if not link:
        return None

    href = clean_text(link.get("href"))

    return clean_ticket_url(href)


def parse_show(show):
    artist_element = show.select_one("h2")
    venue_element = show.select_one(".venue")
    date_elements = show.select(".date")

    headliner = (
        clean_text(
            artist_element.get_text(" ", strip=True)
        )
        if artist_element
        else ""
    )

    venue_text = (
        clean_text(
            venue_element.get_text(" ", strip=True)
        )
        if venue_element
        else ""
    )

    venue, city = split_venue_city(
        venue_text
    )

    if not headliner:
        return []

    if not venue:
        return []

    if not city:
        return []

    ticket_url = find_ticket_url(show)
    image = show.select_one(":scope > .show-image img[src]")
    image_url = official_image_url(clean_text(image.get("src"))) if image else None

    events = []

    for date_element in date_elements:
        event_date = parse_date(
            date_element.get_text(" ", strip=True)
        )

        if not event_date:
            continue

        events.append(
            ConcertEvent(
                date=event_date,
                headliner=headliner,
                venue=venue,
                city=city,
                department="",
                openers=None,
                promoters=["Corida"],
                genre=None,
                facebook_event_url=None,
                ticket_url=ticket_url,
                image_url=image_url,
                image_source=SOURCE_NAME if image_url else None,
            )
        )

    return events


def load_events():
    print(f"Downloading {EVENTS_URL}...")

    response = requests.get(
        EVENTS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    shows = soup.select(
        "#main-concerts-wrapper .show"
    )

    events = []

    for show in shows:
        events.extend(
            parse_show(show)
        )

    print(
        f"Created {len(events)} "
        "Corida ConcertEvent records"
    )

    return discard_repeated_generic_images(events)
