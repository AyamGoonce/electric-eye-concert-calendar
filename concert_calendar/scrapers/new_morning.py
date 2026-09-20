import json
import re
from datetime import date, datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import (
    discard_repeated_generic_images,
    element_image_url,
)
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "New Morning"

PROGRAMME_URL = "https://www.newmorning.com/"
REQUEST_TIMEOUT = 30
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}
EVENT_PATH_PATTERN = re.compile(r"^(\d{8})-\d+-.+\.html$")

BILL_CANDIDATE_SEPARATOR_RE = re.compile(
    r"\s+(?:\+|&|×|/|x|[-–—])\s+",
    re.IGNORECASE,
)

SHOW_CONTEXT_RE = re.compile(
    r"\b(?:"
    r"tribute|tribute\s+to|hommage|"
    r"centenary|centenaire|centième|"
    r"anniversary|anniversaire|"
    r"celebration|célébration|"
    r"birthday|anniversaire|"
    r"year\s+\d{4}|"
    r"\d{2,3}(?:th|st|nd|rd|e|ème)\s+anniversary"
    r")\b",
    re.IGNORECASE,
)


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _text_key(value):
    return clean_text(value).casefold()


def _stable_unique(values):
    result = []
    seen = set()

    for value in values:
        value = clean_text(value)
        key = _text_key(value)

        if not key or key in seen:
            continue

        seen.add(key)
        result.append(value)

    return result


def _parse_explicit_byline(value):
    """
    Parse New Morning's dedicated performer byline.

    Commas are treated as explicit list structure.  Ampersands are deliberately
    left intact because they can belong to a real artist/project name.
    """
    value = clean_text(value)

    if not re.match(r"^by\s+", value, re.IGNORECASE):
        return []

    value = re.sub(r"^by\s+", "", value, flags=re.IGNORECASE)
    value = re.sub(
        r"\s+with\s+guests?.*$",
        "",
        value,
        flags=re.IGNORECASE,
    ).strip()

    if not value:
        return []

    comma_parts = [
        clean_text(part)
        for part in value.split(",")
        if clean_text(part)
    ]

    return _stable_unique(comma_parts or [value])


def _candidate_bill_parts(title):
    parts = [
        clean_text(part)
        for part in BILL_CANDIDATE_SEPARATOR_RE.split(title or "")
        if clean_text(part)
    ]

    return parts if len(parts) > 1 else []


def _jsonld_event_description(soup):
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text()

        if not clean_text(raw):
            continue

        try:
            payload = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue

        records = payload if isinstance(payload, list) else [payload]

        for record in records:
            if not isinstance(record, dict):
                continue

            if record.get("@type") != "Event":
                continue

            description = clean_text(record.get("description"))

            if description:
                return description

    return ""


def _independent_description_text(soup, raw_title):
    description = _jsonld_event_description(soup)

    if not description:
        paragraphs = [
            clean_text(node.get_text(" ", strip=True))
            for node in soup.select("p.fst-italic")
        ]
        description = " ".join(value for value in paragraphs if value)

    if raw_title:
        description = re.sub(
            re.escape(raw_title),
            " ",
            description,
            flags=re.IGNORECASE,
        )

    return clean_text(description)


def _strong_name_evidence(soup):
    names = []

    for node in soup.select("strong"):
        value = clean_text(node.get_text(" ", strip=True))

        if not value:
            continue

        words = value.split()

        if len(words) > 8:
            continue

        names.append(value)

    return _stable_unique(names)


def _phrase_present(value, text):
    if not value or not text:
        return False

    return bool(
        re.search(
            r"(?<!\w)" + re.escape(value) + r"(?!\w)",
            text,
            flags=re.IGNORECASE,
        )
    )


def _resolve_candidate(candidate, strong_names, description):
    candidate = clean_text(candidate)
    candidate_key = _text_key(candidate)

    exact = [
        name
        for name in strong_names
        if _text_key(name) == candidate_key
    ]

    if len(exact) == 1:
        return exact[0]

    candidate_words = candidate_key.split()

    # A single surname/mononym may expand to a unique full performer name
    # explicitly listed by the venue.
    if len(candidate_words) == 1:
        surname_matches = [
            name
            for name in strong_names
            if _text_key(name).split()
            and _text_key(name).split()[-1] == candidate_key
        ]

        if len(surname_matches) == 1:
            return surname_matches[0]

        return None

    # Multi-word candidates may be corroborated independently in venue prose.
    if _phrase_present(candidate, description):
        return candidate

    return None


def infer_performers_from_detail_html(html, raw_title):
    """
    Resolve possible multi-artist billing using independent venue evidence.

    Separators merely generate candidates.  They never establish artist
    structure by themselves.
    """
    soup = BeautifulSoup(html, "html.parser")
    parts = _candidate_bill_parts(raw_title)

    if not parts:
        return [], False

    strong_names = _strong_name_evidence(soup)
    description = _independent_description_text(soup, raw_title)

    resolved = [
        _resolve_candidate(part, strong_names, description)
        for part in parts
    ]

    if resolved and all(resolved):
        return _stable_unique(resolved), False

    # "Artist - Tribute/Centenary/etc." may establish one performer followed
    # by programme prose, but only when the performer itself is corroborated.
    if (
        resolved
        and resolved[0]
        and not any(resolved[1:])
        and SHOW_CONTEXT_RE.search(" ".join(parts[1:]))
    ):
        return [resolved[0]], True

    return [], False


def _card_context(card):
    node = card.select_one(".p-3 > .mb-2.text-uppercase")

    if not node:
        return None, None

    value = clean_text(node.get_text(" ", strip=True))

    if not value:
        return None, None

    if "festival" in value.casefold():
        return value, None

    return None, value


def _detail_performers(session, detail_url, raw_title):
    try:
        response = session.get(
            detail_url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"New Morning detail fetch failed for {detail_url}: {exc}")
        return [], False

    return infer_performers_from_detail_html(
        response.text,
        raw_title,
    )


def parse_card(link, session=None):
    href = clean_text(link.get("href"))
    match = EVENT_PATH_PATTERN.match(href)

    if not match:
        return None

    try:
        event_date = datetime.strptime(match.group(1), "%Y%m%d").date()
    except ValueError:
        return None

    if event_date < date.today():
        return None

    card = link.find_parent("div", class_="bg-white")
    title_element = card.select_one("h3") if card else None
    raw_title = (
        clean_text(title_element.get_text(" ", strip=True))
        if title_element
        else ""
    )

    if not raw_title:
        return None

    image_url = element_image_url(
        card.select_one("a.d-block img.img-fluid"),
        base_url=PROGRAMME_URL,
    )

    byline_node = (
        card.select_one("p.fst-italic")
        if card
        else None
    )
    byline = (
        clean_text(byline_node.get_text(" ", strip=True))
        if byline_node
        else ""
    )

    performers = _parse_explicit_byline(byline)
    event_title = raw_title if performers else None

    festival_name, series_name = _card_context(card)

    detail_url = urljoin(PROGRAMME_URL, href)

    # Only ambiguous candidate bills require an extra detail-page request.
    if not performers and _candidate_bill_parts(raw_title):
        detail_session = session or requests.Session()
        inferred, title_is_programme = _detail_performers(
            detail_session,
            detail_url,
            raw_title,
        )

        if inferred:
            performers = inferred

            if title_is_programme:
                event_title = raw_title

    return ConcertEvent(
        date=event_date.isoformat(),
        headliner=raw_title,
        venue="New Morning",
        city="Paris",
        department="75",
        openers=None,
        co_headliners=None,
        promoters=None,
        genre=None,
        facebook_event_url=None,
        ticket_url=detail_url,
        festival_name=festival_name,
        event_title=event_title,
        series_name=series_name,
        image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
        performers=performers or None,
    )


def event_key(event):
    return event.date, event.headliner.casefold(), event.venue.casefold()


def load_events():
    session = requests.Session()
    print("Downloading New Morning programme...")
    response = session.get(
        PROGRAMME_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events_by_key = {}
    seen_hrefs = set()

    for link in soup.select("a[href]"):
        href = clean_text(link.get("href"))

        if href in seen_hrefs:
            continue

        if not EVENT_PATH_PATTERN.match(href):
            continue

        seen_hrefs.add(href)
        event = parse_card(link, session=session)

        if event is not None:
            events_by_key.setdefault(event_key(event), event)

    events = list(events_by_key.values())
    print(f"Created {len(events)} New Morning ConcertEvent records")
    return discard_repeated_generic_images(events)
