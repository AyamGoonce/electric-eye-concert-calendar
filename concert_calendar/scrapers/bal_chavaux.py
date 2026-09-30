import json
import re
from datetime import date, datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Bal Chavaux"
AGENDA_URL = "https://balchavaux.fr/agenda"
REQUEST_TIMEOUT = 30
PAGINATION_SAFETY_CEILING = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}

MONTHS = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
}

_DIAGNOSTICS = []


class BalChavauxScraperError(RuntimeError):
    pass


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def get_diagnostics():
    return list(_DIAGNOSTICS)


def parse_listing_row(row):
    link = row.select_one("a.block[href]")
    title = row.select_one("h2")
    date_node = row.select_one(".evt-date")
    if not link or not title or not date_node:
        return None
    day = clean_text(date_node.get("data-day"))
    month = MONTHS.get(clean_text(date_node.get("data-month")).casefold())
    year = clean_text(date_node.get("data-year"))
    try:
        event_date = date(int(year), month, int(day)).isoformat()
    except (TypeError, ValueError):
        return None
    time_node = row.select_one(".evt-date-hour")
    match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", clean_text(
        time_node.get_text(" ", strip=True) if time_node else ""
    ))
    category_node = row.select_one(".agenda--evt-categories")
    return {
        "date": event_date,
        "headliner": clean_text(title.get_text(" ", strip=True)),
        "start_time": f"{int(match.group(1)):02d}:{match.group(2)}" if match else None,
        "category": clean_text(category_node.get_text(" / ", strip=True)) or None
        if category_node else None,
        "detail_url": urljoin(AGENDA_URL, clean_text(link.get("href"))),
    }


def find_event_json_ld(soup):
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        objects = payload if isinstance(payload, list) else [payload]
        for item in objects:
            if isinstance(item, dict) and item.get("@type") == "Event":
                return item
    return {}


def organizer_names(payload):
    organizers = payload.get("organizer") or []
    if isinstance(organizers, dict):
        organizers = [organizers]
    return [
        clean_text(item.get("name"))
        for item in organizers
        if isinstance(item, dict) and clean_text(item.get("name"))
    ] or None


def offer_url(payload, detail_url):
    offers = payload.get("offers") or []
    if isinstance(offers, dict):
        offers = [offers]
    for offer in offers:
        if isinstance(offer, dict) and clean_text(offer.get("url")):
            return urljoin(detail_url, clean_text(offer.get("url")))
    return detail_url


def parse_detail_page(html, listing, *, today=None):
    today = today or date.today()
    soup = BeautifulSoup(html, "html.parser")
    payload = find_event_json_ld(soup)
    headliner = clean_text(payload.get("name")) or listing["headliner"]
    start_date = clean_text(payload.get("startDate"))
    try:
        parsed_start = datetime.fromisoformat(start_date) if start_date else None
    except ValueError:
        parsed_start = None
    event_date = parsed_start.date().isoformat() if parsed_start else listing["date"]
    if date.fromisoformat(event_date) < today:
        return None
    start_time = (
        parsed_start.strftime("%H:%M") if parsed_start else listing["start_time"]
    )
    location = payload.get("location") or {}
    address = location.get("address") or {} if isinstance(location, dict) else {}
    venue = clean_text(location.get("name")) if isinstance(location, dict) else ""
    city = clean_text(address.get("addressLocality")) if isinstance(address, dict) else ""
    postcode = clean_text(address.get("postalCode")) if isinstance(address, dict) else ""
    department = postcode[:2] if re.match(r"^(?:75|7[78]|9[1-5])\d{3}$", postcode) else ""
    category = clean_text(payload.get("keywords")) or listing["category"]
    image = payload.get("image") or {}
    image_url = clean_text(image.get("url")) if isinstance(image, dict) else ""
    detail_url = listing["detail_url"]
    return ConcertEvent(
        date=event_date,
        headliner=headliner,
        venue=venue or SOURCE_NAME,
        city=city or "Montreuil",
        department=department,
        promoters=organizer_names(payload),
        category=category or None,
        event_type="concert",
        performers=[headliner],
        start_time=start_time,
        ticket_url=offer_url(payload, detail_url),
        ticket_status="tickets" if payload.get("offers") else None,
        image_url=image_url or None,
        image_source=SOURCE_NAME if image_url else None,
        raw_title=headliner,
    )


def fetch_listing_rows(session):
    rows = {}
    page_url = AGENDA_URL
    visited = set()
    while page_url and page_url not in visited:
        if len(visited) >= PAGINATION_SAFETY_CEILING:
            raise BalChavauxScraperError("agenda pagination exceeded safety ceiling")
        visited.add(page_url)
        response = session.get(page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for row in soup.select(".views-row"):
            item = parse_listing_row(row)
            if item:
                rows[item["detail_url"]] = item
        next_link = soup.select_one('.pager a[rel="next"][href], a[rel="next"][href]')
        page_url = (
            urljoin(page_url, clean_text(next_link.get("href")))
            if next_link and clean_text(next_link.get("href"))
            else None
        )
    return list(rows.values())


def load_events(today=None):
    _DIAGNOSTICS.clear()
    session = requests.Session()
    events = []
    for listing in fetch_listing_rows(session):
        response = session.get(
            listing["detail_url"], headers=HEADERS, timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        event = parse_detail_page(response.text, listing, today=today)
        if event is None:
            _DIAGNOSTICS.append({
                "reason": "malformed_or_past_detail",
                "detail_url": listing["detail_url"],
            })
        else:
            events.append(event)
    print(f"Created {len(events)} Bal Chavaux ConcertEvent records")
    return events
