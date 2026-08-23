import re
import unicodedata

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.geography import (
    is_ile_de_france_event,
    normalize_event_geography,
)
from concert_calendar.promoters import normalize_event_promoters
from concert_calendar.scraper_loader import discover_scrapers
from concert_calendar.venues import normalize_event_venue


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


def is_non_supported_event(title):
    """
    Return True for packages, club nights, parties, tribute events
    and other listings outside the calendar's scope.
    """

    normalized_title = normalize_text_for_matching(title)

    party_is_concert_billing = bool(
        re.search(r"\brelease party\b", normalized_title)
        or re.match(
            r"^bloc party(?:\s*\+|$)",
            normalized_title,
        )
    )

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
        r"\bsoiree\b",
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

    if (
        re.search(r"\bparty\b", normalized_title)
        and not party_is_concert_billing
    ):
        return True

    return any(
        re.search(pattern, normalized_title)
        for pattern in excluded_patterns
    )


def is_supported_event(event):
    """
    Return True only for events that belong in the calendar.

    Comedy, stand-up, one-person shows and spoken-word events are
    supported and will remain in the calendar.
    """

    if is_non_supported_event(event.headliner):
        return False

    normalized_title = normalize_text_for_matching(event.headliner)
    normalized_genre = normalize_text_for_matching(event.genre or "")

    excluded_scope_patterns = [
        r"\btheatre\b",
        r"\bconference\b",
        r"\bmasterclass\b",
    ]

    combined_text = f"{normalized_title} {normalized_genre}"

    return not any(
        re.search(pattern, combined_text)
        for pattern in excluded_scope_patterns
    )


def load_events():
    raw_events = []

    for scraper in discover_scrapers():
        print(f"Loading {scraper.SOURCE_NAME}...")

        scraper_events = scraper.load_events()

        print(f"→ {len(scraper_events)} events loaded")
        print()

        raw_events.extend(scraper_events)

    geography_normalized_events = []

    for event in raw_events:
        normalize_event_geography(event)
        geography_normalized_events.append(event)

    ile_de_france_events = []

    for event in geography_normalized_events:
        if not is_supported_event(event):
            print(
                "Excluded unsupported event: "
                f"{event.headliner}"
            )
            continue

        if not is_ile_de_france_event(event):
            print(
                "Excluded outside Île-de-France: "
                f"{event.headliner} — {event.city}"
            )
            continue

        ile_de_france_events.append(event)

    normalized_events = []

    for event in ile_de_france_events:
        normalize_event_venue(event)
        normalize_event_promoters(event)
        normalized_events.append(event)

    deduplicated_events = deduplicate_events(normalized_events)

    print()
    print(f"Created {len(raw_events)} raw ConcertEvent records")
    print(
        f"Geography-normalized "
        f"{len(geography_normalized_events)} ConcertEvent records"
    )
    print(
        f"Created {len(ile_de_france_events)} "
        "Île-de-France ConcertEvent records before "
        "venue and promoter normalization"
    )
    print(
        f"Normalized {len(normalized_events)} "
        "Île-de-France ConcertEvent records"
    )
    print(
        f"Created {len(deduplicated_events)} "
        "Île-de-France ConcertEvent records after deduplication"
    )

    return deduplicated_events
