from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
import re
import shutil
import unicodedata
from urllib.parse import urlparse

from concert_calendar.models import ConcertEvent


DEFAULT_OUTPUT_PATH = "output/production_calendar.html"
DEFAULT_INTEGRATION_DIR = "output/blogger_prototype"
STATIC_DIR = Path(__file__).with_name("static")
RENDERER_PATH = STATIC_DIR / "calendar-renderer.js"
STYLES_PATH = STATIC_DIR / "calendar.css"

ARTIST_SORT_OVERRIDES = {
    "a perfect circle": "Perfect Circle",
    "an pierle": "An Pierlé",
}
VENUE_SORT_OVERRIDES: dict[str, str] = {}

PUBLIC_GENRES = (
    "Comedy",
    "Electronic",
    "Folk / Country",
    "French chanson",
    "Hip-hop / Rap",
    "Jazz / Blues",
    "Metal / Hard Rock",
    "Pop",
    "R&B / Soul / Funk",
    "Reggae / Dub / Ska",
    "Rock / Indie / Punk",
    "World / Latin",
)

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

GENRE_EXACT_MAPPINGS = {
    "rap, hip-hop": "Hip-hop / Rap",
    "hip hop / rap": "Hip-hop / Rap",
    "hard / metal": "Metal / Hard Rock",
    "hard rock et assimiles": "Metal / Hard Rock",
    "hard rock / metal": "Metal / Hard Rock",
    "metal / hard rock": "Metal / Hard Rock",
    "rock / indie / punk": "Rock / Indie / Punk",
    "afrobeat": "World / Latin",
    "afrobeats": "World / Latin",
    "afropop": "World / Latin",
    "afropop, afrobeats, zouk": "World / Latin",
    "variete francaise": "French chanson",
    "chanson francaise": "French chanson",
    "variete / chanson / pop francaise": "French chanson",
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return re.sub(r"\s+", " ", normalized.casefold()).strip()


def alphabetical_sort_key(
    value: str,
    overrides: dict[str, str] | None = None,
) -> str:
    """Return a conservative, article-aware key without changing display text."""

    normalized = normalize_text(value)
    override = (overrides or {}).get(normalized)

    if override is not None:
        return normalize_text(override)

    return re.sub(
        r"^(?:(?:the|a|an|le|la|les)\s+|l['’]\s*)",
        "",
        normalized,
    )


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

    public_by_identity = {
        normalize_text(label): label
        for label in PUBLIC_GENRES
    }

    if normalized in public_by_identity:
        return [public_by_identity[normalized]]

    exact = GENRE_EXACT_MAPPINGS.get(normalized)

    if exact:
        return [exact]

    matches = {
        category
        for category, keywords in GENRE_RULES
        if any(keyword in normalized for keyword in keywords)
    }

    return list(matches) if len(matches) == 1 else []


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
    """Keep current/future events and sort them deterministically."""

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


def serialize_data(value: object) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def read_renderer() -> str:
    return RENDERER_PATH.read_text(encoding="utf-8")


def read_styles() -> str:
    return STYLES_PATH.read_text(encoding="utf-8")


def build_data_asset(events: list[dict]) -> tuple[str, str, str]:
    """Return deterministic filename, SHA-256 digest, and executable data asset."""

    serialized = serialize_data(events)
    asset = (
        "(function(){\n"
        '  "use strict";\n'
        f"  window.ElectricEyeConcertData = Object.freeze({serialized});\n"
        "  document.dispatchEvent(new CustomEvent(\"ee:concert-data-ready\", "
        f"{{detail:{{count:{len(events)}}}}}));\n"
        "}());\n"
    )
    digest = hashlib.sha256(asset.encode("utf-8")).hexdigest()

    return f"calendar-data.{digest[:16]}.js", digest, asset


def build_current_pointer(data_filename: str, digest: str, count: int) -> str:
    manifest = serialize_data(
        {
            "data": data_filename,
            "sha256": digest,
            "count": count,
        }
    )

    return f"""(function(){{
  "use strict";
  var manifest = Object.freeze({manifest});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {{detail:manifest}}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){{
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {{detail:{{reason:"data asset unavailable"}}}}));
  }};
  document.head.appendChild(script);
}}());
"""


def build_fixture_html(load_order: str = "renderer-first") -> str:
    if load_order not in {"renderer-first", "data-first"}:
        raise ValueError(f"Unsupported fixture load order: {load_order}")

    scripts = (
        '<script src="calendar-renderer.js"></script>\n  <script src="calendar-current.js"></script>'
        if load_order == "renderer-first"
        else '<script src="calendar-current.js"></script>\n  <script src="calendar-renderer.js"></script>'
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Electric Eye Calendar Integration Fixture</title>
  <style>
    :root {{ --ee-bg:#edf1f5; --ee-surface:#fff; --ee-dark:#101010; --ee-text:#171717; --ee-text-soft:#454b53; --ee-muted:#6f7782; --ee-border:#d5dbe2; --ee-accent:#d82323; --ee-accent-hover:#b51d1d; --ee-on-dark:#faf8f4; --ee-wide:1680px; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--ee-bg); color:var(--ee-text-soft); font-family:"Instrument Sans",Arial,sans-serif; }}
    .ee-fixture-masthead {{ min-height:90px; display:grid; place-items:center; background:var(--ee-dark); color:var(--ee-on-dark); font-weight:700; letter-spacing:.08em; }}
    .ee-fixture-nav {{ min-height:54px; display:grid; place-items:center; background:var(--ee-dark); color:var(--ee-on-dark); border-top:1px solid #333; }}
    #content-wrapper {{ padding:48px 0 72px; }}
    #content-wrapper > .container {{ width:min(calc(100% - 48px),var(--ee-wide)); margin:0 auto; }}
    #main-wrapper, .item-post, #post-body {{ width:100%; max-width:none; }}
    .item-post {{ background:transparent; border:0; padding:0; }}
    @media (max-width:680px) {{ #content-wrapper {{ padding:34px 0 54px; }} #content-wrapper > .container {{ width:min(calc(100% - 30px),var(--ee-wide)); }} }}
  </style>
  <link rel="stylesheet" href="calendar.css">
</head>
<body class="is-page ee-calendar-page ee-full-width-page" data-fixture-order="{load_order}">
  <header class="ee-fixture-masthead">ELECTRIC EYE</header>
  <nav class="ee-fixture-nav" aria-label="Fixture navigation">Theme-owned navigation</nav>
  <div id="content-wrapper"><div class="container"><main id="main-wrapper"><article class="item-post">
    <div class="post-body entry-content" id="post-body">
      <div id="ee-concert-calendar"><noscript>The concert calendar requires JavaScript.</noscript></div>
    </div>
  </article></main></div></div>
  {scripts}
</body>
</html>
"""


def build_production_html(events: list[dict]) -> str:
    _, _, data_asset = build_data_asset(events)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Île-de-France Concert Calendar</title>
  <style>
    :root {{ --ee-bg:#edf1f5; --ee-surface:#fff; --ee-dark:#101010; --ee-text:#171717; --ee-text-soft:#454b53; --ee-muted:#6f7782; --ee-border:#d5dbe2; --ee-accent:#d82323; --ee-accent-hover:#b51d1d; --ee-on-dark:#faf8f4; }}
    body {{ margin:0; padding:0 24px 72px; background:var(--ee-bg); }}
    #ee-concert-calendar {{ width:min(100%,1500px); margin:0 auto; }}
    @media (max-width:680px) {{ body {{ padding:0 15px 54px; }} }}
{read_styles()}
  </style>
</head>
<body class="ee-calendar-page">
  <main id="ee-concert-calendar"><noscript>The concert calendar requires JavaScript.</noscript></main>
  <script>{data_asset}</script>
  <script>{read_renderer()}</script>
</body>
</html>
"""


def export_integration_prototype(
    events: list[ConcertEvent],
    output_dir: str = DEFAULT_INTEGRATION_DIR,
    today: date | None = None,
) -> dict[str, Path | str | int]:
    upcoming = prepare_upcoming_events(events, today=today)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    filename, digest, data_asset = build_data_asset(upcoming)

    shutil.copyfile(RENDERER_PATH, destination / RENDERER_PATH.name)
    shutil.copyfile(STYLES_PATH, destination / STYLES_PATH.name)
    (destination / filename).write_text(data_asset, encoding="utf-8")
    (destination / "calendar-current.js").write_text(
        build_current_pointer(filename, digest, len(upcoming)),
        encoding="utf-8",
    )
    (destination / "blogger-fixture.html").write_text(
        build_fixture_html("renderer-first"),
        encoding="utf-8",
    )
    (destination / "blogger-fixture-data-first.html").write_text(
        build_fixture_html("data-first"),
        encoding="utf-8",
    )
    (destination / "calendar-current-missing.js").write_text(
        build_current_pointer("missing-calendar-data.js", "0" * 64, 0),
        encoding="utf-8",
    )
    (destination / "blogger-fixture-missing.html").write_text(
        build_fixture_html("renderer-first").replace(
            "calendar-current.js",
            "calendar-current-missing.js",
        ),
        encoding="utf-8",
    )
    (destination / "calendar-malformed.js").write_text(
        'window.ElectricEyeConcertData = {invalid:true};\n'
        'document.dispatchEvent(new CustomEvent("ee:concert-data-ready"));\n',
        encoding="utf-8",
    )
    (destination / "blogger-fixture-malformed.html").write_text(
        build_fixture_html("data-first").replace(
            "calendar-current.js",
            "calendar-malformed.js",
        ),
        encoding="utf-8",
    )

    print(f"Created Blogger integration prototype with {len(upcoming)} upcoming concerts")

    return {
        "directory": destination,
        "renderer": destination / RENDERER_PATH.name,
        "styles": destination / STYLES_PATH.name,
        "data": destination / filename,
        "pointer": destination / "calendar-current.js",
        "fixture": destination / "blogger-fixture.html",
        "data_first_fixture": destination / "blogger-fixture-data-first.html",
        "missing_fixture": destination / "blogger-fixture-missing.html",
        "malformed_fixture": destination / "blogger-fixture-malformed.html",
        "data_filename": filename,
        "sha256": digest,
        "event_count": len(upcoming),
    }


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
