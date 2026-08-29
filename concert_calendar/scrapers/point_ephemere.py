import re
from datetime import date, timedelta

import requests

from concert_calendar.event_images import official_image_url, discard_repeated_generic_images
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Point Éphémère"

REPOSITORY_URL = "https://pointf.cdn.prismic.io/api/v2"
EVENT_URL_TEMPLATE = "https://www.pointephemere.org/event/{uid}"
REQUEST_TIMEOUT = 30
PAGE_SIZE = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def link_url(value):
    if not isinstance(value, dict):
        return None

    return clean_text(value.get("url")) or None


def prismic_event_image(value):
    if not isinstance(value, dict):
        return None
    dimensions = value.get("dimensions") or {}
    return official_image_url(
        value.get("url"),
        width=dimensions.get("width"),
        height=dimensions.get("height"),
    )


def split_bill(value):
    artists = [
        clean_text(part)
        for part in re.split(r"\s+\+\s+", clean_text(value))
    ]
    artists = [artist for artist in artists if artist]

    if not artists:
        return "", None

    return artists[0], artists[1:] or None


def parse_document(document):
    data = document.get("data") or {}
    event_date = clean_text(data.get("start_date"))
    headliner, openers = split_bill(data.get("name"))
    uid = clean_text(document.get("uid"))
    image_url = prismic_event_image(data.get("cover"))

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", event_date):
        return None

    if len(re.sub(r"\W", "", headliner)) < 2:
        return None

    if not uid:
        return None

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue="Point Éphémère",
        city="Paris",
        department="75",
        openers=openers,
        promoters=None,
        genre=clean_text(data.get("displayed_category")) or None,
        facebook_event_url=link_url(data.get("facebook_link")),
        ticket_url=(
            link_url(data.get("ticket_link"))
            or EVENT_URL_TEMPLATE.format(uid=uid)
        ),
        image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
    )


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
    )


def load_events():
    session = requests.Session()

    print("Reading Point Éphémère repository...")

    repository_response = session.get(
        REPOSITORY_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    repository_response.raise_for_status()
    repository = repository_response.json()
    master_ref = next(
        item["ref"]
        for item in repository.get("refs", [])
        if item.get("isMasterRef")
    )
    search_url = repository["forms"]["everything"]["action"]
    earliest_date = (date.today() - timedelta(days=1)).isoformat()
    events_by_key = {}

    for page_number in range(1, 101):
        print(f"Downloading Point Éphémère page {page_number}...")

        response = session.get(
            search_url,
            params=[
                ("ref", master_ref),
                ("q", '[[at(document.type,"event")]]'),
                (
                    "q",
                    "[[date.after(my.event.start_date,"
                    f'"{earliest_date}")]]',
                ),
                ("q", '[[at(my.event.category,"Concerts")]]'),
                ("page", page_number),
                ("pageSize", PAGE_SIZE),
                ("orderings", "[my.event.start_date]"),
            ],
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        documents = payload.get("results", [])

        if not documents:
            break

        new_events = 0

        for document in documents:
            event = parse_document(document)

            if event is None:
                continue

            key = event_key(event)

            if key not in events_by_key:
                events_by_key[key] = event
                new_events += 1

        if new_events == 0:
            break

        if page_number >= payload.get("total_pages", page_number):
            break

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Point Éphémère ConcertEvent records"
    )

    return discard_repeated_generic_images(events)
