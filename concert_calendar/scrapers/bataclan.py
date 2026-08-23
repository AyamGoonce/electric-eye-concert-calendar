import json
import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Bataclan"

AGENDA_URL = "https://www.bataclan.fr/agenda/"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

CANCELLED_STATUS_UIDS = {
    "annule",
    "cancelled",
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def decode_nuxt_payload(payload):
    """Decode the reference-array format emitted by Nuxt/devalue."""

    decoded = {}

    def decode_index(index):
        if index in decoded:
            return decoded[index]

        value = payload[index]

        if isinstance(value, dict):
            result = {}
            decoded[index] = result
            result.update(
                {
                    key: (
                        decode_index(item)
                        if isinstance(item, int) and item >= 0
                        else item
                    )
                    for key, item in value.items()
                }
            )
            return result

        if isinstance(value, list):
            if (
                value
                and isinstance(value[0], str)
                and value[0] in {"ShallowReactive", "Reactive", "Ref"}
            ):
                result = decode_index(value[1])
                decoded[index] = result
                return result

            if value and value[0] == "Date":
                result = decode_index(value[1])
                decoded[index] = result
                return result

            result = []
            decoded[index] = result
            result.extend(
                decode_index(item)
                if isinstance(item, int) and item >= 0
                else item
                for item in value
            )
            return result

        return value

    return decode_index(0)


def relation_title(value):
    data = (value or {}).get("data") or {}
    return clean_text((data.get("attributes") or {}).get("title"))


def relation_uid(value):
    data = (value or {}).get("data") or {}
    return clean_text((data.get("attributes") or {}).get("uid"))


def is_concert(attributes):
    if relation_title(attributes.get("type")).casefold() == (
        "concert & festival"
    ):
        return True

    return any(
        clean_text(meeting.get("genre")).casefold()
        == "concert & festival"
        for meeting in (attributes.get("meetings") or [])
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
    attributes = document.get("attributes") or {}
    event_date = clean_text(attributes.get("date"))[:10]
    status_uid = relation_uid(attributes.get("status")).casefold()
    headliner, openers = split_bill(attributes.get("title"))

    if not is_concert(attributes):
        return None

    if status_uid in CANCELLED_STATUS_UIDS:
        return None

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", event_date):
        return None

    if event_date < date.today().isoformat() or not headliner:
        return None

    ticket_url = clean_text(attributes.get("ticketingUrl"))

    if not ticket_url:
        meetings = attributes.get("meetings") or []
        ticket_url = next(
            (
                clean_text(meeting.get("url"))
                for meeting in meetings
                if clean_text(meeting.get("url"))
            ),
            "",
        )

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue="Bataclan",
        city="Paris",
        department="75",
        openers=openers,
        promoters=None,
        genre=relation_title(attributes.get("genre")) or None,
        facebook_event_url=None,
        ticket_url=ticket_url or AGENDA_URL,
        sold_out=("complet" in status_uid or "sold-out" in status_uid),
    )


def event_key(event):
    return (
        event.date,
        (event.ticket_url or event.headliner).casefold(),
        event.venue.casefold(),
    )


def load_events():
    session = requests.Session()

    print("Downloading Bataclan agenda...")

    response = session.get(
        AGENDA_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    soup = BeautifulSoup(response.text, "html.parser")
    payload_element = soup.select_one("script[data-nuxt-data][data-src]")

    if payload_element is None:
        response.raise_for_status()
        return []

    payload_url = urljoin(
        AGENDA_URL,
        clean_text(payload_element.get("data-src")),
    )

    print("Downloading Bataclan Nuxt payload...")

    payload_response = session.get(
        payload_url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    payload_response.raise_for_status()
    root = decode_nuxt_payload(json.loads(payload_response.text))
    documents = root["data"]["events"]["data"]
    events_by_key = {}

    documents = sorted(
        documents,
        key=lambda item: (
            (item.get("attributes") or {}).get("locale") != "fr",
        ),
    )

    for document in documents:
        event = parse_document(document)

        if event is None:
            continue

        key = event_key(event)
        existing = events_by_key.get(key)

        if existing is None or (
            event.openers and not existing.openers
        ):
            events_by_key[key] = event

    events = list(events_by_key.values())

    print(f"Created {len(events)} Bataclan ConcertEvent records")

    return events
