import json
import re
import threading
import unicodedata
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


def _fold(value):
    value = unicodedata.normalize("NFKD", clean_text(value).casefold())
    return "".join(character for character in value if not unicodedata.combining(character))


def evidenced_title_semantics(title, description):
    """Separate Sunset presentation copy only when its own detail proves it."""
    raw = clean_text(title).strip(" .")
    prose = clean_text(
        BeautifulSoup(description or "", "html.parser").get_text(" ", strip=True)
    )
    folded_prose = _fold(prose)

    # These programme grammars explicitly distinguish context from the named
    # act.  The rule is Sunset-specific and never treats a bare dash or "avec"
    # as a general artist separator.
    tribute = re.fullmatch(
        r"(?P<context>.+\btribute)\s+[–—-]\s+(?P<artist>.+)", raw, re.I
    )
    if tribute:
        return clean_text(tribute.group("artist")), clean_text(tribute.group("context"))

    programme_with = re.fullmatch(
        r"(?P<context>(?:hommage(?:\s+[àa])?|jazz\s*&\s*go[uû]ter|jam\s+session)\b.+?)"
        r"\s+(?:avec|with)\s+(?P<artist>.+?)"
        r"(?P<jam>\s+\+\s+(?:jam(?:\s+session)?|jam\s+vocale|jam\s+blues|jam\s+br[ée]sil))?\s*",
        raw,
        re.I,
    )
    if programme_with:
        context = clean_text(
            programme_with.group("context") + (programme_with.group("jam") or "")
        )
        return clean_text(programme_with.group("artist")), context

    # A featured-artist list remains presentation context when the prose names
    # a distinct project and describes it as the current duo/project.
    project_match = re.fullmatch(
        r"(?P<project>.+?)\s+ft\.?\s+.+?\s+[-–—]\s+Festival\s+.+",
        raw,
        re.I,
    )
    if project_match:
        project = clean_text(project_match.group("project"))
        if (
            _fold(project) in folded_prose
            and re.search(r"\bduo\b", prose, re.I)
            and re.search(r"\bprojet\b", prose, re.I)
        ):
            return project, raw

    # Quoted work/show names are context only when the detail independently
    # names the preceding act.  Ampersands are retained inside one opaque
    # billed identity; they are used solely to corroborate a described duo.
    quoted = re.match(r"(?P<artist>.+?)(?:\s+[-–—])?\s+[\"“«]", raw)
    candidate = clean_text(quoted.group("artist")).rstrip(" -–—") if quoted else ""
    if candidate and not re.match(
        r"(?:hommage|jazz\s*&\s*go[uû]ter|jam\s+session|festival)\b",
        candidate,
        re.I,
    ):
        candidate_folded = _fold(candidate)
        exact_evidence = candidate_folded in folded_prose
        duo_evidence = False
        if " & " in candidate and re.search(r"\bduo\b", prose, re.I):
            names = [clean_text(part) for part in candidate.split(" & ")]
            duo_evidence = len(names) == 2 and all(_fold(name) in folded_prose for name in names)
        ensemble_base = re.sub(
            r"\s+(?:group|trio|quartet|quintet|orchestra|orchestre|ensemble)$",
            "",
            candidate,
            flags=re.I,
        )
        ensemble_evidence = (
            ensemble_base != candidate
            and _fold(ensemble_base) in folded_prose
            and bool(re.search(r"\b(?:duo|trio|quartet|quintet|groupe|formation|ensemble)\b", prose, re.I))
        )
        if exact_evidence or duo_evidence or ensemble_evidence:
            return candidate, raw

    festival = re.fullmatch(r"(?P<artist>.+?)\s+[-–—]\s+Festival\s+.+", raw, re.I)
    if festival:
        candidate = clean_text(festival.group("artist"))
        if _fold(candidate) in folded_prose:
            return candidate, raw

    return raw, None


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

    raw_title = clean_text(ticketing.get("title")).strip(" .")
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
    description = clean_text(ticketing.get("description"))
    headliner, evidenced_event_title = evidenced_title_semantics(raw_title, description)
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
            event_title=evidenced_event_title or raw_title,
            raw_title=raw_title if evidenced_event_title else None,
            identity_aliases=[raw_title] if evidenced_event_title else None,
            description=description or None,
        ))

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
    events = list(events_by_key.values())

    if errors:
        if not events:
            raise RuntimeError(
                f"{len(errors)} Sunset/Sunside detail pages failed; first: {errors[0]}"
            )
        print(
            f"Sunset/Sunside partial scrape: {len(errors)} detail page(s) failed; "
            f"keeping {len(events)} successfully parsed events. First error: {errors[0]}"
        )

    if not events:
        raise RuntimeError("Sunset/Sunside returned zero dated performances")
    print(f"Created {len(events)} Sunset/Sunside ConcertEvent records")
    return events
