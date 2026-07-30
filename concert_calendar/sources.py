import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.geography import (
    is_ile_de_france_event,
    normalize_event_geography,
)
from concert_calendar.models import ConcertEvent
from concert_calendar.promoters import normalize_event_promoters
from concert_calendar.venues import normalize_event_venue


GDP_EVENTS_URL = "https://www.gdp.fr/fr/agenda"
SUPERSONIC_EVENTS_URL = "https://supersonic-club.fr/events/"

REQUEST_TIMEOUT = 30


def normalize_text_for_matching(text):
    """
    Return lowercase, accent-free text for reliable comparisons.
    """

    normalized = unicodedata.normalize("NFKD", text or "")
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return normalized.casefold()


def is_non_concert_event(title):
    """
    Return True for club nights, parties, tribute events, VIP packages
    and other listings that are not concerts within the calendar scope.
    """

    normalized_title = normalize_text_for_matching(title)

    excluded_patterns = [
        # VIP and commercial package listings
        r"\bpackage\b",
        r"\bvip\b",

        # Club nights, parties and DJ events
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

        # Tribute events
        r"\btribute\b",

        # Recurring or branded nightlife formats
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


def is_supported_event(event):
    """
    Return True only for events that belong in the concert calendar.
    """

    if is_non_concert_event(event.headliner):
        return False

    normalized_title = normalize_text_for_matching(event.headliner)
    normalized_genre = normalize_text_for_matching(event.genre or "")

    excluded_scope_patterns = [
        r"\bone man show\b",
        r"\bstand[- ]?up\b",
        r"\bhumour\b",
        r"\bcomedy\b",
        r"\btheatre\b",
        r"\bconference\b",
        r"\bmasterclass\b",
    ]

    combined_text = f"{normalized_title} {normalized_genre}"

    return not any(
        re.search(pattern, combined_text)
        for pattern in excluded_scope_patterns
    )


def load_gdp_events():
    print(f"Downloading {GDP_EVENTS_URL}...")

    response = requests.get(
        GDP_EVENTS_URL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    event_cards = soup.select("div.gdpEvtCardCtnt")

    events = []

    for card in event_cards:
        artist_element = card.select_one(".gdpEvtCardName")
        genre_element = card.select_one(".gdpEvtCardGenre")
        date_element = card.select_one(".gdpEvtCardDate")
        city_element = card.select_one(".gdpEvtCardCity")
        venue_element = card.select_one(".gdpEvtCardVenue")
        link_element = card.select_one(".gdpEvtCardName a")

        headliner = (
            artist_element.get_text(" ", strip=True)
            if artist_element
            else ""
        )

        genre = (
            genre_element.get_text(" ", strip=True)
            if genre_element
            else None
        )

        date = (
            date_element.get("datetime", "").strip()
            if date_element
            else ""
        )

        city = (
            city_element.get_text(" ", strip=True)
            if city_element
            else ""
        )

        venue = (
            venue_element.get_text(" ", strip=True)
            if venue_element
            else ""
        )

        ticket_url = None

        if link_element:
            href = link_element.get("href", "").strip()

            if href:
                ticket_url = urljoin(GDP_EVENTS_URL, href)

        if not headliner:
            continue

        event = ConcertEvent(
            date=date,
            headliner=headliner,
            venue=venue,
            city=city,
            department="",
            promoters=["GDP"],
            genre=genre,
            ticket_url=ticket_url,
        )

        if not is_supported_event(event):
            print(f"Excluded non-concert event: {headliner}")
            continue

        events.append(event)

    print(f"Created {len(events)} GDP ConcertEvent records")

    return events


def load_supersonic_events():
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

            if not is_supported_event(event):
                print(f"Excluded non-concert event: {full_title}")
                continue

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


def load_events():
    raw_events = []

    raw_events.extend(load_gdp_events())
    raw_events.extend(load_supersonic_events())

    normalized_events = []

    for event in raw_events:
        normalize_event_geography(event)
        normalize_event_venue(event)
        normalize_event_promoters(event)
        normalized_events.append(event)

    filtered_events = []

    for event in normalized_events:
        if not is_ile_de_france_event(event):
            print(
                "Excluded outside Île-de-France: "
                f"{event.headliner} — {event.city}"
            )
            continue

        filtered_events.append(event)

    deduplicated_events = deduplicate_events(filtered_events)

    print()
    print(f"Created {len(raw_events)} raw ConcertEvent records")
    print(
        f"Normalized {len(normalized_events)} "
        "ConcertEvent records"
    )
    print(
        f"Created {len(filtered_events)} "
        "Île-de-France ConcertEvent records before deduplication"
    )
    print(
        f"Created {len(deduplicated_events)} "
        "Île-de-France ConcertEvent records after deduplication"
    )

    return deduplicated_events