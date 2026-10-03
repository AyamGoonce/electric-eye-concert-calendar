import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Supersonic"

SUPERSONIC_EVENTS_URL = "https://supersonic-club.fr/agenda/"
REQUEST_TIMEOUT = 30

LINEUP_CONTEXT_RE = re.compile(
    r"^[^:]+\b(?:fest(?:ival)?|tour)\b\s*:|"
    r"^[^:]+\s*:\s*[^:]+\b(?:fest(?:ival)?|tour)\b",
    re.IGNORECASE,
)
TGBB_PREFIX_RE = re.compile(r"^TGBB\s+fest\s*:\s*(?P<artist>.+)$", re.IGNORECASE)


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


def needs_detail_lineup(title):
    billing_parts = re.split(r"\s*\+\s*", title or "", maxsplit=1)
    if len(billing_parts) < 2:
        return False
    first_billing_part = billing_parts[0]
    return bool(LINEUP_CONTEXT_RE.search(first_billing_part))


def parse_detail_lineup(html):
    soup = BeautifulSoup(html or "", "html.parser")
    return [
        name
        for element in soup.select(".lineup .horaire-name")
        if (name := element.get_text(" ", strip=True))
        and normalize_text_for_matching(name) not in {
            "ouverture des portes",
            "doors",
            "doors open",
        }
    ]


def normalize_structured_performers(title, lineup_names=None):
    performers = [
        part.strip()
        for part in re.split(r"\s*\+\s*", title or "")
        if part.strip()
    ]
    if len(performers) < 2:
        return None, None

    lineup_names = [name.strip() for name in lineup_names or [] if name.strip()]
    lineup_by_key = {
        normalize_text_for_matching(name): name
        for name in lineup_names
    }
    normalized = []
    first_was_contextual = False
    first_was_proven = False
    for index, performer in enumerate(performers):
        performer_key = normalize_text_for_matching(performer)
        exact = lineup_by_key.get(performer_key)
        if exact:
            normalized.append(exact)
            if index == 0:
                first_was_proven = True
            continue

        if index == 0 and needs_detail_lineup(title):
            tgbb_match = TGBB_PREFIX_RE.fullmatch(performer)
            if tgbb_match:
                artist = tgbb_match.group("artist").strip()
                normalized.append(
                    lineup_by_key.get(normalize_text_for_matching(artist), artist)
                )
                first_was_contextual = True
                first_was_proven = True
                continue
            matches = [
                name for name in lineup_names
                if re.search(
                    rf"(?<!\w){re.escape(normalize_text_for_matching(name))}(?!\w)",
                    performer_key,
                )
            ]
            if len(matches) == 1:
                normalized.append(matches[0])
                first_was_contextual = True
                first_was_proven = True
                continue

        normalized.append(performer)

    if needs_detail_lineup(title) and not first_was_proven:
        return None, None
    return normalized, normalized[0] if first_was_contextual else None


def load_detail_lineup(url):
    for attempt in range(1, 4):
        try:
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 Safari/537.36"
                    )
                },
            )
            response.raise_for_status()
            return parse_detail_lineup(response.text)
        except requests.RequestException as error:
            print(
                "Supersonic detail request failed "
                f"(attempt {attempt}/3): {error}"
            )
    return []


def parse_event_row(row, page_url, *, lineup_names=None):
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

    performers, structured_headliner = normalize_structured_performers(
        full_title,
        lineup_names=lineup_names,
    )
    headliner = structured_headliner or full_title

    href = (title_link.get("href") or "").strip()

    return ConcertEvent(
        date=(
            date_element.get("datetime", "").strip()
            if date_element
            else ""
        ),
        headliner=headliner,
        raw_title=full_title,
        event_title=full_title if structured_headliner else None,
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
            title_element = row.select_one("h3")
            title_link = row.select_one("a.agenda-item-link")
            title = title_element.get_text(" ", strip=True) if title_element else ""
            detail_url = urljoin(
                page_url,
                (title_link.get("href") or "").strip(),
            ) if title_link else ""
            lineup_names = (
                load_detail_lineup(detail_url)
                if detail_url and needs_detail_lineup(title)
                else None
            )
            event = parse_event_row(
                row,
                page_url,
                lineup_names=lineup_names,
            )
            if event is not None:
                events.append(event)

        page_url = None

    print(f"Created {len(events)} Supersonic ConcertEvent records")

    return events
