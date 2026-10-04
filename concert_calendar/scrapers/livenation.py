from math import ceil
from urllib.parse import urljoin

import requests

from concert_calendar.event_images import official_image_url, discard_repeated_generic_images
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Live Nation"

API_URL = "https://www.livenation.fr/__api/search/events"
BASE_URL = "https://www.livenation.fr"
REQUEST_TIMEOUT = 30
PAGE_SIZE = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.livenation.fr/event/allevents",
    "X-Culture": "fr-FR",
    "X-Site": "3",
}

_DIAGNOSTICS = []


def get_diagnostics():
    return list(_DIAGNOSTICS)


def _billing_key(value):
    return " ".join(
        "".join(
            character.lower() if character.isalnum() else " "
            for character in (value or "")
        ).split()
    )


def get_billing(document):
    """
    Preserve Live Nation's explicit headline/support roles.

    Some records expose a synthetic primary headline representing a combined
    bill, while also exposing the real headline artists as separate `headline`
    lineup entries. Treat that primary value as a wrapper only when at least
    two separate non-primary headline names are all present inside it.
    """
    lineup = document.get("lineup") or []

    headline_entries = [
        artist for artist in lineup
        if artist.get("type") == "headline"
        and (artist.get("name") or "").strip()
    ]
    support_entries = [
        artist for artist in lineup
        if artist.get("type") != "headline"
        and (artist.get("name") or "").strip()
    ]

    primary = next(
        (
            artist for artist in headline_entries
            if artist.get("isPrimary")
        ),
        None,
    )

    non_primary = [
        artist for artist in headline_entries
        if artist is not primary
    ]

    headline_names = []

    if primary is not None:
        primary_name = (primary.get("name") or "").strip()
        primary_key = _billing_key(primary_name)

        non_primary_names = [
            (artist.get("name") or "").strip()
            for artist in non_primary
        ]

        primary_is_wrapper = (
            len(non_primary_names) >= 2
            and all(
                _billing_key(name)
                and _billing_key(name) in primary_key
                for name in non_primary_names
            )
        )

        if primary_is_wrapper:
            headline_names = non_primary_names
        else:
            headline_names = [
                primary_name,
                *non_primary_names,
            ]

    elif headline_entries:
        headline_names = [
            (artist.get("name") or "").strip()
            for artist in headline_entries
        ]

    if not headline_names:
        fallback = (document.get("name") or "").strip()
        headline_names = [fallback] if fallback else []

    headline_names = list(dict.fromkeys(headline_names))

    support_names = list(dict.fromkeys(
        (artist.get("name") or "").strip()
        for artist in support_entries
        if (artist.get("name") or "").strip()
        not in headline_names
    ))

    headliner = headline_names[0] if headline_names else ""
    co_headliners = headline_names[1:] or None
    openers = support_names[:5] or None

    return headliner, co_headliners, openers


def get_genre(document):
    genres = document.get("genres") or []

    genre_names = [
        (genre.get("name") or "").strip()
        for genre in genres
        if (genre.get("name") or "").strip()
    ]

    return ", ".join(genre_names) or None


def get_ticket_url(document):
    tickets = document.get("tickets") or []

    for ticket in tickets:
        if not ticket.get("isVisible", True):
            continue

        url = (
            ticket.get("overrideUrl")
            or ticket.get("ticketUrl")
            or ""
        ).strip()

        if url:
            return urljoin(
                "https://www.livenation.fr",
                url,
            )

    direct_purchase = document.get("directPurchaseButton") or {}
    direct_url = (direct_purchase.get("url") or "").strip()

    if direct_url:
        return urljoin(
            "https://www.livenation.fr",
            direct_url,
        )

    return None


def get_event_url(document):
    localizations = document.get("localizations") or []

    for localization in localizations:
        if localization.get("cultureName") == "fr-FR":
            url = (localization.get("url") or "").strip()

            if url:
                return urljoin(BASE_URL, url)

    url = (document.get("url") or "").strip()

    if not url:
        return None

    return urljoin(BASE_URL, url)


def document_to_event(document):
    venue_data = document.get("venue") or {}

    headliner, co_headliners, openers = get_billing(document)

    if not headliner:
        return None

    date = (
        document.get("eventDate")
        or document.get("eventDateUtc")
        or ""
    ).strip()

    if "T" in date:
        date = date.split("T", 1)[0]

    venue = (venue_data.get("name") or "").strip()
    city = (venue_data.get("city") or "").strip()

    if not date or not venue or not city:
        return None

    promoter = (document.get("promoter") or SOURCE_NAME).strip()

    ticket_url = get_ticket_url(document)
    event_url = get_event_url(document)
    image_url = official_image_url(document.get("image"))

    return ConcertEvent(
        date=date,
        headliner=headliner,
        openers=openers,
        co_headliners=co_headliners,
        venue=venue,
        city=city,
        department="",
        promoters=[promoter] if promoter else [SOURCE_NAME],
        genre=get_genre(document),
        facebook_event_url=None,
        ticket_url=ticket_url or event_url,
        image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
    )


def fetch_page(page_number):
    response = requests.get(
        API_URL,
        params={
            "culture": "fr-FR",
            "Page": page_number,
            "PageSize": PAGE_SIZE,
        },
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    return response.json()


def fetch_inventory_snapshot():
    """Fetch one complete page-number inventory from a single starting total."""

    first_page = fetch_page(1)

    total = first_page.get("total", 0)
    documents = list(first_page.get("documents") or [])

    total_pages = max(1, ceil(total / PAGE_SIZE))

    for page_number in range(2, total_pages + 1):
        page_data = fetch_page(page_number)
        documents.extend(page_data.get("documents") or [])

    return documents


def _stable_document_id(document):
    value = document.get("id")
    if value is None or value == "":
        return None
    return str(value)


def _coherent_snapshot(documents):
    """Deduplicate one inventory by Live Nation's stable document identifier."""

    documents_by_id = {}
    unidentified = []
    for document in documents:
        document_id = _stable_document_id(document)
        if document_id is None:
            unidentified.append(document)
            continue
        documents_by_id.setdefault(document_id, document)

    return {
        "documents": [*documents_by_id.values(), *unidentified],
        "ids": frozenset(documents_by_id),
        "distinct_count": len(documents_by_id),
        "unidentified_count": len(unidentified),
    }


def _select_inventory_snapshot(snapshots):
    """Choose the fullest coherent snapshot, then consensus, then earliest."""

    if len(snapshots) == 2 and snapshots[0]["ids"] == snapshots[1]["ids"]:
        # The second matching snapshot is the freshest confirmation of the
        # stable inventory without requiring a third network pass.
        return 1

    def selection_key(index):
        snapshot = snapshots[index]
        agreement = sum(
            len(snapshot["ids"] & other["ids"])
            for other_index, other in enumerate(snapshots)
            if other_index != index
        )
        return snapshot["distinct_count"], agreement, -index

    return max(range(len(snapshots)), key=selection_key)


def load_events():
    global _DIAGNOSTICS
    _DIAGNOSTICS = []

    snapshots = [
        _coherent_snapshot(fetch_inventory_snapshot()),
        _coherent_snapshot(fetch_inventory_snapshot()),
    ]
    disagreement = snapshots[0]["ids"] != snapshots[1]["ids"]
    if disagreement:
        snapshots.append(_coherent_snapshot(fetch_inventory_snapshot()))

    selected_index = _select_inventory_snapshot(snapshots)
    selected = snapshots[selected_index]
    distinct_counts = [snapshot["distinct_count"] for snapshot in snapshots]
    unidentified_counts = [
        snapshot["unidentified_count"] for snapshot in snapshots
    ]
    _DIAGNOSTICS.append({
        "kind": "inventory_stability",
        "snapshot_disagreement": disagreement,
        "snapshots_fetched": len(snapshots),
        "snapshot_distinct_counts": distinct_counts,
        "snapshot_unidentified_counts": unidentified_counts,
        "selected_snapshot": selected_index + 1,
        "selected_distinct_count": selected["distinct_count"],
    })
    print(
        "Live Nation inventory stability | "
        f"distinct_counts={distinct_counts} | "
        f"disagreement={str(disagreement).lower()} | "
        f"selected_snapshot={selected_index + 1}",
        flush=True,
    )

    documents = selected["documents"]
    events = []

    for document in documents:
        event = document_to_event(document)

        if event is not None:
            events.append(event)

    return discard_repeated_generic_images(events)
