import re

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Garmonbozia"

EVENTS_URL = (
    "https://web.digitick.com/ext/billetterie5/"
    "index.php?site=garmonbozia"
)
REQUEST_TIMEOUT = 30
MAX_DIAGNOSTICS = 200
_DIAGNOSTICS = []

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def parse_lineup(value):
    """A title alone does not establish individual artists or support roles."""
    return clean_text(value), None


def parse_structured_billing(value, *, structured_artists=None, info_text=""):
    """Use a '+' bill only when Garmonbozia supplies explicit current-role evidence."""

    title = clean_text(value)
    parts = [
        clean_text(part)
        for part in re.split(r"\s+\+\s+", title)
        if clean_text(part)
    ]
    if len(parts) < 2:
        return None

    structured_keys = {
        clean_text(artist).casefold()
        for artist in (structured_artists or [])
        if clean_text(artist)
    }
    part_keys = {part.casefold() for part in parts}

    # Hidden metadata is corroboration, not a complete artist list:
    # Garmonbozia occasionally omits a billed artist from this field.
    if (
        len(structured_keys.intersection(part_keys)) < 2
        or parts[0].casefold() not in structured_keys
    ):
        return None

    info = clean_text(info_text).casefold()
    openers = []

    for part in parts[1:]:
        artist = re.escape(part.casefold())
        role_pattern = (
            r"(?:l['’]ouverture de soirée\s+)?"
            r"sera assur(?:ée|e) par\s+"
            + artist
            + r"(?=$|[\s(,.;:!?\-])"
        )
        if re.search(role_pattern, info, re.IGNORECASE):
            openers.append(part)

    # Do not reinterpret the bill unless a billed artist has an explicit
    # current-event opening role in Garmonbozia's own description.
    if not openers:
        return None

    performers = [
        part
        for part in parts
        if part not in openers
    ]
    if not performers:
        return None

    return performers[0], openers, performers


def parse_city(value):
    city = clean_text(value).lstrip("- ").strip()

    if re.fullmatch(
        r"paris(?:\s+\d{1,2})?",
        city,
        flags=re.IGNORECASE,
    ):
        return "Paris"

    return city


def parse_card(card):
    title_element = card.select_one(
        "dd .evenementNom"
    )
    date_element = card.select_one(
        "time[itemprop='startDate']"
    )
    venue_element = card.select_one(
        ".evenementSalleNom"
    )
    city_elements = card.select(
        ".evenementSalleVille"
    )
    genre_element = card.select_one(
        ".evenementSousGenre"
    )
    ticket_element = card.select_one(
        "a.evenementReserver[href]"
    )
    artists_element = card.select_one(
        ".evenementInfoArtists"
    )
    info_element = card.select_one(
        ".evenementInfo"
    )

    title = (
        clean_text(
            title_element.get_text(" ", strip=True)
        )
        if title_element
        else ""
    )
    headliner, openers = parse_lineup(title)
    performers = None

    structured_artists = (
        [
            clean_text(artist)
            for artist in artists_element.get_text(",", strip=True).split(",")
            if clean_text(artist)
        ]
        if artists_element
        else []
    )
    info_text = (
        clean_text(info_element.get_text(" ", strip=True))
        if info_element
        else ""
    )

    structured_billing = parse_structured_billing(
        title,
        structured_artists=structured_artists,
        info_text=info_text,
    )
    if structured_billing:
        headliner, openers, performers = structured_billing

    event_date = (
        clean_text(date_element.get("datetime"))[:10]
        if date_element
        else ""
    )
    venue = (
        clean_text(
            venue_element.get_text(" ", strip=True)
        )
        if venue_element
        else ""
    )
    city = (
        parse_city(
            city_elements[-1].get_text(" ", strip=True)
        )
        if city_elements
        else ""
    )
    genre = (
        clean_text(
            genre_element.get_text(" ", strip=True)
        )
        if genre_element
        else None
    )
    ticket_url = (
        clean_text(ticket_element.get("href"))
        if ticket_element
        else None
    )

    if re.search(r"\s[+&/]\s|\b(?:with|feat\.?|featuring)\b", title, re.I) or openers:
        _DIAGNOSTICS.append({
            "source_event_id": clean_text(card.get("data-id") or card.get("id")) or None,
            "listing_url": EVENTS_URL,
            "detail_url": ticket_url or None,
            "raw_event_title": title,
            "raw_date": clean_text(date_element.get("datetime")) if date_element else None,
            "final_date": event_date,
            "raw_venue": clean_text(venue_element.get_text(" ", strip=True)) if venue_element else None,
            "final_venue": venue,
            "final_city": city,
            "parser_billing_path": (
                "explicit_role_evidence"
                if performers
                else "plus_title_split"
                if "+" in title
                else "plain_compound_title"
            ),
            "parsed_headliner": headliner,
            "parsed_co_headliners": performers[1:] if performers else None,
            "parsed_openers": openers,
        })
        del _DIAGNOSTICS[MAX_DIAGNOSTICS:]

    if not event_date:
        return None

    if not headliner:
        return None

    if not venue:
        return None

    if not city:
        return None

    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        performers=performers,
        venue=venue,
        city=city,
        department="",
        openers=openers,
        promoters=["Garmonbozia"],
        genre=genre or None,
        facebook_event_url=None,
        ticket_url=ticket_url or None,
    )


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
        event.city.casefold(),
    )


def load_events():
    _DIAGNOSTICS.clear()
    session = requests.Session()

    print(f"Downloading {EVENTS_URL}...")

    response = session.get(
        EVENTS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )
    cards = soup.select(
        ".evenementListe > dl"
    )

    events_by_key = {}

    for card in cards:
        event = parse_card(card)

        if event is not None:
            events_by_key[event_key(event)] = event

    events = list(events_by_key.values())

    print(
        f"Created {len(events)} "
        "Garmonbozia ConcertEvent records"
    )

    return events


def get_diagnostics():
    return list(_DIAGNOSTICS)
