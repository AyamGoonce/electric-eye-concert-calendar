import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Supersonic"

SUPERSONIC_EVENTS_URL = "https://supersonic-club.fr/agenda/"
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


def parse_event_row(row, page_url):
    venue_id = (row.get("data-venue") or "").strip()

    if venue_id not in {"supersonic-2", "supersonic-records"}:
        return None

    title_element = row.select_one("h3")
    title_link = row.select_one("a.agenda-item-link")
    date_element = row.select_one("time[datetime]")
    venue_element = row.select_one(".agenda-item-venue")

    if not title_element or not title_link:
        return None

    full_title = title_element.get_text(" ", strip=True)

    if not full_title or is_non_concert_event(full_title):
        return None

    headliner = full_title

    performers = [
        part.strip()
        for part in re.split(r"\s*\+\s*", full_title)
        if part.strip()
    ]
    if len(performers) < 2:
        performers = None

    href = (title_link.get("href") or "").strip()

    return ConcertEvent(
        date=(
            date_element.get("datetime", "").strip()
            if date_element
            else ""
        ),
        headliner=headliner,
        raw_title=full_title,
        performers=performers,
        venue=(
            venue_element.get_text(" ", strip=True)
            if venue_element
            else (
                "Supersonic Records"
                if venue_id == "supersonic-records"
                else "Supersonic"
            )
        ),
        city="Paris",
        department="75",
        promoters=["Supersonic"],
        genre=None,
        facebook_event_url=None,
        ticket_url=urljoin(page_url, href) if href else None,
    )


def load_events():
    events = []
    visited_pages = set()
    page_url = SUPERSONIC_EVENTS_URL

    while page_url and page_url not in visited_pages:
        visited_pages.add(page_url)

        print(f"Downloading {page_url}...")

        response = None

        for attempt in range(1, 4):
            try:
                response = requests.get(
                    page_url,
                    timeout=REQUEST_TIMEOUT,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                            "AppleWebKit/537.36 Safari/537.36"
                        )
                    },
                )
                response.raise_for_status()
                break

            except requests.RequestException as error:
                print(
                    f"Supersonic request failed "
                    f"(attempt {attempt}/3): {error}"
                )

                if attempt == 3:
                    print(
                        f"Skipping Supersonic page after 3 failed attempts: "
                        f"{page_url}"
                    )
                    response = None

        if response is None:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        event_rows = soup.select(
            "li.agenda-item"
        )

        for row in event_rows:
            event = parse_event_row(row, page_url)
            if event is not None:
                events.append(event)

        page_url = None

    print(f"Created {len(events)} Supersonic ConcertEvent records")

    return events
