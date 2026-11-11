import re
import unicodedata

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "File7"

PROGRAMME_URL = "https://file7.com/fr/programme/programme.html"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def clean_text(value):
    if not value:
        return ""

    value = value.replace("\u200b", "")
    return re.sub(r"\s+", " ", value).strip()


def explicit_detail_artist_sections(html, billing):
    """Confirm artists using separately titled official venue programme sections.

    An opaque '+' bill is not enough: every component must have its own H2/H3
    heading on the independently downloaded official event detail page.
    Genre labels may follow each artist in the same heading.
    """
    values = [
        clean_text(value)
        for value in re.split(r"\s+\+\s+", clean_text(billing))
    ]
    is_open_stage = bool(
        values and re.fullmatch(r"sc[èe]ne\s+ouverte", values[0], re.I)
    )
    if is_open_stage:
        values = values[1:]
    if len(values) < 2 or len(values) > 9 or any(not value for value in values):
        return []

    def key(value):
        text = unicodedata.normalize("NFKD", value or "")
        return "".join(c for c in text if not unicodedata.combining(c)).casefold()

    heading_names = [
        key(clean_text(node.get_text(" ", strip=True)))
        for node in BeautifulSoup(html or "", "html.parser").select("h2,h3")
    ]
    genre = re.compile(
        r"(?:metalcore|metal|rock|pop|jazz|folk|rap|hip.hop|"
        r"hardcore|punk|reggae|electro|indie|soul|blues|"
        r"chanson|alternative|post.hardcore|grunge|psychedelic)"
        r"(?:\s+(?:rock|metal|pop|punk))?$",
        re.I,
    )
    for artist in values:
        normalized = key(artist)
        if not any(
            heading == normalized
            or (
                heading.startswith(normalized + " ")
                and genre.fullmatch(heading[len(normalized):].strip())
            )
            for heading in heading_names
        ):
            return []
    return values


def enrich_official_detail_billing(event, html):
    """Update roles only after independent programme-section corroboration."""
    original = event.raw_title or event.headliner
    artist_parts = explicit_detail_artist_sections(html, event.headliner)
    if not artist_parts:
        return False
    event.headliner = artist_parts[0]
    event.co_headliners = artist_parts[1:]
    event.performers = artist_parts
    event.raw_title = original
    if original and original not in (event.identity_aliases or []):
        event.identity_aliases = [*(event.identity_aliases or []), original]
    if re.match(r"^sc[èe]ne\s+ouverte\s*\+", event.raw_title or "", re.I):
        event.event_title = "Scène Ouverte"
    elif event.series_name:
        event.event_title = event.series_name
    return True


def split_bill(value):
    """A File7 display title alone does not prove '+' performer boundaries."""
    return clean_text(value), None


def title_semantics(value):
    """Separate only File7's explicit recurring programme wrapper."""
    raw = clean_text(value)
    wrapper = re.fullmatch(
        r"(?P<series>Soirées?\s+Fan[- ]Club|Café[- ]Concert)\s*:\s*(?P<artist>.+)",
        raw,
        re.I,
    )
    if not wrapper:
        return raw, None
    return clean_text(wrapper.group("artist")), clean_text(wrapper.group("series"))


def legacy_primary_identity(value):
    """Return the former parser's primary title for state migration only."""
    value = re.sub(
        r"^(?:Soirées Fan Club|Café-Concert)\s*:\s*",
        "",
        clean_text(value),
        flags=re.IGNORECASE,
    )
    return clean_text(re.split(r"\s*\+\s*", value, maxsplit=1)[0])


def parse_card(card):
    link = card.select_one("a[href]")
    artist_element = card.select_one(".artistes")

    if link is None or artist_element is None:
        return None

    detail_url = clean_text(link.get("href"))
    date_match = re.search(
        r"/(\d{2})-(\d{2})-(\d{4})-\d{2}h\d{2}-",
        detail_url,
    )
    raw_title = clean_text(artist_element.get_text(" ", strip=True))
    headliner, series_name = title_semantics(raw_title)
    legacy_identity = legacy_primary_identity(raw_title)

    if not date_match or not headliner:
        return None

    day, month, year = date_match.groups()

    return ConcertEvent(
        date=f"{year}-{month}-{day}",
        headliner=headliner,
        venue="File7",
        city="Magny-le-Hongre",
        department="77",
        co_headliners=None,
        event_title=raw_title if series_name else None,
        raw_title=raw_title if series_name else None,
        series_name=series_name,
        # The old File7 parser treated the first '+' component as the primary
        # identity. Keep that spelling only so event-state can retain the
        # existing public ID/first_seen; it is not performer-role evidence.
        identity_aliases=[legacy_identity] if legacy_identity != headliner else None,
        promoters=None,
        genre=None,
        facebook_event_url=None,
        ticket_url=detail_url,
    )


def event_key(event):
    return (
        event.date,
        event.headliner.casefold(),
        event.venue.casefold(),
    )


def load_events():
    session = requests.Session()

    print("Downloading File7 concert programme...")

    response = session.get(
        PROGRAMME_URL,
        params={"filtre1": 4},
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    events_by_key = {}

    for card in soup.select(".zone_grille .bloc_show"):
        event = parse_card(card)

        if event is None:
            continue

        events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())
    # Only seven File7 published events currently have spaced-plus billings;
    # additional detail requests are bounded and never turn source failure into
    # zero inventory. Official event sections are independent artist evidence.
    for event in events:
        if not re.search(r"\s+\+\s+", event.headliner):
            continue
        try:
            detail = session.get(
                event.ticket_url, headers=HEADERS, timeout=8,
            )
            detail.raise_for_status()
        except requests.RequestException as exc:
            print(f"File7 detail artist evidence unavailable: {event.date}: {exc}")
            continue
        enrich_official_detail_billing(event, detail.text)

    if not events:
        raise RuntimeError(
            "File7 returned no parsable concert listings; "
            "treat as source failure and retain eligible previously published events"
        )

    print(f"Created {len(events)} File7 ConcertEvent records")

    return events
