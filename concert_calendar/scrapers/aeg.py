import json
import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "AEG Presents France"

API_URL = "https://www.aegpresents.fr/wp-json/dest/v1/events"
BASE_URL = "https://www.aegpresents.fr"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
    "Accept": "application/json",
}


FRENCH_MONTHS = {
    "janv": 1,
    "janvier": 1,
    "fevr": 2,
    "fevrier": 2,
    "mars": 3,
    "avr": 4,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juil": 7,
    "juillet": 7,
    "aout": 8,
    "sept": 9,
    "septembre": 9,
    "oct": 10,
    "octobre": 10,
    "nov": 11,
    "novembre": 11,
    "dec": 12,
    "decembre": 12,
}


def normalize_month_name(value):
    value = (value or "").lower().strip()
    value = value.replace(".", "")

    replacements = {
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "ä": "a",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ô": "o",
        "ö": "o",
        "î": "i",
        "ï": "i",
        "ç": "c",
    }

    for original, replacement in replacements.items():
        value = value.replace(original, replacement)

    return value


def parse_french_date(text):
    """
    Parse strings such as:
        '11 sept.'
        '23 Août'

    Return:
        (month, day)
    """

    cleaned = re.sub(r"\s+", " ", text or "").strip()

    match = re.search(
        r"(\d{1,2})\s+([A-Za-zÀ-ÿ.]+)",
        cleaned,
    )

    if not match:
        return None

    day = int(match.group(1))
    month_name = normalize_month_name(match.group(2))
    month = FRENCH_MONTHS.get(month_name)

    if month is None:
        return None

    return month, day


def split_venue_city(text):
    """
    Split AEG venue text into venue and city.

    Example:
        "Fête de l'Humanité - Brétigny-sur-Orge"
    """

    cleaned = re.sub(r"\s+", " ", text or "").strip()

    for separator in (" – ", " - "):
        if separator in cleaned:
            venue, city = cleaned.rsplit(separator, 1)

            return (
                venue.strip(),
                city.strip(),
            )

    return cleaned, ""


def get_json_ld_event(soup):
    """
    Return the Event JSON-LD object from an AEG detail page.
    """

    for script in soup.find_all(
        "script",
        type="application/ld+json",
    ):
        raw = script.get_text(strip=True)

        if not raw:
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        objects = data if isinstance(data, list) else [data]

        for obj in objects:
            if (
                isinstance(obj, dict)
                and obj.get("@type") == "Event"
            ):
                return obj

    return {}


def find_ticket_url(event_details, detail_url):
    """
    Look around an individual performance row for its booking link.

    If AEG does not expose a separate ticket link in that row,
    fall back to the AEG event detail page.
    """

    container = event_details

    for _ in range(4):
        if container is None:
            break

        links = container.find_all("a", href=True)

        for link in links:
            text = link.get_text(" ", strip=True).casefold()

            if (
                "réserver" in text
                or "reserver" in text
                or "billet" in text
                or "ticket" in text
            ):
                href = link.get("href", "").strip()

                if href:
                    return urljoin(detail_url, href)

        container = container.parent

    return detail_url


def parse_detail_page(detail_url, headliner):
    """
    Expand one AEG artist/event page into individual ConcertEvent
    records.
    """

    response = requests.get(
        detail_url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    json_ld = get_json_ld_event(soup)

    start_date = json_ld.get("startDate") or ""

    try:
        starting_year = int(start_date[:4])
    except (TypeError, ValueError):
        starting_year = date.today().year

    event_rows = soup.select(".event-details")

    events = []

    current_year = starting_year
    previous_month = None

    for row in event_rows:
        date_element = row.select_one(".event-date")
        venue_element = row.select_one(".event-venue")

        if not date_element or not venue_element:
            continue

        parsed_date = parse_french_date(
            date_element.get_text(" ", strip=True)
        )

        if parsed_date is None:
            continue

        month, day = parsed_date

        if (
            previous_month is not None
            and month < previous_month
        ):
            current_year += 1

        previous_month = month

        venue, city = split_venue_city(
            venue_element.get_text(" ", strip=True)
        )

        if not venue or not city:
            continue

        iso_date = (
            f"{current_year:04d}-"
            f"{month:02d}-"
            f"{day:02d}"
        )

        ticket_url = find_ticket_url(
            row,
            detail_url,
        )

        event = ConcertEvent(
            date=iso_date,
            headliner=headliner,
            venue=venue,
            city=city,
            department="",
            openers=None,
            promoters=["AEG Presents France"],
            genre=None,
            facebook_event_url=None,
            ticket_url=ticket_url,
        )

        events.append(event)

    return events


def fetch_api_page(page_number, page_parameter):
    response = requests.get(
        API_URL,
        params={
            page_parameter: page_number,
        },
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    return response.json()


def determine_page_parameter():
    """
    Detect whether the AEG API expects 'page' or 'paged'.
    """

    for parameter in ("page", "paged"):
        try:
            data = fetch_api_page(2, parameter)
        except requests.RequestException:
            continue

        pager = data.get("pager") or {}

        try:
            current_page = int(
                pager.get("currentPage", 0)
            )
        except (TypeError, ValueError):
            current_page = 0

        if current_page == 2:
            return parameter

    raise RuntimeError(
        "Could not determine AEG API pagination parameter"
    )


def get_detail_pages_from_api():
    """
    Retrieve all unique AEG event detail URLs.
    """

    first_response = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    first_response.raise_for_status()

    first_page = first_response.json()
    pager = first_page.get("pager") or {}

    total_pages = int(
        pager.get("totalPages", 1)
    )

    page_parameter = determine_page_parameter()

    detail_pages = {}

    for page_number in range(1, total_pages + 1):
        print(
            f"Downloading AEG page "
            f"{page_number}/{total_pages}..."
        )

        if page_number == 1:
            data = first_page
        else:
            data = fetch_api_page(
                page_number,
                page_parameter,
            )

        items_html = data.get("items") or ""

        soup = BeautifulSoup(
            items_html,
            "html.parser",
        )

        for card in soup.select(
            ".events-listings-card"
        ):
            artist_link = card.select_one(
                ".event-listings-artist a[href]"
            )

            if not artist_link:
                continue

            headliner = artist_link.get_text(
                " ",
                strip=True,
            )

            detail_url = (
                artist_link.get("href", "")
                .strip()
            )

            if not headliner or not detail_url:
                continue

            detail_url = urljoin(
                BASE_URL,
                detail_url,
            )

            detail_pages[detail_url] = headliner

    return detail_pages


def load_events():
    detail_pages = get_detail_pages_from_api()

    print(
        f"Found {len(detail_pages)} "
        "unique AEG event pages"
    )

    events = []

    for index, (detail_url, headliner) in enumerate(
        detail_pages.items(),
        start=1,
    ):
        print(
            f"Reading AEG event "
            f"{index}/{len(detail_pages)}: "
            f"{headliner}"
        )

        try:
            page_events = parse_detail_page(
                detail_url,
                headliner,
            )
        except requests.RequestException as error:
            print(
                f"Failed AEG event page: "
                f"{detail_url} — {error}"
            )
            continue

        events.extend(page_events)

    return events
