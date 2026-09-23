import re
import unicodedata
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent


SOURCE_NAME = "Les Étoiles"
BASE_URL = "https://www.etoiles.paris/"
PROGRAMME_URL = f"{BASE_URL}agenda/"
REST_EVENTS_URL = f"{BASE_URL}wp-json/wp/v2/evenement"
REST_FORMATS_URL = f"{BASE_URL}wp-json/wp/v2/format"
REST_STATUSES_URL = f"{BASE_URL}wp-json/wp/v2/status-event"
REQUEST_TIMEOUT = 30
REST_PER_PAGE = 100
MAX_REST_PAGES = 10
HEADERS = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
REST_FIELDS = "id,slug,link,date,format,genre,status-event,title"

MONTHS = {
    "jan": 1, "janv": 1, "janvier": 1,
    "fev": 2, "fevr": 2, "fevrier": 2,
    "mar": 3, "mars": 3,
    "avr": 4, "avril": 4,
    "mai": 5,
    "juin": 6,
    "juil": 7, "juillet": 7,
    "aou": 8, "aout": 8,
    "sep": 9, "sept": 9, "septembre": 9,
    "oct": 10, "octobre": 10,
    "nov": 11, "novembre": 11,
    "dec": 12, "decembre": 12,
}
WEEKDAYS = {
    "lun": 0, "lundi": 0,
    "mar": 1, "mardi": 1,
    "mer": 2, "mercredi": 2,
    "jeu": 3, "jeudi": 3,
    "ven": 4, "vendredi": 4,
    "sam": 5, "samedi": 5,
    "dim": 6, "dimanche": 6,
}


class EtoilesScraperError(RuntimeError):
    pass


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def fold(value):
    value = unicodedata.normalize("NFKD", clean(value))
    return "".join(c for c in value if not unicodedata.combining(c)).casefold()


def _json_response(response, *, context):
    response.raise_for_status()
    try:
        payload = response.json()
    except (TypeError, ValueError) as exc:
        raise EtoilesScraperError(f"Malformed Les Étoiles {context} JSON") from exc
    if not isinstance(payload, list):
        raise EtoilesScraperError(f"Malformed Les Étoiles {context}: expected a list")
    return payload


def _fetch_terms(session, url, *, context):
    response = session.get(
        url,
        params={"per_page": REST_PER_PAGE, "hide_empty": "false"},
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    terms = _json_response(response, context=context)
    for term in terms:
        if not isinstance(term, dict) or not isinstance(term.get("id"), int) or not term.get("slug"):
            raise EtoilesScraperError(f"Malformed Les Étoiles {context} term")
    return terms


def _term_id(terms, slug, *, required=False):
    matches = [term["id"] for term in terms if fold(term.get("slug")) == slug]
    if len(matches) > 1 or (required and len(matches) != 1):
        raise EtoilesScraperError(
            f"Expected exactly one Les Étoiles taxonomy term with slug {slug!r}"
        )
    return matches[0] if matches else None


def fetch_rest_posts(session):
    """Fetch and validate the complete WordPress event collection."""

    posts = []
    expected_pages = None
    expected_total = None
    for page in range(1, MAX_REST_PAGES + 1):
        print(f"Downloading Les Étoiles REST events page {page}")
        response = session.get(
            REST_EVENTS_URL,
            params={"per_page": REST_PER_PAGE, "page": page, "_fields": REST_FIELDS},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        page_posts = _json_response(response, context=f"events page {page}")
        try:
            page_count = int(response.headers["X-WP-TotalPages"])
            total_count = int(response.headers["X-WP-Total"])
        except (KeyError, TypeError, ValueError) as exc:
            raise EtoilesScraperError(
                "Les Étoiles REST pagination headers are missing or malformed"
            ) from exc
        if not 1 <= page_count <= MAX_REST_PAGES or total_count < 0:
            raise EtoilesScraperError("Les Étoiles REST pagination is outside bounded limits")
        if expected_pages is None:
            expected_pages, expected_total = page_count, total_count
        elif (page_count, total_count) != (expected_pages, expected_total):
            raise EtoilesScraperError("Les Étoiles REST pagination changed during retrieval")
        if page > expected_pages:
            raise EtoilesScraperError("Les Étoiles REST returned an unexpected extra page")
        if not page_posts:
            raise EtoilesScraperError(f"Les Étoiles REST events page {page} is unexpectedly empty")
        for post in page_posts:
            if (
                not isinstance(post, dict)
                or not isinstance(post.get("id"), int)
                or not isinstance(post.get("format"), list)
                or not all(isinstance(term_id, int) for term_id in post["format"])
            ):
                raise EtoilesScraperError(f"Malformed Les Étoiles event row on page {page}")
        posts.extend(page_posts)
        if page == expected_pages:
            break
    else:
        raise EtoilesScraperError("Les Étoiles REST pagination exceeded its safety bound")

    if len(posts) != expected_total:
        raise EtoilesScraperError(
            f"Incomplete Les Étoiles REST collection: expected {expected_total}, got {len(posts)}"
        )
    post_ids = [post["id"] for post in posts]
    if len(post_ids) != len(set(post_ids)):
        raise EtoilesScraperError("Les Étoiles REST collection contains duplicate post IDs")
    return posts


def resolve_event_date(date_label, published_at, *, candidate_years=None):
    """Resolve one yearless French date using its weekday and bounded post-year evidence."""

    normalized = fold(date_label).rstrip(".")
    match = re.fullmatch(r"([a-z]+)\s+(\d{1,2})\s+([a-z]+)\.?", normalized)
    if not match:
        raise EtoilesScraperError(f"Malformed Les Étoiles event date {date_label!r}")
    weekday = WEEKDAYS.get(match.group(1))
    month = MONTHS.get(match.group(3))
    if weekday is None or month is None:
        raise EtoilesScraperError(f"Unknown Les Étoiles event date {date_label!r}")
    try:
        published = datetime.fromisoformat(str(published_at).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise EtoilesScraperError("Malformed Les Étoiles REST publication timestamp") from exc
    years = tuple(candidate_years) if candidate_years is not None else tuple(
        range(published.year, published.year + 3)
    )
    candidates = []
    for year in years:
        try:
            candidate = date(int(year), month, int(match.group(2)))
        except (TypeError, ValueError):
            continue
        if candidate.weekday() == weekday:
            candidates.append(candidate)
    if len(candidates) != 1:
        raise EtoilesScraperError(
            f"Les Étoiles event date {date_label!r} resolved to {len(candidates)} years"
        )
    return candidates[0]


def _dates_block(soup):
    content = soup.select_one(".SingleEvenement__content")
    labels = [] if content is None else [
        label for label in content.select(".ts-label")
        if fold(label.get_text(" ", strip=True)) == "dates"
    ]
    if len(labels) != 1:
        raise EtoilesScraperError("Les Étoiles detail page has no unique Dates block")
    container = labels[0].find_next_sibling()
    if container is None:
        raise EtoilesScraperError("Les Étoiles Dates block has no values")
    rows = [
        clean(row.get_text(" ", strip=True))
        for row in container.find_all("div", recursive=False)
    ]
    rows = [row for row in rows if row]
    if not rows:
        rows = re.findall(
            r"(?:lun(?:di)?|mar(?:di)?|mer(?:credi)?|jeu(?:di)?|ven(?:dredi)?|sam(?:edi)?|dim(?:anche)?)\s+\d{1,2}\s+[A-Za-zÀ-ÿ]+\. ?",
            clean(container.get_text(" ", strip=True)),
            flags=re.IGNORECASE,
        )
        rows = [clean(row) for row in rows]
    if not rows:
        raise EtoilesScraperError("Les Étoiles Dates block is empty")
    return rows


def parse_detail_page(html, post, *, today=None):
    cutoff = today or date.today()
    if not isinstance(post, dict) or not post.get("link") or not post.get("date"):
        raise EtoilesScraperError("Malformed Les Étoiles REST concert row")
    soup = BeautifulSoup(html, "html.parser")
    header = soup.select_one(".SingleEvenement__header")
    heading = header.select_one("h1") if header else None
    if heading is None:
        raise EtoilesScraperError(f"Les Étoiles detail page has no primary H1: {post['link']}")
    headliner = clean(heading.get_text(" ", strip=True))
    primary = heading.parent
    tags = [fold(tag.get_text(" ", strip=True)) for tag in primary.select(".tag")]
    labels = [clean(label.get_text(" ", strip=True)) for label in primary.select(".ts-label")]
    start_times = [label for label in labels if re.fullmatch(r"\d{1,2}:\d{2}", label)]
    if not headliner or "concert" not in tags or len(start_times) != 1:
        raise EtoilesScraperError(f"Malformed Les Étoiles primary event data: {post['link']}")

    image = element_image_url(header.select_one("img"), base_url=post["link"])
    resolved_dates = [resolve_event_date(row, post["date"]) for row in _dates_block(soup)]
    if len(resolved_dates) != len(set(resolved_dates)):
        raise EtoilesScraperError(f"Duplicate Les Étoiles performance date: {post['link']}")
    events = []
    for event_date in resolved_dates:
        if event_date < cutoff:
            continue
        events.append(ConcertEvent(
            date=event_date.isoformat(),
            headliner=headliner,
            venue=SOURCE_NAME,
            city="Paris",
            department="75",
            ticket_url=post["link"],
            ticket_status="tickets",
            start_time=start_times[0],
            image_url=image,
            image_source=SOURCE_NAME if image else None,
        ))
    return events


def load_events(today=None):
    today = today or date.today()
    session = requests.Session()
    format_terms = _fetch_terms(session, REST_FORMATS_URL, context="format taxonomy")
    concert_id = _term_id(format_terms, "concert", required=True)
    status_terms = _fetch_terms(session, REST_STATUSES_URL, context="status taxonomy")
    cancelled_id = _term_id(status_terms, "annule", required=True)

    posts = fetch_rest_posts(session)
    concert_posts = [post for post in posts if concert_id in post["format"]]
    events = {}
    for post in concert_posts:
        statuses = post.get("status-event") or []
        if not isinstance(statuses, list):
            raise EtoilesScraperError(f"Malformed Les Étoiles status data for post {post['id']}")
        if cancelled_id in statuses:
            continue
        detail_url = post.get("link")
        if not isinstance(detail_url, str) or not detail_url.startswith(f"{BASE_URL}evenement/"):
            raise EtoilesScraperError(f"Malformed Les Étoiles detail URL for post {post['id']}")
        print(f"Downloading Les Étoiles concert detail: {detail_url}")
        response = session.get(detail_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        parsed = parse_detail_page(
            response.text,
            post,
            today=today,
        )
        for event in parsed:
            key = (event.date, fold(event.headliner), event.start_time)
            events.setdefault(key, event)

    result = sorted(
        events.values(),
        key=lambda event: (event.date, fold(event.headliner), event.start_time or ""),
    )
    result = discard_repeated_generic_images(result)
    print(f"Created {len(result)} Les Étoiles ConcertEvent records")
    return result
