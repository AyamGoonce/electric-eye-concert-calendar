from math import ceil
from urllib.parse import urljoin

import requests

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Live Nation"

API_URL = "https://www.livenation.fr/__api/search/events"
BASE_URL = "https://www.livenation.fr"
REQUEST_TIMEOUT = 30
PAGE_SIZE = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.livenation.fr/event/allevents",
    "X-Culture": "fr-FR",
    "X-Site": "3",
}


def get_primary_headliner(document):
    lineup = document.get("lineup") or []

    for artist in lineup:
        if artist.get("isPrimary"):
            return (artist.get("name") or "").strip()

    for artist in lineup:
        if artist.get("type") == "headline":
            return (artist.get("name") or "").strip()

    return (document.get("name") or "").strip()


def get_openers(document, headliner):
    lineup = document.get("lineup") or []
    openers = []

    for artist in lineup:
        name = (artist.get("name") or "").strip()

        if not name:
            continue

        if name.casefold() == headliner.casefold():
            continue

        if name not in openers:
            openers.append(name)

    return openers[:5] or None


def get_genre(document):
    genres = document.get("genres") or []

    genre_names = [
        (genre.get("name") or "").strip()
        for genre in genres
        if (genre.get("name") or "").strip()
    ]

    return ", ".join(genre_names) or None


def get_ticket_url(document):
    tickets = document.get("tickets") or []

    for ticket in tickets:
        if not ticket.get("isVisible", True):
            continue

        url = (
            ticket.get("overrideUrl")
            or ticket.get("ticketUrl")
            or ""
        ).strip()

        if url:
            return urljoin(
                "https://www.livenation.fr",
                url,
            )

    direct_purchase = document.get("directPurchaseButton") or {}
    direct_url = (direct_purchase.get("url") or "").strip()

    if direct_url:
        return urljoin(
            "https://www.livenation.fr",
            direct_url,
        )

    return None


def get_event_url(document):
    localizations = document.get("localizations") or []

    for localization in localizations:
        if localization.get("cultureName") == "fr-FR":
            url = (localization.get("url") or "").strip()

            if url:
                return urljoin(BASE_URL, url)

    url = (document.get("url") or "").strip()

    if not url:
        return None

    return urljoin(BASE_URL, url)


def document_to_event(document):
    venue_data = document.get("venue") or {}

    headliner = get_primary_headliner(document)

    if not headliner:
        return None

    date = (
        document.get("eventDate")
        or document.get("eventDateUtc")
        or ""
    ).strip()

    if "T" in date:
        date = date.split("T", 1)[0]

    venue = (venue_data.get("name") or "").strip()
    city = (venue_data.get("city") or "").strip()

    if not date or not venue or not city:
        return None

    promoter = (document.get("promoter") or SOURCE_NAME).strip()

    ticket_url = get_ticket_url(document)
    event_url = get_event_url(document)

    return ConcertEvent(
        date=date,
        headliner=headliner,
        openers=get_openers(document, headliner),
        venue=venue,
        city=city,
        department="",
        promoters=[promoter] if promoter else [SOURCE_NAME],
        genre=get_genre(document),
        facebook_event_url=None,
        ticket_url=ticket_url or event_url,
    )


def fetch_page(page_number):
    response = requests.get(
        API_URL,
        params={
            "culture": "fr-FR",
            "Page": page_number,
            "PageSize": PAGE_SIZE,
        },
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    return response.json()


def load_events():
    first_page = fetch_page(1)

    total = first_page.get("total", 0)
    documents = list(first_page.get("documents") or [])

    total_pages = max(1, ceil(total / PAGE_SIZE))

    for page_number in range(2, total_pages + 1):
        page_data = fetch_page(page_number)
        documents.extend(page_data.get("documents") or [])

    events = []

    for document in documents:
        event = document_to_event(document)

        if event is not None:
            events.append(event)

    return events
