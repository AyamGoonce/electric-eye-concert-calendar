import re
import time
import unicodedata
from dataclasses import dataclass

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.deduplication import normalize_headliner
from concert_calendar.geography import (
    is_ile_de_france_event,
    normalize_event_geography,
)
from concert_calendar.genres import enrich_event_genres
from concert_calendar.promoters import normalize_event_promoters
from concert_calendar.scraper_loader import discover_scrapers_with_issues
from concert_calendar.venues import normalize_event_venue
from concert_calendar.venues import normalize_venue_key


IMAGE_ENRICHMENT_MODULES = ()


def enrich_official_venue_images(events):
    """Fill blank images from exact official venue-listing identities only."""

    from importlib import import_module

    if not events:
        return events

    candidates = {}
    for module_name in IMAGE_ENRICHMENT_MODULES:
        module = import_module(module_name)
        for candidate in module.load_events():
            key = (
                candidate.date[:10],
                normalize_venue_key(candidate.venue),
                normalize_headliner(candidate.headliner),
            )
            if candidate.image_url:
                candidates.setdefault(key, candidate)

    enriched = 0
    for event in events:
        if event.image_url:
            continue
        key = (
            event.date[:10],
            normalize_venue_key(event.venue),
            normalize_headliner(event.headliner),
        )
        candidate = candidates.get(key)
        if candidate:
            event.image_url = candidate.image_url
            event.image_source = candidate.image_source
            enriched += 1
    print(f"Added {enriched} exact official venue-listing images")
    return events


@dataclass(frozen=True)
class PipelineReport:
    configured_sources: list[str]
    source_health: list[dict]
    source_counts: dict[str, int]
    source_failures: dict[str, str]
    registration_failures: dict[str, str]
    raw_count: int
    geography_normalized_count: int
    idf_count: int
    normalized_count: int
    final_count: int
    package_product_count: int
    festival_days_aggregated: int
    festival_artist_rows_collapsed: int
    opener_enriched_records: int
    unresolved_deduplication_candidates: list[dict]
    genre_report: dict


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
        or re.search(r"\bparty\b.*\blive on tour\b", normalized_title)
        or re.match(
            r"^bloc party(?:\s*\+|$)",
            normalized_title,
        )
    )

    excluded_patterns = [
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
    ) or is_ticket_product_title(title)


def is_ticket_product_title(title):
    """Identify explicit ticket products without matching artist-name tokens."""

    normalized = normalize_text_for_matching(title)
    product_patterns = (
        r"^(?:package|vip)\s+",
        r"\bpass\s+(?:1|2|3|4)\s+jours?\b",
        r"\bpass\s+(?:weekend|week-end|samedi|dimanche)\b",
        r"\b(?:weekend|week-end|day|multi-day|\d+-day)\s+pass\b",
        r"\b(?:vip|premium|hospitality)\s+"
        r"(?:package|upgrade|experience|ticket|pass)\b",
        r"\bmeet(?:-and-| and )greet(?:\s+package)?\b",
        r"\bearly[- ]entry(?:\s+(?:product|upgrade|pass))?\b",
        r"\bparking\s+(?:product|ticket|pass|add-on)\b",
        r"\b(?:ticket\s+)?(?:add-on|upgrade|resale|membership|adhesion)\s+product\b",
        r"\bupgrade\s*$",
        r"\bgeneric\s+bundle\b",
    )

    return any(re.search(pattern, normalized) for pattern in product_patterns)


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


def load_events_with_report(
    *,
    scraper_attempts: int = 3,
    retry_delay_seconds: float = 2.0,
):
    raw_events = []
    source_health = []
    source_counts = {}
    source_failures = {}
    scrapers, registration_failures = discover_scrapers_with_issues()

    for scraper in scrapers:
        print(f"Loading {scraper.SOURCE_NAME}...")

        scraper_events = None
        last_error = None

        for attempt in range(1, scraper_attempts + 1):
            try:
                scraper_events = scraper.load_events()
                if scraper_events or attempt == scraper_attempts:
                    break
                print(
                    f"Attempt {attempt}/{scraper_attempts} returned zero events "
                    f"for {scraper.SOURCE_NAME}"
                )
                if retry_delay_seconds:
                    time.sleep(retry_delay_seconds * attempt)
            except Exception as error:  # Individual sources must not hide the run report.
                last_error = error
                print(
                    f"Attempt {attempt}/{scraper_attempts} failed for "
                    f"{scraper.SOURCE_NAME}: {error}"
                )
                if attempt < scraper_attempts and retry_delay_seconds:
                    time.sleep(retry_delay_seconds * attempt)

        if not scraper_events and last_error is not None:
            source_failures[scraper.SOURCE_NAME] = (
                f"{type(last_error).__name__}: {last_error}"
            )
        if scraper_events is None:
            scraper_events = []

        for event in scraper_events:
            event.source_names = [scraper.SOURCE_NAME]
            if event.genre:
                event.genre_source = scraper.SOURCE_NAME
                event.genre_evidence = [{
                    "raw": event.genre,
                    "source": scraper.SOURCE_NAME,
                }]

        print(f"→ {len(scraper_events)} events loaded")
        print()

        source_counts[scraper.SOURCE_NAME] = len(scraper_events)
        source_health.append({
            "source_name": scraper.SOURCE_NAME,
            "module": scraper.__name__,
            "status": (
                "failed" if scraper.SOURCE_NAME in source_failures
                else "ok" if scraper_events else "empty"
            ),
            "future_event_count": len(scraper_events),
            "error": source_failures.get(scraper.SOURCE_NAME),
            "allow_empty": bool(getattr(scraper, "ALLOW_EMPTY", False)),
        })
        raw_events.extend(scraper_events)

    geography_normalized_events = []

    for event in raw_events:
        normalize_event_geography(event)
        geography_normalized_events.append(event)

    ile_de_france_events = []
    package_product_count = 0

    for event in geography_normalized_events:
        if is_ticket_product_title(event.headliner):
            package_product_count += 1

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

    enrich_official_venue_images(normalized_events)

    deduplication_diagnostics = {}
    deduplicated_events = deduplicate_events(
        normalized_events,
        diagnostics=deduplication_diagnostics,
    )
    genre_report = enrich_event_genres(deduplicated_events)

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

    report = PipelineReport(
        configured_sources=[scraper.SOURCE_NAME for scraper in scrapers],
        source_health=source_health,
        source_counts=source_counts,
        source_failures=source_failures,
        registration_failures=registration_failures,
        raw_count=len(raw_events),
        geography_normalized_count=len(geography_normalized_events),
        idf_count=len(ile_de_france_events),
        normalized_count=len(normalized_events),
        final_count=len(deduplicated_events),
        package_product_count=package_product_count,
        festival_days_aggregated=deduplication_diagnostics.get(
            "festival_days_aggregated", 0
        ),
        festival_artist_rows_collapsed=deduplication_diagnostics.get(
            "festival_artist_rows_collapsed", 0
        ),
        opener_enriched_records=deduplication_diagnostics.get(
            "opener_enriched_records", 0
        ),
        unresolved_deduplication_candidates=deduplication_diagnostics.get(
            "unresolved_candidates", []
        ),
        genre_report=genre_report,
    )

    return deduplicated_events, report


def load_events():
    events, _ = load_events_with_report()
    return events
