import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Sunset/Sunside"
PROGRAMME_URL = "https://billetterie.sunset-sunside.com/"
REQUEST_TIMEOUT = 30
MAX_TICKETINGS = 500
MAX_WORKERS = 8
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}
_thread_local = threading.local()


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def next_data(html):
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        raise RuntimeError("Sunset/Sunside page has no __NEXT_DATA__ payload")
    return json.loads(script.string or script.get_text())


def programme_items(html):
    payload = next_data(html)
    collection = payload["props"]["pageProps"]["entities"]["ticketings"]
    items = collection.get("hydra:member") or []
    total = collection.get("hydra:totalItems")
    if not isinstance(total, int) or total > MAX_TICKETINGS:
        raise RuntimeError(f"Unexpected Sunset/Sunside listing count: {total!r}")
    if len(items) != total:
        raise RuntimeError(
            f"Incomplete Sunset/Sunside listing: received {len(items)} of {total}"
        )
    return [item for item in items if item.get("type") == "dated_events"]


def room_name(ticketing):
    venue = ticketing.get("venue") or {}
    name = clean_text(venue.get("name"))
    room = clean_text(venue.get("seatingName"))
    if name.casefold() == "sunset sunside" and room.casefold() in {"sunset", "sunside"}:
        return f"Sunset/Sunside — {room}"
    return name or clean_text(ticketing.get("place"))


def image_url(ticketing):
    media = ticketing.get("mediaList") or []
    path = clean_text(media[0].get("path")) if media else ""
    if not path:
        return None
    extension = path.rsplit(".", 1)[-1].casefold()
    if extension not in {"jpg", "jpeg", "png", "webp"}:
        extension = "jpeg"
    return f"https://img.mapado.net/{path}_thumbs/340-340.{extension}"


def parse_detail_payload(payload, detail_url, listing_item=None):
    page_props = payload["props"]["pageProps"]
    entities = page_props["entities"]
    ticketing = entities["ticketing"]
    collection = entities["eventDates"]
    sessions = collection.get("hydra:member") or []
    total = collection.get("hydra:totalItems", len(sessions))
    if len(sessions) != total:
        raise RuntimeError(
            f"Sunset/Sunside detail pagination incomplete for {detail_url}: "
            f"received {len(sessions)} of {total}"
        )

    headliner = clean_text(ticketing.get("title")).strip(" .")
    venue = room_name(ticketing)
    city = clean_text((ticketing.get("venue") or {}).get("city") or "Paris")
    category_data = ticketing.get("ticketingCategory") or {}
    category = clean_text(
        category_data.get("name") if isinstance(category_data, dict) else ""
    )
    if not category and listing_item:
        listing_category = listing_item.get("ticketingCategory") or {}
        if isinstance(listing_category, dict):
            category = clean_text(listing_category.get("name"))
    picture = image_url(ticketing)
    if not headliner or not venue:
        return []

    parsed = []
    for session in sessions:
        try:
            start = datetime.fromisoformat(clean_text(session.get("startDate")))
        except ValueError:
            continue
        if start.date() < date.today():
            continue
        status = clean_text(session.get("availabilityStatus") or session.get("status")).casefold()
        ticket_status = None
        sold_out = status in {"soldout", "sold_out", "full"}
        if "cancel" in status:
            ticket_status = "cancelled"
        elif sold_out:
            ticket_status = "sold_out"
        elif "entrée libre" in category.casefold():
            ticket_status = "free"
        elif session.get("onSale"):
            ticket_status = "tickets"

        parsed.append(ConcertEvent(
            date=start.date().isoformat(),
            headliner=headliner,
            venue=venue,
            city=city,
            department="75" if city.casefold() == "paris" else "",
            promoters=None,
            genre=category or None,
            facebook_event_url=None,
            ticket_url=detail_url,
            sold_out=sold_out,
            ticket_status=ticket_status,
            start_time=start.strftime("%H:%M"),
            image_url=picture,
            image_source=SOURCE_NAME if picture else None,
        ))

    same_identity = {}
    for event in parsed:
        key = (event.date, event.headliner.casefold(), event.venue.casefold())
        same_identity.setdefault(key, []).append(event)
    for group in same_identity.values():
        if len(group) > 1:
            for event in group:
                event.headliner = f"{event.headliner} – {event.start_time.replace(':', 'h')}"
    return parsed


def _session():
    if not hasattr(_thread_local, "session"):
        _thread_local.session = requests.Session()
    return _thread_local.session


def fetch_detail(item):
    slug = clean_text(item.get("slug"))
    if not slug:
        return []
    url = urljoin(PROGRAMME_URL, f"event/{slug}")
    response = _session().get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return parse_detail_payload(next_data(response.text), url, item)


def event_key(event):
    return (
        event.date, event.headliner.casefold(), event.venue.casefold(),
        event.start_time, event.ticket_url,
    )


def load_events():
    session = requests.Session()
    print("Downloading Sunset/Sunside programme...")
    response = session.get(PROGRAMME_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    items = programme_items(response.text)
    events_by_key = {}
    errors = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_detail, item): item for item in items}
        for future in as_completed(futures):
            item = futures[future]
            try:
                for event in future.result():
                    events_by_key.setdefault(event_key(event), event)
            except Exception as exc:
                errors.append(f"{item.get('slug')}: {exc}")
    if errors:
        raise RuntimeError(
            f"{len(errors)} Sunset/Sunside detail pages failed; first: {errors[0]}"
        )
    events = list(events_by_key.values())
    if not events:
        raise RuntimeError("Sunset/Sunside returned zero dated performances")
    print(f"Created {len(events)} Sunset/Sunside ConcertEvent records")
    return events
