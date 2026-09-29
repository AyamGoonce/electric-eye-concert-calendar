import json
import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import official_image_url, discard_repeated_generic_images
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
    """A title alone does not establish individual artists or support roles."""
    return clean_text(value), None


def evidenced_billing(title, *, team_love="", description=""):
    """Interpret separators only when current-event prose establishes roles."""
    raw = clean_text(title)
    prose = clean_text(
        BeautifulSoup(team_love or "", "html.parser").get_text(" ", strip=True)
    )

    def named_in(text, artist):
        return bool(re.search(r"(?<![\w@])" + re.escape(artist) + r"(?!\w)", text, re.I))

    plus_parts = [clean_text(part) for part in re.split(r"\s+\+\s+", raw)]
    if len(plus_parts) >= 2:
        role = re.search(
            r"\b(?:en support|supported by|accompagn[ée] de|joined by)\b",
            prose,
            re.I,
        )
        if role and all(named_in(prose[role.end():], part) for part in plus_parts[1:]):
            return plus_parts[0], plus_parts[1:], None

    if re.search(r"\b(?:double|triple)\s+(?:affiche|bill)\b", prose, re.I):
        description_soup = BeautifulSoup(description or "", "html.parser")
        paragraphs = [node.get_text(" ", strip=True) for node in description_soup.select("p")]
        billed = clean_text(
            paragraphs[0] if paragraphs else description_soup.get_text(" ", strip=True)
        )
        full_parts = [clean_text(part) for part in re.split(r"\s+\+\s+", billed)]
        title_parts = [
            clean_text(part)
            for part in re.split(r"\s+(?:\+|x|×)\s+", raw, flags=re.I)
        ]
        if (
            len(full_parts) >= len(title_parts) >= 2
            and [part.casefold() for part in full_parts[:len(title_parts)]]
            == [part.casefold() for part in title_parts]
            and all(named_in(prose, part) for part in full_parts)
        ):
            return full_parts[0], None, full_parts
        if len(title_parts) >= 2 and all(named_in(prose, part) for part in title_parts):
            return title_parts[0], None, title_parts
    return raw, None, None


def strapi_event_image(attributes):
    for field in ("imageList", "imageCover"):
        media = (((attributes.get(field) or {}).get("data") or {}).get("attributes") or {})
        formats = media.get("formats") or {}
        for format_name in ("list", "mood", "large"):
            candidate = formats.get(format_name) or {}
            if url := official_image_url(
                candidate.get("url"),
                width=candidate.get("width"),
                height=candidate.get("height"),
            ):
                return url
        if url := official_image_url(
            media.get("url"), width=media.get("width"), height=media.get("height")
        ):
            return url
    return None


def parse_document(document):
    attributes = document.get("attributes") or {}
    event_date = clean_text(attributes.get("date"))[:10]
    status_uid = relation_uid(attributes.get("status")).casefold()
    raw_title = clean_text(attributes.get("title"))
    headliner, openers, performers = evidenced_billing(
        raw_title,
        team_love=attributes.get("teamLove") or "",
        description=attributes.get("description") or "",
    )

    if not is_concert(attributes):
        return None

    if status_uid in CANCELLED_STATUS_UIDS:
        return None

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", event_date):
        return None

    if event_date < date.today().isoformat() or not headliner:
        return None

    ticket_url = clean_text(attributes.get("ticketingUrl"))
    image_url = strapi_event_image(attributes)

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
        co_headliners=performers[1:] if performers else None,
        performers=performers,
        raw_title=raw_title if headliner != raw_title else None,
        event_title=raw_title if headliner != raw_title else None,
        identity_aliases=[raw_title] if headliner != raw_title else None,
        venue="Bataclan",
        city="Paris",
        department="75",
        openers=openers,
        promoters=None,
        genre=relation_title(attributes.get("genre")) or None,
        facebook_event_url=None,
        ticket_url=ticket_url or AGENDA_URL,
        sold_out=("complet" in status_uid or "sold-out" in status_uid),
        image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
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

    return discard_repeated_generic_images(events)
