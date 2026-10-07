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


SOURCE_NAME = "Glazart"
PROGRAMME_URL = (
    "https://www.glazart.com/agenda-concerts/portfolio-category/concert/"
)
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
TITLE_RE = re.compile(
    r"^(\d{2}\.\d{2}\.\d{2})\s*[–—-]\s*Concert\s*:\s*(.+)$",
    re.IGNORECASE,
)


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_detail_artists(html):
    """
    Extract independently listed artist names from a Glazart detail page.

    The detail pages list each billed artist on its own line followed by a
    genre/country parenthetical. Those lines are stronger evidence than the
    compact programme-card title.
    """
    soup = BeautifulSoup(html, "html.parser")
    artists = []

    for line in soup.get_text("\n", strip=True).splitlines():
        value = clean_text(line)

        match = re.match(
            r"^(.+?)\s+\((?:[^()]*)\)$",
            value,
        )

        if not match:
            continue

        artist = clean_text(match.group(1))

        if not artist:
            continue

        if artist.casefold() not in {item.casefold() for item in artists}:
            artists.append(artist)

    return artists


def resolve_detail_bill(detail_url, raw_title, session=None):
    """
    Resolve a '+' programme title only when the Glazart detail page
    independently lists every artist in billing order.
    """
    parts = [
        clean_text(part)
        for part in re.split(r"\s+\+\s+", raw_title)
        if clean_text(part)
    ]

    if len(parts) < 2:
        return None

    client = session or requests.Session()

    try:
        response = client.get(
            detail_url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    detailed = parse_detail_artists(response.text)

    if len(detailed) < len(parts):
        return None

    resolved = detailed[:len(parts)]

    if len(resolved) != len(parts):
        return None

    return resolved


def parse_card(card, *, today=None, session=None):
    link = None
    match = None
    for candidate in card.select("a.item-link[href]"):
        candidate_match = TITLE_RE.match(
            clean_text(candidate.get_text(" ", strip=True))
        )
        if candidate_match:
            link = candidate
            match = candidate_match
            break
    if not match:
        return None
    try:
        event_date = datetime.strptime(match.group(1), "%d.%m.%y").date()
    except ValueError:
        return None
    if event_date < (today or date.today()):
        return None
    raw_title = clean_text(match.group(2))
    if not raw_title:
        return None
    detail_url = urljoin(PROGRAMME_URL, link.get("href"))

    resolved_bill = resolve_detail_bill(
        detail_url,
        raw_title,
        session=session,
    )

    if resolved_bill:
        headliner = resolved_bill[0]
        co_headliners = resolved_bill[1:] or None
        performers = resolved_bill
        event_title = " + ".join(resolved_bill)
    else:
        headliner = raw_title
        co_headliners = None
        performers = None
        event_title = None
    image_url = element_image_url(card.select_one("img"), base_url=PROGRAMME_URL)
    if image_url and "blank-admat" in image_url.casefold():
        image_url = None
    return ConcertEvent(
        date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME,
        city="Paris", department="75", ticket_url=detail_url,
        ticket_status="tickets", image_url=image_url,
        image_source=SOURCE_NAME if image_url else None,
        co_headliners=co_headliners,
        performers=performers,
        event_title=event_title,
    )


def load_events(today=None):
    today = today or date.today()
    session = requests.Session()
    print(f"Downloading Glazart concert programme: {PROGRAMME_URL}")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events = {}
    for card in soup.select(".portfolio-item[data-terms~='concert']"):
        event = parse_card(card, today=today, session=session)
        if event is not None:
            events.setdefault((event.date, event.headliner.casefold()), event)
    result = discard_repeated_generic_images(list(events.values()))
    print(f"Created {len(result)} Glazart ConcertEvent records")
    return result
