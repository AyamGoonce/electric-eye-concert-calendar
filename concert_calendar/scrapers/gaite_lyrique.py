import json
import re
import unicodedata

from datetime import date
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup

from concert_calendar.event_images import (
    discard_repeated_generic_images,
    element_image_url,
)
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "La Gaîté Lyrique"
AGENDA_URL = "https://www.gaite-lyrique.net/agenda/"
REQUEST_TIMEOUT = 30
MAX_PAGES = 7

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    )
}

MONTHS = {
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


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def folded(value):
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", clean(value))
        if not unicodedata.combining(character)
    ).casefold()


def parse_date(value):
    match = re.search(
        r"\b(\d{1,2})\s+([a-z]+)\s+(20\d{2})\b",
        folded(value),
    )

    if not match or match.group(2) not in MONTHS:
        return None

    try:
        return date(
            int(match.group(3)),
            MONTHS[match.group(2)],
            int(match.group(1)),
        )
    except ValueError:
        return None


def _stable_names(values):
    result = []
    seen = set()

    for value in values:
        value = clean(value)
        key = value.casefold()

        if value and key not in seen:
            seen.add(key)
            result.append(value)

    return result


def _jsonld_performers(soup, event_title):
    result = []

    def visit(value):
        if isinstance(value, list):
            for item in value:
                visit(item)
            return

        if not isinstance(value, dict):
            return

        event_type = value.get("@type")
        types = event_type if isinstance(event_type, list) else [event_type]

        if ("Event" in types or "MusicEvent" in types) and folded(value.get("name")) == folded(event_title):
            performer = value.get("performer")

            if not isinstance(performer, list):
                performer = [performer] if performer else []

            for item in performer:
                if isinstance(item, dict):
                    result.append(item.get("name"))
                elif isinstance(item, str):
                    result.append(item)

        for nested in value.values():
            if isinstance(nested, (dict, list)):
                visit(nested)

    for script in soup.find_all(
        "script",
        attrs={"type": "application/ld+json"},
    ):
        try:
            visit(json.loads(script.string or script.get_text()))
        except (TypeError, ValueError, json.JSONDecodeError):
            continue

    names = _stable_names(result)

    # A programme title repeated as the sole "performer" is not evidence.
    names = [
        name
        for name in names
        if name.casefold() != clean(event_title).casefold()
    ]

    return names if len(names) >= 2 else []


def detail_performers(html, event_title):
    """
    Return independently evidenced performers from the official detail page.

    Structured Event performer metadata is preferred. The heading fallback is
    deliberately conservative and requires a comma-separated artist list.
    """
    soup = BeautifulSoup(html, "html.parser")

    structured = _jsonld_performers(soup, event_title)
    if structured:
        return structured

    heading = soup.find("h1")
    value = clean(
        heading.get_text(" ", strip=True)
        if heading
        else ""
    )
    title = clean(event_title)

    if (
        not value
        or not title
        or not value.casefold().startswith(title.casefold())
    ):
        return []

    remainder = clean(value[len(title):]).lstrip(" :-–—")

    if not remainder:
        return []

    sentence = re.split(
        r"\s+(?:sont|seront|est|sera|are|will be)\s+",
        remainder,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip(" :-–—")

    # Avoid treating an ambiguous two-part '&' band/project name as two acts.
    if "," not in sentence:
        return []

    performers = _stable_names(
        re.split(
            r"\s*(?:,|&|\bet\b|\band\b)\s*",
            sentence,
            flags=re.IGNORECASE,
        )
    )

    if not 2 <= len(performers) <= 8:
        return []

    if any(
        len(name) > 70 or len(name.split()) > 8
        for name in performers
    ):
        return []

    return performers


def parse_card(card, session=None):
    categories = {
        folded(anchor.get_text(" ", strip=True))
        for anchor in card.select(".event-categories a")
    }

    if "musique" not in categories:
        return None

    date_group = card.find_parent("li", class_="events-date")
    heading = (
        date_group.find(
            "h2",
            class_="events-date-title",
            recursive=False,
        )
        if date_group
        else None
    )

    event_date = parse_date(
        heading.get_text(" ", strip=True)
        if heading
        else ""
    )

    title = card.select_one(".event-title a[href]")
    headliner = clean(
        title.get_text(" ", strip=True)
        if title
        else ""
    )

    if (
        not event_date
        or event_date < date.today()
        or not headliner
    ):
        return None

    image_url = element_image_url(
        card.select_one(".media img"),
        base_url=AGENDA_URL,
    )

    detail_url = urljoin(
        AGENDA_URL,
        clean(title.get("href")),
    )

    performers = []

    if session and detail_url:
        try:
            response = session.get(
                detail_url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            performers = detail_performers(
                response.text,
                headliner,
            )
        except requests.RequestException:
            # Detail enrichment must never make the agenda source unusable.
            performers = []

    return ConcertEvent(
        date=event_date.isoformat(),
        headliner=headliner,
        venue=SOURCE_NAME,
        city="Paris",
        department="75",
        ticket_url=detail_url,
        image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
        event_title=headliner if performers else None,
        performers=performers or None,
    )


def load_events():
    events = {}
    session = requests.Session()

    for page in range(1, MAX_PAGES + 1):
        url = (
            AGENDA_URL
            if page == 1
            else urljoin(AGENDA_URL, f"page/{page}/")
        )

        response = session.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        if page > 1 and response.status_code == 404:
            break
        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        cards = soup.select("article.event")

        if not cards:
            break

        for card in cards:
            event = parse_card(
                card,
                session=session,
            )

            if event:
                events.setdefault(
                    (
                        event.date,
                        event.headliner.casefold(),
                        event.venue.casefold(),
                    ),
                    event,
                )

    return discard_repeated_generic_images(
        list(events.values())
    )
