import re
import unicodedata
import xml.etree.ElementTree as ET
from datetime import date
from html import unescape
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Los Production"
AGENDA_URL = "https://www.losproduction.com/agenda/"
SITEMAP_INDEX_URL = "https://www.losproduction.com/wp-sitemap.xml"
SHOWS_INDEX_URL = "https://www.losproduction.com/spectacles/"
REQUEST_TIMEOUT = 30
SUBJECT_SAFETY_CEILING = 500

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

MONTHS = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
    "decembre": 12,
}

_DIAGNOSTICS = []


class LosProductionScraperError(RuntimeError):
    pass


def clean_text(value):
    return re.sub(r"\s+", " ", unescape(value or "")).strip()


def match_key(value):
    normalized = unicodedata.normalize("NFKD", clean_text(value))
    normalized = "".join(
        character for character in normalized
        if not unicodedata.combining(character)
    ).casefold()
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def get_diagnostics():
    return list(_DIAGNOSTICS)


def parse_french_date(value):
    match = re.search(
        r"\b(\d{1,2})\s+([A-Za-zÀ-ÿ]+)\s+(\d{4})\b",
        clean_text(value).casefold(),
    )
    if not match:
        return ""
    month = MONTHS.get(match.group(2))
    if month is None:
        return ""
    try:
        return date(int(match.group(3)), month, int(match.group(1))).isoformat()
    except ValueError:
        return ""


def split_venue_city(value):
    text = clean_text(value)
    start_time = None
    time_match = re.search(r"\s+-\s+(\d{1,2})h(?:(\d{2}))?\s*$", text, re.I)
    if time_match:
        start_time = f"{int(time_match.group(1)):02d}:{time_match.group(2) or '00'}"
        text = text[:time_match.start()].strip()
    if "," in text:
        venue, city = text.rsplit(",", 1)
    elif " - " in text:
        venue, city = text.rsplit(" - ", 1)
    else:
        venue, city = text, ""
    return clean_text(venue), clean_text(city), start_time


def parse_agenda_card(card):
    title_node = card.select_one(".titre")
    date_node = card.select_one(".date")
    venue_node = card.select_one(".lieu")
    link = card.select_one("a.wrap[href]")
    title = clean_text(title_node.get_text(" ", strip=True) if title_node else "")
    event_date = parse_french_date(
        date_node.get_text(" ", strip=True) if date_node else ""
    )
    raw_location = clean_text(
        venue_node.get_text(" ", strip=True) if venue_node else ""
    )
    venue, city, start_time = split_venue_city(raw_location)
    ticket_url = clean_text(link.get("href")) if link else ""
    image = card.select_one("img")
    image_url = clean_text(image.get("src")) if image else ""
    if not all((title, event_date, venue)):
        return None
    return {
        "date": event_date,
        "title": title,
        "venue": venue,
        "city": city,
        "start_time": start_time,
        "ticket_url": ticket_url or None,
        "image_url": image_url or None,
        "raw_location": raw_location,
    }


def card_key(card):
    return (
        card["date"], match_key(card["title"]), match_key(card["raw_location"]),
        card["ticket_url"] or "",
    )


def parse_agenda(html):
    soup = BeautifulSoup(html, "html.parser")
    cards = []
    for node in soup.select(".bloc_extrait.evenement"):
        card = parse_agenda_card(node)
        if card:
            cards.append(card)
    return cards


def canonical_subjects(html, path):
    soup = BeautifulSoup(html, "html.parser")
    subjects = {}
    for link in soup.select(f'a[href*="/{path}/"]'):
        href = clean_text(link.get("href"))
        title = clean_text(link.get("title")) or clean_text(link.get_text(" ", strip=True))
        if title and re.match(rf"https?://[^/]+/{path}/[^/]+/?$", href):
            subjects[match_key(title)] = {"title": title, "url": href}
    return subjects


def sitemap_locations(xml):
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as error:
        raise LosProductionScraperError("invalid Los Production sitemap XML") from error
    return [
        clean_text(node.text)
        for node in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if clean_text(node.text)
    ]


def canonical_artist_urls(urls):
    subjects = {}
    for url in urls:
        match = re.match(r"https?://[^/]+/artistes/([^/]+)/?$", url)
        if match:
            subjects[match_key(match.group(1))] = url
    return subjects


def artist_filter_subjects(agenda_html, canonical_artists):
    soup = BeautifulSoup(agenda_html, "html.parser")
    subjects = []
    for field in soup.select('input[name="show[]"][value]'):
        label = field.find_parent("label")
        title = clean_text(label.get_text(" ", strip=True) if label else "")
        post_id = clean_text(field.get("value"))
        canonical_url = canonical_artists.get(match_key(title))
        if post_id.isdigit() and canonical_url:
            subjects.append({
                "id": post_id,
                "title": title,
                "url": canonical_url,
            })
    unique = {subject["id"]: subject for subject in subjects}
    if len(unique) > SUBJECT_SAFETY_CEILING:
        raise LosProductionScraperError("artist relationship count exceeded safety ceiling")
    return list(unique.values())


def filtered_agenda_url(post_id):
    return f"{AGENDA_URL}?{urlencode([('show[]', post_id)])}"


def card_to_event(card):
    return ConcertEvent(
        date=card["date"],
        headliner=card["title"],
        venue=card["venue"],
        city=card["city"],
        department="",
        promoters=None,
        ticket_url=card["ticket_url"],
        ticket_status="tickets" if card["ticket_url"] else None,
        start_time=card["start_time"],
        event_type="concert",
        performers=[card["title"]],
        image_url=card["image_url"],
        image_source=SOURCE_NAME if card["image_url"] else None,
        raw_title=card["title"],
    )


def load_events(today=None):
    today = today or date.today()
    _DIAGNOSTICS.clear()
    session = requests.Session()

    agenda_response = session.get(AGENDA_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    agenda_response.raise_for_status()
    sitemap_response = session.get(
        SITEMAP_INDEX_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT,
    )
    sitemap_response.raise_for_status()
    shows_response = session.get(
        SHOWS_INDEX_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT,
    )
    shows_response.raise_for_status()

    agenda_cards = parse_agenda(agenda_response.text)
    artist_sitemaps = [
        url for url in sitemap_locations(sitemap_response.text)
        if "wp-sitemap-posts-artistes-" in url
    ]
    if not artist_sitemaps or len(artist_sitemaps) > SUBJECT_SAFETY_CEILING:
        raise LosProductionScraperError("artist sitemap inventory is unavailable or unbounded")
    artist_urls = []
    for sitemap_url in artist_sitemaps:
        response = session.get(sitemap_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        artist_urls.extend(sitemap_locations(response.text))
    canonical_artists = canonical_artist_urls(artist_urls)
    canonical_shows = canonical_subjects(shows_response.text, "spectacles")
    subjects = artist_filter_subjects(agenda_response.text, canonical_artists)
    if agenda_cards and not subjects:
        raise LosProductionScraperError(
            "agenda contained rows but exposed no validated artist relationships"
        )

    eligible = {}
    for subject in subjects:
        response = session.get(
            filtered_agenda_url(subject["id"]),
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        for card in parse_agenda(response.text):
            eligible[card_key(card)] = (card, subject)

    agenda_keys = {card_key(card): card for card in agenda_cards}
    for key, card in agenda_keys.items():
        if key in eligible:
            continue
        classification = canonical_shows.get(match_key(card["title"]))
        if classification:
            _DIAGNOSTICS.append({
                "reason": "excluded_canonical_spectacle",
                "title": card["title"],
                "date": card["date"],
                "classification_url": classification["url"],
            })
        else:
            _DIAGNOSTICS.append({
                "reason": "unclassified_agenda_row",
                "title": card["title"],
                "date": card["date"],
                "venue": card["raw_location"],
            })

    events = []
    for card, subject in eligible.values():
        if date.fromisoformat(card["date"]) < today:
            continue
        event = card_to_event(card)
        events.append(event)
        _DIAGNOSTICS.append({
            "reason": "included_canonical_artist",
            "title": card["title"],
            "date": card["date"],
            "classification_url": subject["url"],
        })

    deduplicated = {}
    for event in events:
        key = (event.date, match_key(event.headliner), match_key(event.venue), event.start_time)
        deduplicated[key] = event
    result = list(deduplicated.values())
    print(
        f"Created {len(result)} Los Production ConcertEvent records; "
        f"skipped {sum(d.get('reason') == 'unclassified_agenda_row' for d in _DIAGNOSTICS)} "
        "unclassified rows"
    )
    return result
