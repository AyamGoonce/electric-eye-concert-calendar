from datetime import date, datetime
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Le Grand Rex"
PROGRAMME_URL = "https://www.legrandrex.com/evenement/"
REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}


def _clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _start_time(value):
    match = re.search(r"\b(?:à|a)\s+(\d{1,2})(?::|h)(\d{2})?\b", value, re.I)
    if not match:
        return None
    return f"{int(match.group(1)):02d}:{match.group(2) or '00'}"


def _is_cine_concert(card):
    """
    Exclude cinema-first events explicitly identified by the venue as
    ciné-concerts. Ordinary concerts and orchestral concerts are retained.
    """
    info = card.select_one(".infos")
    if not info:
        return False

    text = _clean(info.get_text(" ", strip=True))

    return bool(re.search(
        r"\bcin[ée][\s\-‐-‒–—]*concerts?\b|#cineconcert\b",
        text,
        re.IGNORECASE,
    ))


def _explicit_concert_title(card, title):
    """Use a fuller title only when the card copy explicitly quotes it."""
    info = card.select_one(".infos")
    if not info:
        return title
    text = info.get_text(" ", strip=True)
    for candidate in re.findall(r'["“«]([^"”»]+?\ben concert)\s*["”»]', text, re.I):
        candidate = _clean(candidate)
        if candidate.casefold().startswith(title.casefold()) and len(candidate) > len(title):
            return candidate
    return title


def _parse_modern_cards(soup, cutoff):
    """Parse the venue's redesigned category-labelled concert cards.

    Only explicitly classified Concert cards with one exact date qualify.
    Date ranges and generic Spectacle/film categories remain excluded.
    """
    events = []
    for card in soup.select("article.carte"):
        category = card.select_one(".carte__categorie")
        if not category or _clean(category.get_text(" ", strip=True)).casefold() != "concert":
            continue
        title_node = card.select_one(".carte__titre")
        date_node = card.select_one(".carte__date")
        link = card.select_one("a.carte__lien[href]")
        if not (title_node and date_node and link):
            continue
        title = _clean(title_node.get_text(" ", strip=True))
        raw_date = _clean(date_node.get_text(" ", strip=True))
        if not title or not re.fullmatch(r"\d{2}/\d{2}/\d{4}", raw_date):
            continue
        try:
            event_date = datetime.strptime(raw_date, "%d/%m/%Y").date()
        except ValueError:
            continue
        if event_date < cutoff:
            continue
        href = _clean(link.get("href"))
        if not href:
            continue
        image = element_image_url(
            card.select_one(".carte__affiche img"), base_url=PROGRAMME_URL,
        )
        events.append(ConcertEvent(
            date=event_date.isoformat(), headliner=title, venue=SOURCE_NAME,
            city="Paris", department="75",
            ticket_url=urljoin(PROGRAMME_URL, href),
            ticket_status="tickets", image_url=image,
            image_source=SOURCE_NAME if image else None,
        ))
    return events


def parse_events(soup, *, today=None):
    cutoff = today or date.today()
    events = []
    # The venue replaced its legacy .row-event cards with article.carte.
    # Prefer the new explicit concert category when present; keep the old
    # implementation for archived HTML and future transition periods.
    if soup.select("article.carte"):
        return _parse_modern_cards(soup, cutoff)
    for card in soup.select(".row-event"):
        classes = set(card.get("class", []))
        # The venue's broad visible category combines concerts and shows.  The
        # machine-readable `concerts` class is the narrow, authoritative signal.
        if "concerts" not in classes or "annule" in classes:
            continue
        title_link = card.select_one("h3.title-movie-tout a[href]")
        if not title_link:
            continue

        if _is_cine_concert(card):
            continue

        headliner = _clean(title_link.get_text(" ", strip=True))
        if not headliner:
            continue
        headliner = _explicit_concert_title(card, headliner)
        event_dates = []
        for value in classes:
            match = re.fullmatch(r"date-(\d{4}-\d{2}-\d{2})", value)
            if not match:
                continue
            try:
                parsed = date.fromisoformat(match.group(1))
            except ValueError:
                continue
            if parsed >= cutoff:
                event_dates.append(parsed)
        date_node = card.select_one(".date-tout")
        event_time = _start_time(_clean(date_node.get_text(" ", strip=True) if date_node else ""))
        booking = card.select_one(".btn-book[data-url]")
        ticket_url = _clean(booking.get("data-url", "") if booking else "")
        # A generic search result can be shared by distinct performances and is
        # therefore weaker than the card's event-specific official URL.
        if not ticket_url or re.search(r"/search(?:\?|$)", ticket_url):
            ticket_url = urljoin(PROGRAMME_URL, title_link["href"])
        image = element_image_url(card.select_one(".cm3 img"), base_url=PROGRAMME_URL)
        sold_out = "complet" in classes
        for event_date in sorted(set(event_dates)):
            events.append(ConcertEvent(
                date=event_date.isoformat(), headliner=headliner, venue=SOURCE_NAME,
                city="Paris", department="75", ticket_url=ticket_url,
                ticket_status="sold_out" if sold_out else "tickets", sold_out=sold_out,
                start_time=event_time, image_url=image,
                image_source=SOURCE_NAME if image else None,
            ))
    return events


def load_events():
    session = requests.Session()
    print(f"Downloading Le Grand Rex programme: {PROGRAMME_URL}")
    # Both paths are published by the venue, but their responses may differ.
    # Try the canonical path before the legacy trailing-slash path; an empty
    # response is not a valid inventory and must never erase retained records.
    for url in (PROGRAMME_URL.rstrip("/"), PROGRAMME_URL):
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        unique = {}
        for event in parse_events(BeautifulSoup(response.text, "html.parser")):
            unique.setdefault((event.date, event.start_time, event.headliner.casefold()), event)
        if unique:
            result = discard_repeated_generic_images(list(unique.values()))
            print(f"Created {len(result)} Le Grand Rex ConcertEvent records")
            return result
        print(f"No Le Grand Rex concerts found at {url}; trying alternate path")
    print("Created 0 Le Grand Rex ConcertEvent records")
    return []
