from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlparse

from concert_calendar.models import ConcertEvent


DEFAULT_OUTPUT_PATH = "output/production_calendar.html"

ARTIST_SORT_OVERRIDES = {
    "a perfect circle": "Perfect Circle",
}

VENUE_SORT_OVERRIDES: dict[str, str] = {}

GENRE_RULES = (
    ("Rock / Indie / Punk", ("rock", "indie", "punk", "shoegaze", "grunge", "psych", "new wave", "newwave")),
    ("Metal / Hard Rock", ("metal", "hard rock", "hardrock", "newcore")),
    ("Pop", ("pop",)),
    ("Hip-hop / Rap", ("hip hop", "hip-hop", "hiphop", "rap", "grime", "drill")),
    ("Electronic", ("electro", "electronic", "electronica", "synth", "dance", "club")),
    ("R&B / Soul / Funk", ("rnb", "r'n'b", "soul", "funk", "groove")),
    ("Jazz / Blues", ("jazz", "blues")),
    ("Folk / Country", ("folk", "country", "americana")),
    ("Reggae / Dub / Ska", ("reggae", "ragga", "dub", "ska")),
    ("World / Latin", ("latin", "latine", "cumbia", "bossa", "afrobeat", "afropop", "zouk", "musique du monde", "musiques traditionnelles")),
    ("French chanson", ("chanson francaise", "variete francaise")),
    ("Comedy", ("comedy", "one man show")),
)


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    normalized = normalized.casefold()

    return re.sub(r"\s+", " ", normalized).strip()


def alphabetical_sort_key(
    value: str,
    overrides: dict[str, str] | None = None,
) -> str:
    """Return a conservative, article-aware key without changing display text."""

    normalized = normalize_text(value)
    override = (overrides or {}).get(normalized)

    if override is not None:
        return normalize_text(override)

    return re.sub(r"^(?:(?:the|le|la|les)\s+|l['’]\s*)", "", normalized)


def parse_event_date(value: str) -> date | None:
    try:
        return date.fromisoformat((value or "")[:10])
    except ValueError:
        return None


def safe_ticket_url(value: str | None) -> str | None:
    if not value:
        return None

    parsed = urlparse(value)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None

    return value


def genre_categories(value: str | None) -> list[str]:
    normalized = normalize_text(value or "")

    if not normalized:
        return []

    return [
        category
        for category, keywords in GENRE_RULES
        if any(keyword in normalized for keyword in keywords)
    ]


def event_to_data(event: ConcertEvent) -> dict:
    return {
        "d": event.date[:10],
        "h": event.headliner,
        "o": event.openers or [],
        "v": event.venue,
        "c": event.city,
        "g": event.genre or "",
        "x": genre_categories(event.genre),
        "p": event.promoters or [],
        "t": safe_ticket_url(event.ticket_url),
    }


def prepare_upcoming_events(
    events: list[ConcertEvent],
    today: date | None = None,
) -> list[dict]:
    """
    Keep current/future events and sort by date, headliner, venue, then city.
    """

    cutoff = today or date.today()
    upcoming = []

    for event in events:
        event_date = parse_event_date(event.date)

        if event_date is None or event_date < cutoff:
            continue

        upcoming.append((event_date, event))

    upcoming.sort(
        key=lambda item: (
            item[0],
            normalize_text(item[1].headliner),
            normalize_text(item[1].venue),
            normalize_text(item[1].city),
        )
    )

    return [event_to_data(event) for _, event in upcoming]


def serialize_data(events: object) -> str:
    serialized = json.dumps(
        events,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def build_production_html(events: list[dict]) -> str:
    event_data = serialize_data(events)
    artist_sort_overrides = serialize_data(ARTIST_SORT_OVERRIDES)
    venue_sort_overrides = serialize_data(VENUE_SORT_OVERRIDES)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Île-de-France Concert Calendar</title>
  <style>
    :root {{
      color-scheme: light;
      --ee-bg: #edf1f5;
      --ee-surface: #ffffff;
      --ee-dark: #101010;
      --ee-text: #171717;
      --ee-text-soft: #454b53;
      --ee-muted: #6f7782;
      --ee-border: #d5dbe2;
      --ee-accent: #d82323;
      --ee-accent-hover: #b51d1d;
      --ee-on-dark: #faf8f4;
      --ee-wide: 1500px;
      font-family: "Instrument Sans", Arial, sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--ee-bg); color: var(--ee-text-soft); font-size: 16px; line-height: 1.5; }}
    main {{ width: min(calc(100% - 48px), var(--ee-wide)); margin: 0 auto 72px; }}
    header {{ margin: 0 -24px 30px; padding: 40px 24px 36px; background: var(--ee-dark); color: var(--ee-on-dark); border-bottom: 4px solid var(--ee-accent); }}
    h1 {{ margin: 0; color: var(--ee-on-dark); font-size: clamp(2.25rem, 4.2vw, 3.65rem); font-weight: 700; letter-spacing: -.04em; line-height: 1.02; }}
    .intro {{ color: #c7c1b9; margin: 10px 0 0; font-size: 1.05rem; }}
    .filters {{ display: grid; grid-template-columns: minmax(220px, 2fr) repeat(4, minmax(130px, 1fr)) auto; gap: 14px; padding: 18px; background: var(--ee-surface); border: 1px solid var(--ee-border); }}
    label {{ display: grid; gap: 6px; color: var(--ee-text-soft); font-size: .75rem; font-weight: 700; letter-spacing: .055em; text-transform: uppercase; }}
    input, select, button {{ min-width: 0; min-height: 44px; border: 1px solid #aeb6c0; border-radius: 0; background: var(--ee-surface); color: var(--ee-text); font: inherit; padding: 9px 11px; transition: border-color .17s ease, background-color .17s ease, color .17s ease; }}
    input:hover, select:hover {{ border-color: var(--ee-text-soft); }}
    button {{ align-self: end; cursor: pointer; background: var(--ee-dark); border-color: var(--ee-dark); color: var(--ee-on-dark); font-weight: 700; }}
    button:hover {{ background: var(--ee-accent); border-color: var(--ee-accent); }}
    input:focus-visible, select:focus-visible, button:focus-visible, a:focus-visible {{ outline: 3px solid var(--ee-accent); outline-offset: 2px; }}
    .summary {{ display: flex; justify-content: space-between; gap: 16px; margin: 24px 0 9px; color: var(--ee-muted); font-size: .875rem; }}
    #result-count {{ font-weight: 700; color: var(--ee-text); letter-spacing: .015em; }}
    .event-list {{ list-style: none; margin: 0; padding: 0; background: var(--ee-surface); border: 1px solid var(--ee-border); overflow: hidden; }}
    .event-row {{ display: grid; grid-template-columns: 145px minmax(220px, 1.6fr) minmax(210px, 1fr) minmax(120px, .8fr) 92px; gap: 18px; align-items: start; padding: 14px 18px; border-bottom: 1px solid var(--ee-border); transition: background-color .15s ease; }}
    .event-row:hover {{ background: #f8fafb; }}
    .event-list li:last-child .event-row {{ border-bottom: 0; }}
    .event-date {{ color: var(--ee-text); font-size: .875rem; font-weight: 700; letter-spacing: .01em; white-space: nowrap; }}
    .event-artist {{ min-width: 0; }}
    .event-artist h2 {{ overflow-wrap: anywhere; margin: 0; color: var(--ee-text); font-size: 1.025rem; font-weight: 700; letter-spacing: -.015em; line-height: 1.3; }}
    .openers {{ overflow-wrap: anywhere; margin: 4px 0 0; color: var(--ee-muted); font-size: .86rem; }}
    .venue {{ color: var(--ee-text); overflow-wrap: anywhere; font-weight: 600; }}
    .metadata {{ min-width: 0; color: var(--ee-muted); font-size: .8rem; overflow-wrap: anywhere; }}
    .metadata span {{ display: block; }}
    .promoter {{ margin-top: 3px; }}
    .ticket {{ display: inline-flex; justify-content: center; align-items: center; min-height: 38px; background: var(--ee-accent); color: var(--ee-on-dark); font-size: .82rem; font-weight: 700; letter-spacing: .025em; text-decoration: none; padding: 8px 12px; transition: background-color .17s ease; }}
    .ticket:hover {{ background: var(--ee-accent-hover); color: var(--ee-on-dark); }}
    .ticket-space {{ min-height: 1px; }}
    .no-results {{ margin: 0; padding: 38px 18px; background: var(--ee-surface); border: 1px solid var(--ee-border); text-align: center; color: var(--ee-muted); }}
    [hidden] {{ display: none !important; }}
    @media (max-width: 980px) {{
      .filters {{ grid-template-columns: 1fr 1fr; }}
      .search-control {{ grid-column: 1 / -1; }}
      .event-row {{ grid-template-columns: 125px minmax(180px, 1.5fr) minmax(170px, 1fr) 88px; }}
      .metadata {{ grid-column: 2 / 4; }}
    }}
    @media (max-width: 680px) {{
      main {{ width: min(calc(100% - 30px), var(--ee-wide)); margin-bottom: 54px; }}
      header {{ margin: 0 -15px 24px; padding: 30px 15px 27px; border-bottom-width: 3px; }}
      h1 {{ font-size: clamp(2rem, 10vw, 2.8rem); }}
      .intro {{ font-size: .95rem; }}
      .filters {{ grid-template-columns: 1fr; padding: 14px; }}
      .search-control {{ grid-column: auto; }}
      .summary {{ margin-top: 16px; }}
      .event-list {{ background: transparent; border: 0; overflow: visible; }}
      .event-list li {{ margin-bottom: 10px; }}
      .event-row {{ display: grid; grid-template-columns: 1fr auto; gap: 7px 12px; padding: 15px; background: var(--ee-surface); border: 1px solid var(--ee-border); border-left: 3px solid var(--ee-accent); }}
      .event-date, .event-artist, .venue, .metadata {{ grid-column: 1 / -1; }}
      .metadata {{ display: flex; flex-wrap: wrap; gap: 4px 12px; }}
      .promoter {{ margin-top: 0; }}
      .ticket {{ grid-column: 2; grid-row: 1; min-height: 42px; }}
      .ticket-space {{ display: none; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      input, select, button, .event-row, .ticket {{ transition: none; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Île-de-France Concert Calendar</h1>
      <p class="intro">Upcoming concerts across Paris and Île-de-France.</p>
    </header>
    <section class="filters" aria-label="Concert filters">
      <label class="search-control" for="search">Search
        <input id="search" type="search" placeholder="Artist, opener, venue or town" autocomplete="off">
      </label>
      <label for="month-filter">Date
        <select id="month-filter"><option value="">All dates</option></select>
      </label>
      <label for="venue-filter">Venue
        <select id="venue-filter"><option value="">All venues</option></select>
      </label>
      <label for="genre-filter">Genre
        <select id="genre-filter"><option value="">All genres</option></select>
      </label>
      <label for="sort-order">Sort
        <select id="sort-order">
          <option value="date-asc">Date — soonest first</option>
          <option value="date-desc">Date — latest first</option>
          <option value="artist-asc">Artist — A–Z</option>
          <option value="venue-asc">Venue — A–Z</option>
        </select>
      </label>
      <button id="clear-filters" type="button">Clear</button>
    </section>
    <div class="summary">
      <span id="result-count" aria-live="polite"></span>
    </div>
    <ol id="event-list" class="event-list"></ol>
    <p id="no-results" class="no-results" hidden>No concerts match your current filters.</p>
    <noscript><p class="no-results">JavaScript is required to search and filter this calendar.</p></noscript>
  </main>
  <script id="calendar-data" type="application/json">{event_data}</script>
  <script>
    (function () {{
      "use strict";
      const events = JSON.parse(document.getElementById("calendar-data").textContent);
      const search = document.getElementById("search");
      const monthFilter = document.getElementById("month-filter");
      const venueFilter = document.getElementById("venue-filter");
      const genreFilter = document.getElementById("genre-filter");
      const sortOrder = document.getElementById("sort-order");
      const clearButton = document.getElementById("clear-filters");
      const list = document.getElementById("event-list");
      const count = document.getElementById("result-count");
      const noResults = document.getElementById("no-results");
      const dateFormatter = new Intl.DateTimeFormat("en-GB", {{ weekday: "short", day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }});
      const monthFormatter = new Intl.DateTimeFormat("en-GB", {{ month: "long", year: "numeric", timeZone: "UTC" }});
      const normalize = value => (value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase();
      const dateFromISO = value => {{ const parts = value.split("-").map(Number); return new Date(Date.UTC(parts[0], parts[1] - 1, parts[2])); }};
      const option = (value, label) => {{ const element = document.createElement("option"); element.value = value; element.textContent = label; return element; }};
      const artistSortOverrides = {artist_sort_overrides};
      const venueSortOverrides = {venue_sort_overrides};
      const articleAwareKey = (value, overrides) => overrides[normalize(value)] || normalize(value).replace(/^(?:(?:the|le|la|les)\\s+|l['’]\\s*)/i, "");
      const compareText = (left, right) => left.localeCompare(right, "fr", {{ sensitivity: "base" }});
      const compareDateAscending = (left, right) => compareText(left.d, right.d);
      const compareArtist = (left, right) => compareText(left.a, right.a) || compareDateAscending(left, right) || compareText(left.w, right.w) || left.i - right.i;
      const compareVenue = (left, right) => compareText(left.w, right.w) || compareDateAscending(left, right) || compareText(left.a, right.a) || left.i - right.i;
      const compareDate = (left, right, direction) => direction * compareDateAscending(left, right) || compareText(left.a, right.a) || compareText(left.w, right.w) || left.i - right.i;

      events.forEach((event, index) => {{
        event.i = index;
        event.a = articleAwareKey(event.h, artistSortOverrides);
        event.w = articleAwareKey(event.v, venueSortOverrides);
        event.s = normalize([event.h, ...event.o, event.v, event.c].join(" "));
      }});

      [...new Set(events.map(event => event.d.slice(0, 7)))].forEach(month => {{
        monthFilter.append(option(month, monthFormatter.format(dateFromISO(month + "-01"))));
      }});
      [...new Set(events.map(event => event.v))].sort((a, b) => a.localeCompare(b, "fr", {{ sensitivity: "base" }})).forEach(venue => {{
        venueFilter.append(option(venue, venue));
      }});
      [...new Set(events.flatMap(event => event.x))].sort().forEach(genre => {{
        genreFilter.append(option(genre, genre));
      }});

      function addText(parent, className, text, tagName) {{
        const element = document.createElement(tagName || "div");
        element.className = className;
        element.textContent = text;
        parent.append(element);
        return element;
      }}

      function createRow(event) {{
        const item = document.createElement("li");
        const article = document.createElement("article");
        article.className = "event-row";
        const eventDate = addText(article, "event-date", dateFormatter.format(dateFromISO(event.d)), "time");
        eventDate.dateTime = event.d;
        const artist = document.createElement("div");
        artist.className = "event-artist";
        addText(artist, "", event.h, "h2");
        if (event.o.length) addText(artist, "openers", "with " + event.o.join(", "), "p");
        article.append(artist);
        addText(article, "venue", event.c.toLocaleLowerCase() === "paris" ? event.v : event.v + " (" + event.c + ")");
        const metadata = document.createElement("div");
        metadata.className = "metadata";
        if (event.g) addText(metadata, "genre", event.g, "span");
        if (event.p.length) addText(metadata, "promoter", event.p.join(", "), "span");
        article.append(metadata);
        if (event.t) {{
          const ticket = addText(article, "ticket", "Tickets", "a");
          ticket.href = event.t;
          ticket.target = "_blank";
          ticket.rel = "noopener noreferrer";
          ticket.setAttribute("aria-label", "Tickets for " + event.h);
        }} else {{
          addText(article, "ticket-space", "");
        }}
        item.append(article);
        return item;
      }}

      function render() {{
        const query = normalize(search.value.trim());
        const month = monthFilter.value;
        const venue = venueFilter.value;
        const genre = genreFilter.value;
        const order = sortOrder.value;
        const filtered = events.filter(event => (!query || event.s.includes(query)) && (!month || event.d.startsWith(month)) && (!venue || event.v === venue) && (!genre || event.x.includes(genre)));
        filtered.sort(order === "date-desc" ? (left, right) => compareDate(left, right, -1) : order === "artist-asc" ? compareArtist : order === "venue-asc" ? compareVenue : (left, right) => compareDate(left, right, 1));
        const fragment = document.createDocumentFragment();
        filtered.forEach(event => fragment.append(createRow(event)));
        list.replaceChildren(fragment);
        count.textContent = filtered.length.toLocaleString("en-GB") + (filtered.length === 1 ? " concert" : " concerts");
        list.hidden = filtered.length === 0;
        noResults.hidden = filtered.length !== 0;
      }}

      let scheduled = false;
      function scheduleRender() {{
        if (scheduled) return;
        scheduled = true;
        requestAnimationFrame(() => {{ scheduled = false; render(); }});
      }}
      search.addEventListener("input", scheduleRender);
      [monthFilter, venueFilter, genreFilter, sortOrder].forEach(control => control.addEventListener("change", scheduleRender));
      clearButton.addEventListener("click", () => {{ search.value = ""; monthFilter.value = ""; venueFilter.value = ""; genreFilter.value = ""; render(); search.focus(); }});
      render();
    }})();
  </script>
</body>
</html>
"""


def export_production_calendar(
    events: list[ConcertEvent],
    output_path: str = DEFAULT_OUTPUT_PATH,
    today: date | None = None,
) -> Path:
    upcoming = prepare_upcoming_events(events, today=today)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        build_production_html(upcoming),
        encoding="utf-8",
    )

    print(f"Created production calendar with {len(upcoming)} upcoming concerts")

    return destination
