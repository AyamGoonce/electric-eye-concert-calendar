import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Supersonic"

SUPERSONIC_EVENTS_URL = "https://supersonic-club.fr/events/"
REQUEST_TIMEOUT = 30


def normalize_text_for_matching(text):
    normalized = unicodedata.normalize("NFKD", text or "")
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return normalized.casefold()


def is_non_concert_event(title):
    normalized_title = normalize_text_for_matching(title)

    excluded_patterns = [
        r"\bpackage\b",
        r"\bvip\b",
        r"\bafterparty\b",
        r"\bafter party\b",
        r"\bclub night\b",
        r"\bdj set\b",
        r"\bdj night\b",
        r"\bkaraoke\b",
        r"\bdancefloor\b",
        r"\bdance floor\b",
        r"\bparty\b",
        r"\bsoiree\b",
        r"\bnuit\b",
        r"\bdisco\b",
        r"\btribute\b",
        r"\bjeudi disco\b",
        r"\bdancing with myself\b",
        r"\bwhere is my mind\b",
        r"\bone more time\b",
        r"\bcommon people\b",
        r"\bas it was\b",
        r"\bfriday i'm in love\b",
        r"\brock around the clock\b",
        r"\bamerican idiot\b",
        r"\btrilogie du samedi\b",
    ]

    return any(
        re.search(pattern, normalized_title)
        for pattern in excluded_patterns
    )


def load_events():
    events = []
    visited_pages = set()
    page_url = SUPERSONIC_EVENTS_URL

    while page_url and page_url not in visited_pages:
        visited_pages.add(page_url)

        print(f"Downloading {page_url}...")

        response = requests.get(
            page_url,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        event_rows = soup.select(
            ".tribe-events-calendar-list__event-row"
        )

        for row in event_rows:
            title_link = row.select_one(
                ".tribe-events-calendar-list__event-title-link"
            )

            date_element = row.select_one(
                ".tribe-events-calendar-list__event-datetime"
            )

            venue_element = row.select_one(
                ".tribe-events-calendar-list__event-venue-title"
            )

            if not title_link:
                continue

            full_title = title_link.get_text(" ", strip=True)

            if not full_title:
                continue

            artists = [
                artist.strip()
                for artist in full_title.split("•")
                if artist.strip()
            ]

            headliner = artists[0] if artists else full_title
            openers = artists[1:6] or None

            date = (
                date_element.get("datetime", "").strip()
                if date_element
                else ""
            )

            venue = (
                venue_element.get_text(" ", strip=True)
                if venue_element
                else "Supersonic"
            )

            if is_non_concert_event(full_title):
                print(f"Excluded non-concert event: {full_title}")
                continue

            event = ConcertEvent(
                date=date,
                headliner=headliner,
                openers=openers,
                venue=venue,
                city="Paris",
                department="75",
                promoters=["Supersonic"],
                genre=None,
                facebook_event_url=None,
                ticket_url=None,
            )

            events.append(event)

        next_link = soup.select_one(
            "a.tribe-events-c-nav__next"
        )

        if next_link:
            next_href = next_link.get("href", "").strip()

            page_url = (
                urljoin(page_url, next_href)
                if next_href
                else None
            )
        else:
            page_url = None

    print(f"Created {len(events)} Supersonic ConcertEvent records")

    return events
