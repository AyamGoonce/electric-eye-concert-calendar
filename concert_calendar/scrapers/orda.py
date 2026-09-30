import re
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "On the RoaD Again / ORDA"
CONCERTS_URL = "https://ontheroad-again.eu/concerts/"
REST_EVENTS_URL = "https://ontheroad-again.eu/wp-json/wp/v2/events"
REQUEST_TIMEOUT = 30
REST_PAGE_SIZE = 100
REST_PAGE_SAFETY_CEILING = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
    "Accept": "application/json, text/html;q=0.9",
}


class OrdaScraperError(RuntimeError):
    pass


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def split_location(value):
    text = clean_text(value)
    if " · " not in text:
        return text, ""
    venue, city = text.rsplit(" · ", 1)
    return clean_text(venue), clean_text(city)


def parse_datetime(value):
    try:
        parsed = datetime.fromisoformat(clean_text(value))
    except ValueError:
        return "", None
    return parsed.date().isoformat(), parsed.strftime("%H:%M")


def image_url(node):
    image = node.select_one("img")
    if not image:
        return None
    return clean_text(image.get("data-src") or image.get("src")) or None


def parse_event_tile(node):
    link = node.select_one("a[href]")
    time = node.select_one("time[datetime]")
    info = node.select_one(".event-tile__info")
    artist = info.select_one("p") if info else None
    title = info.select_one("h2") if info else None
    location = info.select_one("span") if info else None
    event_date, start_time = parse_datetime(time.get("datetime") if time else "")
    headliner = clean_text(artist.get_text(" ", strip=True) if artist else "")
    venue, city = split_location(
        location.get_text(" ", strip=True) if location else ""
    )
    detail_url = clean_text(link.get("href")) if link else ""
    if not all((event_date, headliner, venue, city, detail_url)):
        return None
    return {
        "date": event_date,
        "start_time": start_time,
        "artist": headliner,
        "display_title": clean_text(title.get_text(" ", strip=True)) if title else "",
        "venue": venue,
        "city": city,
        "detail_url": detail_url,
        "is_production": node.select_one(".production-badge") is not None,
        "image_url": image_url(node),
    }


def parse_production_card(node):
    link = node.select_one("a[href]")
    time = node.select_one("time[datetime]")
    title = node.select_one("h3")
    location = node.select_one(".production-card__body p")
    event_date, start_time = parse_datetime(time.get("datetime") if time else "")
    bill = clean_text(title.get_text(" ", strip=True) if title else "")
    venue, city = split_location(
        location.get_text(" ", strip=True) if location else ""
    )
    detail_url = clean_text(link.get("href")) if link else ""
    if not all((event_date, bill, venue, city, detail_url)):
        return None
    return {
        "date": event_date,
        "start_time": start_time,
        "bill": bill,
        "venue": venue,
        "city": city,
        "detail_url": detail_url,
        "image_url": image_url(node),
    }


def production_key(item):
    return (
        item["date"], item["venue"].casefold(), item["city"].casefold(),
    )


def ordered_components(bill, tiles):
    positions = []
    folded = bill.casefold()
    for tile in tiles:
        artist = tile["artist"]
        position = folded.find(artist.casefold())
        if position < 0:
            return []
        positions.append((position, artist))
    return [artist for _, artist in sorted(set(positions))]


def fetch_event_metadata(session):
    metadata = {}
    expected_pages = None
    expected_total = None
    fetched = 0
    for page in range(1, REST_PAGE_SAFETY_CEILING + 1):
        response = session.get(
            REST_EVENTS_URL,
            params={"per_page": REST_PAGE_SIZE, "page": page},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise OrdaScraperError("events REST endpoint returned a non-list payload")
        if page == 1:
            try:
                expected_pages = int(response.headers.get("X-WP-TotalPages", "1"))
                expected_total = int(response.headers.get("X-WP-Total", str(len(payload))))
            except ValueError as error:
                raise OrdaScraperError("invalid REST pagination headers") from error
            if expected_pages > REST_PAGE_SAFETY_CEILING:
                raise OrdaScraperError("events REST pagination exceeded safety ceiling")
        fetched += len(payload)
        for record in payload:
            if not isinstance(record, dict):
                continue
            link = clean_text(record.get("link"))
            meta = record.get("meta") or {}
            if not link or not isinstance(meta, dict):
                continue
            ticket_url = clean_text(meta.get("event_call_action_0_event_link_rp"))
            metadata[link] = {
                "ticket_url": ticket_url or None,
                "is_production": bool(meta.get("orda_is_production")),
            }
        if expected_pages is not None and page >= expected_pages:
            break
    else:
        raise OrdaScraperError("events REST pagination did not terminate")
    if expected_total is not None and fetched != expected_total:
        raise OrdaScraperError(
            f"incomplete events REST inventory: expected {expected_total}, got {fetched}"
        )
    return metadata


def parse_events(html, metadata, *, today=None):
    today = today or date.today()
    soup = BeautifulSoup(html, "html.parser")
    tiles = [
        tile for tile in (parse_event_tile(node) for node in soup.select(".event-tile"))
        if tile and date.fromisoformat(tile["date"]) >= today
    ]
    productions = [
        card for card in (
            parse_production_card(node) for node in soup.select(".production-card")
        ) if card and date.fromisoformat(card["date"]) >= today
    ]
    production_keys = {production_key(card) for card in productions}
    tiles_by_production = {}
    for tile in tiles:
        if tile["is_production"]:
            tiles_by_production.setdefault(production_key(tile), []).append(tile)

    events = []
    for card in productions:
        components = ordered_components(
            card["bill"], tiles_by_production.get(production_key(card), []),
        )
        headliner = components[0] if components else card["bill"]
        meta = metadata.get(card["detail_url"], {})
        events.append(ConcertEvent(
            date=card["date"],
            headliner=headliner,
            venue=card["venue"],
            city=card["city"],
            department="",
            co_headliners=components[1:] or None,
            promoters=["ORDA"],
            ticket_url=meta.get("ticket_url") or card["detail_url"],
            ticket_status="tickets" if meta.get("ticket_url") else None,
            start_time=card["start_time"],
            event_title=card["bill"],
            authoritative_billing=bool(components),
            event_type="concert",
            performers=components or [card["bill"]],
            image_url=card["image_url"],
            image_source=SOURCE_NAME if card["image_url"] else None,
            raw_title=card["bill"],
        ))

    for tile in tiles:
        key = production_key(tile)
        if key in production_keys:
            continue
        meta = metadata.get(tile["detail_url"], {})
        explicit_production = tile["is_production"] or meta.get("is_production")
        events.append(ConcertEvent(
            date=tile["date"],
            headliner=tile["artist"],
            venue=tile["venue"],
            city=tile["city"],
            department="",
            promoters=["ORDA"] if explicit_production else None,
            ticket_url=meta.get("ticket_url") or tile["detail_url"],
            ticket_status="tickets" if meta.get("ticket_url") else None,
            start_time=tile["start_time"],
            event_type="concert",
            performers=[tile["artist"]],
            image_url=tile["image_url"],
            image_source=SOURCE_NAME if tile["image_url"] else None,
            raw_title=tile["artist"],
        ))
    return events


def load_events(today=None):
    session = requests.Session()
    response = session.get(CONCERTS_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    metadata = fetch_event_metadata(session)
    events = parse_events(response.text, metadata, today=today)
    print(f"Created {len(events)} ORDA ConcertEvent records")
    return events
