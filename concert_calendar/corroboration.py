import json
import os
import re
import unicodedata
from datetime import datetime
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


FACEBOOK_REQUEST_TIMEOUT = 10
BANDSINTOWN_REQUEST_TIMEOUT = 10
MAX_FACEBOOK_EVENTS_PER_RUN = 25
MAX_BANDSINTOWN_EVENTS_PER_RUN = 25
MAX_BANDSINTOWN_RESULTS = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    ),
}


def normalize(value):
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(character for character in text if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def is_direct_facebook_event_url(url):
    return bool(re.match(
        r"^https?://(?:www\.)?facebook\.com/events/\d+/?(?:[?#].*)?$",
        url or "",
        re.I,
    ))


def _event_json_ld(soup):
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        queue = payload if isinstance(payload, list) else [payload]
        while queue:
            item = queue.pop(0)
            if not isinstance(item, dict):
                continue
            if item.get("@type") == "Event":
                return item
            graph = item.get("@graph")
            if isinstance(graph, list):
                queue.extend(graph)
    return {}


def parse_public_event_metadata(html):
    soup = BeautifulSoup(html, "html.parser")
    payload = _event_json_ld(soup)
    if not payload:
        return {}
    performer = payload.get("performer") or {}
    if isinstance(performer, list):
        performer = performer[0] if len(performer) == 1 else {}
    location = payload.get("location") or {}
    address = location.get("address") or {} if isinstance(location, dict) else {}
    start = payload.get("startDate") or ""
    try:
        parsed_start = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
    except ValueError:
        parsed_start = None
    offers = payload.get("offers") or {}
    if isinstance(offers, list):
        offers = next((item for item in offers if isinstance(item, dict)), {})
    return {
        "artist": (
            performer.get("name") if isinstance(performer, dict) else None
        ) or payload.get("name"),
        "date": parsed_start.date().isoformat() if parsed_start else None,
        "start_time": parsed_start.strftime("%H:%M") if parsed_start else None,
        "venue": location.get("name") if isinstance(location, dict) else None,
        "city": address.get("addressLocality") if isinstance(address, dict) else None,
        "ticket_url": offers.get("url") if isinstance(offers, dict) else None,
    }


def apply_corroboration(event, metadata, *, source):
    required = (
        normalize(metadata.get("artist")) == normalize(event.headliner)
        and metadata.get("date") == event.date[:10]
        and normalize(metadata.get("venue")) == normalize(event.venue)
    )
    city = metadata.get("city")
    if city and normalize(city) != normalize(event.city):
        required = False
    if not required:
        return {
            "source": source,
            "status": "not_applied",
            "reason": "canonical_identity_mismatch",
        }
    applied = []
    if not event.start_time and metadata.get("start_time"):
        event.start_time = metadata["start_time"]
        applied.append("start_time")
    if not event.ticket_url and metadata.get("ticket_url"):
        event.ticket_url = metadata["ticket_url"]
        applied.append("ticket_url")
    return {
        "source": source,
        "status": "applied" if applied else "corroborated",
        "fields": applied,
    }


def corroborate_facebook_event(event, *, session=None, enabled=None):
    if not is_direct_facebook_event_url(event.facebook_event_url):
        return {"source": "Facebook Events", "status": "skipped", "reason": "no_direct_event_url"}
    if enabled is None:
        enabled = os.getenv("FACEBOOK_EVENT_CORROBORATION") == "1"
    if not enabled:
        return {"source": "Facebook Events", "status": "disabled"}
    session = session or requests.Session()
    try:
        response = session.get(
            event.facebook_event_url,
            headers=HEADERS,
            timeout=FACEBOOK_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        metadata = parse_public_event_metadata(response.text)
        if not metadata:
            return {"source": "Facebook Events", "status": "unavailable"}
        return apply_corroboration(event, metadata, source="Facebook Events")
    except Exception as error:
        return {
            "source": "Facebook Events",
            "status": "unavailable",
            "reason": f"{type(error).__name__}: {error}",
        }


def corroborate_bandsintown_event(event, *, session=None, app_id=None):
    app_id = app_id or os.getenv("BANDSINTOWN_APP_ID")
    if not app_id:
        return {"source": "Bandsintown", "status": "disabled", "reason": "no_credential"}
    session = session or requests.Session()
    url = f"https://rest.bandsintown.com/artists/{quote(event.headliner, safe='')}/events"
    try:
        response = session.get(
            url,
            params={"app_id": app_id, "date": event.date[:10]},
            headers=HEADERS,
            timeout=BANDSINTOWN_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or len(payload) > MAX_BANDSINTOWN_RESULTS:
            return {"source": "Bandsintown", "status": "unavailable", "reason": "invalid_or_unbounded_payload"}
        for item in payload:
            if not isinstance(item, dict):
                continue
            venue = item.get("venue") or {}
            starts_at = item.get("datetime") or ""
            try:
                parsed_start = datetime.fromisoformat(str(starts_at).replace("Z", "+00:00"))
            except ValueError:
                continue
            metadata = {
                "artist": event.headliner,
                "date": parsed_start.date().isoformat(),
                "start_time": parsed_start.strftime("%H:%M"),
                "venue": venue.get("name") if isinstance(venue, dict) else None,
                "city": venue.get("city") if isinstance(venue, dict) else None,
                "ticket_url": item.get("url"),
            }
            result = apply_corroboration(event, metadata, source="Bandsintown")
            if result.get("reason") != "canonical_identity_mismatch":
                return result
        return {"source": "Bandsintown", "status": "not_applied", "reason": "no_exact_event_match"}
    except Exception as error:
        return {
            "source": "Bandsintown",
            "status": "unavailable",
            "reason": f"{type(error).__name__}: {error}",
        }


def corroborate_events(events):
    diagnostics = []
    facebook_enabled = os.getenv("FACEBOOK_EVENT_CORROBORATION") == "1"
    bandsintown_enabled = bool(os.getenv("BANDSINTOWN_APP_ID"))
    if facebook_enabled:
        candidates = [event for event in events if is_direct_facebook_event_url(event.facebook_event_url)]
        for event in candidates[:MAX_FACEBOOK_EVENTS_PER_RUN]:
            diagnostics.append(corroborate_facebook_event(event, enabled=True))
    if bandsintown_enabled:
        candidates = [event for event in events if not event.start_time or not event.ticket_url]
        for event in candidates[:MAX_BANDSINTOWN_EVENTS_PER_RUN]:
            diagnostics.append(corroborate_bandsintown_event(event))
    return diagnostics
