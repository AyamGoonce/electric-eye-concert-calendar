"""Public embedded Mapado data for venue-owned ticket offices only."""
import json
from datetime import datetime
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, official_image_url
from concert_calendar.models import ConcertEvent

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ConcertCalendar/1.0)"}
MAX_DETAILS = 100
NON_CONCERT_CATEGORIES = {"atelier", "conférence", "exposition", "stage", "visite"}


def entities(html):
    node = BeautifulSoup(html, "html.parser").select_one("#__NEXT_DATA__")
    if node is None:
        raise ValueError("Official ticket office: missing Next data")
    return json.loads(node.text)["props"]["pageProps"]["entities"]


def complete_members(collection):
    members = collection["hydra:member"]
    if len(members) != collection["hydra:totalItems"]:
        raise ValueError("Official ticket office: incomplete paginated collection")
    return members


def parse_detail(data, listing, *, base_url, venue, city, department, today):
    item = data["ticketing"]
    # Offer/membership products and explicitly non-concert categories are not shows.
    category = (listing.get("ticketingCategory") or {}).get("name", "")
    if item.get("type") != "dated_events" or category.casefold() in NON_CONCERT_CATEGORIES:
        return []
    if item["venue"]["@id"] != listing["venue"]["@id"]:
        raise ValueError("Official ticket office: event venue changed")
    genre = category.removeprefix("Concert - ") if category.startswith("Concert - ") else None
    if genre == "Jeune Public":
        genre = None
    image = next((official_image_url("https://img.mapado.net/" + m["path"]) for m in item.get("mediaList", []) if m.get("imageType") == "image"), None)
    events = []
    for occurrence in complete_members(data["eventDates"]):
        if occurrence.get("status") in {"cancelled", "postponed"} or occurrence.get("availabilityStatus") in {"cancelled", "postponed"}:
            continue
        start = datetime.fromisoformat(occurrence["startDate"]).astimezone(ZoneInfo("Europe/Paris"))
        if start.date() < today:
            continue
        sold = occurrence.get("availabilityStatus") == "soldOut"
        events.append(ConcertEvent(
            date=start.date().isoformat(), start_time=start.strftime("%H:%M"),
            headliner=item["title"].strip(), venue=venue, city=city, department=department,
            ticket_url=urljoin(base_url, "event/" + item["slug"]), genre=genre,
            image_url=image, image_source=venue if image else None, sold_out=sold,
            ticket_status="sold_out" if sold else ("tickets" if occurrence.get("onSale") else None),
        ))
    return events


def load_official(base_url, venue, city, department, venue_ids, today=None):
    today = today or datetime.now(ZoneInfo("Europe/Paris")).date()
    with requests.Session() as session:
        session.headers.update(HEADERS)
        def get(url):
            response = session.get(url, timeout=30)
            response.raise_for_status()
            return entities(response.text)
        listings = complete_members(get(base_url)["ticketings"])
        if len(listings) > MAX_DETAILS:
            raise ValueError("Official ticket office exceeds bounded programme size")
        output = {}
        for item in listings:
            if item.get("type") != "dated_events":
                continue
            if item["venue"]["@id"] not in venue_ids:
                # A venue's ticket office can sell off-site events; never relocate them.
                continue
            if (item.get("ticketingCategory") or {}).get("name", "").casefold() in NON_CONCERT_CATEGORIES:
                continue
            detail = get(urljoin(base_url, "event/" + item["slug"]))
            for event in parse_detail(detail, item, base_url=base_url, venue=venue, city=city, department=department, today=today):
                output.setdefault((event.date, event.start_time, event.headliner), event)
    return discard_repeated_generic_images(list(output.values()))
