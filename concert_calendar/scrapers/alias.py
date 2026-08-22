import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Alias Production"

EVENTS_URL = "https://alias-production.fr/billetterie/"
AJAX_URL = "https://alias-production.fr/wp-admin/admin-ajax.php"
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


def parse_month(value):
    """
    Convert Alias month labels such as 'août 2026' into (2026, 8).
    """

    parts = clean_text(value).casefold().split()

    if len(parts) != 2:
        return None

    month_name, year = parts
    month = MONTHS.get(month_name)

    if month is None:
        return None

    try:
        return int(year), month
    except ValueError:
        return None


def parse_date(card):
    month_data = parse_month(card.get("data-month"))
    day_element = card.select_one(".date_numb.desktop")

    if month_data is None or day_element is None:
        return ""

    day_match = re.search(
        r"\d{1,2}",
        day_element.get_text(" ", strip=True),
    )

    if not day_match:
        return ""

    year, month = month_data

    try:
        parsed_date = date(
            year,
            month,
            int(day_match.group()),
        )
    except ValueError:
        return ""

    return parsed_date.isoformat()


def split_city_venue(value):
    """
    Alias combines location fields as 'Paris (La Cigale)'.
    """

    value = clean_text(value)

    match = re.fullmatch(
        r"(.+?)\s*\((.+)\)",
        value,
    )

    if not match:
        return "", ""

    city, venue = match.groups()

    return clean_text(city), clean_text(venue)


def find_ticket_url(card):
    link = card.select_one(
        ".concert_item-link a[href]"
    )

    if not link:
        return None

    href = clean_text(link.get("href"))

    return href or None


def parse_card(card):
    artist_element = card.select_one(
        ".concert_info h3"
    )
    location_element = card.select_one(
        ".concert_info p"
    )

    headliner = (
        clean_text(
            artist_element.get_text(" ", strip=True)
        )
        if artist_element
        else ""
    )
    location = (
        clean_text(
            location_element.get_text(" ", strip=True)
        )
        if location_element
        else ""
    )
    city, venue = split_city_venue(location)
    event_date = parse_date(card)

    if not event_date:
        return None

    if not headliner:
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
        openers=None,
        promoters=["Alias Production"],
        genre=None,
        facebook_event_url=None,
        ticket_url=find_ticket_url(card),
    )


def add_months(year, month, amount):
    month_index = year * 12 + month - 1 + amount

    return divmod(month_index, 12)[0], divmod(month_index, 12)[1] + 1


def get_initial_cards(session):
    print(f"Downloading {EVENTS_URL}...")

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
    events_section = soup.select_one(
        ".template-concerts.concert-page .sec2"
    )

    if events_section is None:
        raise RuntimeError(
            "Could not find Alias concert listings"
        )

    try:
        advertised_count = int(
            events_section.get("data-count") or 0
        )
    except ValueError:
        advertised_count = 0

    return (
        events_section.select("div.concert"),
        advertised_count,
    )


def fetch_more_cards(
    session,
    start_year,
    start_month,
    end_year,
    end_month,
):
    print(
        "Downloading Alias concerts "
        f"{start_year:04d}-{start_month:02d} "
        "through "
        f"{end_year:04d}-{end_month:02d}..."
    )

    response = session.get(
        AJAX_URL,
        params={
            "action": "more_concert_ajax",
            "date1": (
                f"{start_year:04d}"
                f"{start_month:02d}01"
            ),
            "date2": (
                f"{end_year:04d}"
                f"{end_month:02d}31"
            ),
            "vConcerts": 0,
            "ppp": -1,
        },
        headers={
            **HEADERS,
            "Referer": EVENTS_URL,
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    return soup.select("div.concert")


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
        event.city.casefold(),
    )


def load_events():
    session = requests.Session()
    cards, advertised_count = get_initial_cards(
        session
    )

    events_by_key = {}
    last_month = None

    for card in cards:
        event = parse_card(card)

        if event is not None:
            events_by_key[event_key(event)] = event

        card_month = parse_month(
            card.get("data-month")
        )

        if card_month is not None:
            last_month = card_month

    requests_made = 0

    while (
        last_month is not None
        and (
            not advertised_count
            or len(events_by_key) < advertised_count
        )
    ):
        start_year, start_month = add_months(
            *last_month,
            1,
        )
        end_year, end_month = add_months(
            start_year,
            start_month,
            2,
        )

        more_cards = fetch_more_cards(
            session,
            start_year,
            start_month,
            end_year,
            end_month,
        )

        if not more_cards:
            break

        new_events = 0

        for card in more_cards:
            event = parse_card(card)

            if event is not None:
                key = event_key(event)

                if key not in events_by_key:
                    events_by_key[key] = event
                    new_events += 1

        next_last_month = parse_month(
            more_cards[-1].get("data-month")
        )

        if (
            new_events == 0
            or next_last_month is None
            or next_last_month <= last_month
        ):
            break

        last_month = next_last_month
        requests_made += 1

        if requests_made >= 24:
            break

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Alias Production ConcertEvent records"
    )

    return events
