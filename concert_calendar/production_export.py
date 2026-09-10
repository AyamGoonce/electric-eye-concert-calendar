from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
from collections import defaultdict
import html
import json
from pathlib import Path
import re
import shutil
import unicodedata
from urllib.parse import urlparse

from concert_calendar.models import ConcertEvent
from concert_calendar.event_images import repeated_generic_image_urls
from concert_calendar.genres import PUBLIC_GENRES, map_raw_genre, map_raw_genres
from concert_calendar.event_state import canonical_event_identity


DEFAULT_OUTPUT_PATH = "output/production_calendar.html"
DEFAULT_INTEGRATION_DIR = "output/blogger_prototype"
STATIC_DIR = Path(__file__).with_name("static")
RENDERER_PATH = STATIC_DIR / "calendar-renderer.js"
STYLES_PATH = STATIC_DIR / "calendar.css"
SUPPORTING_STATIC_ASSETS = (
    "artist-page.js", "artist-page.css", "artist-autolinker.js", "artist.html",
    "coverage-page.js", "coverage.html",
)

ARTIST_SORT_OVERRIDES = {
    "a perfect circle": "Perfect Circle",
    "an pierle": "An Pierlé",
}
VENUE_SORT_OVERRIDES: dict[str, str] = {}

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


def safe_image_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value)
    lowered = (parsed.path + "?" + parsed.query).casefold()
    if parsed.scheme != "https" or not parsed.netloc:
        return None
    if any(marker in lowered for marker in (
        "tracking", "pixel", "spacer", "placeholder", "default-image",
        "default_image", "logo.", "/logo/", "favicon",
    )):
        return None
    return value


def genre_categories(value: str | None) -> list[str]:
    return map_raw_genres(value)


def _display_subtitle(
    event_title: str | None,
    original: str,
    extracted: str | None,
) -> str | None:
    """
    Prefer an independently supplied event title.

    If event_title merely repeats the raw headliner, use the cleaner
    extracted programme/theme text instead.
    """
    current = (event_title or "").strip()
    extracted = (extracted or "").strip()

    def key(value: str) -> str:
        return " ".join(value.casefold().split())

    if current and key(current) != key(original):
        return current

    return extracted or current or None



def _artist_display_case(name: str) -> str:
    """
    Return canonical public casing for a performer/bill.

    Mixed-case names are preserved. ALL-CAPS source shouting falls back to
    word-initial capitalization unless the artist has an explicitly verified
    display spelling.
    """
    letters = [
        character
        for character in name
        if character.isalpha()
    ]
    is_all_caps = bool(letters) and all(
        not character.islower()
        for character in letters
    )

    if not is_all_caps:
        return name

    # Local import avoids coupling module initialization.
    from concert_calendar.deduplication import (
        VERIFIED_ARTIST_DISPLAY_NAMES,
        normalize_artist_component,
    )

    return VERIFIED_ARTIST_DISPLAY_NAMES.get(
        normalize_artist_component(name),
        name.title(),
    )


def _display_title_parts(event: ConcertEvent) -> tuple[str, str | None]:
    """
    Return performer billing for the main public line and event prose below it.

    This is display normalization only: it does not mutate artist identity or
    invent performers from arbitrary punctuation.
    """
    headliner = (event.headliner or "").strip()
    event_title = event.event_title

    original_headliner = headliner

    # Country/origin tags are metadata, not performer identity.
    country_tag = re.search(
        r"\s+\((?:"
        r"IT|FR|BE|DE|ES|PT|NL|UK|US|USA|CA|AU|JP|"
        r"SE|NO|FI|DK|CH"
        r")\)\s*$",
        headliner,
        re.IGNORECASE,
    )
    if country_tag:
        headliner = headliner[:country_tag.start()].strip()

    # Parenthetical release markers belong to event context.
    release_marker = re.search(
        r"\s+\((?P<context>"
        r"(?:album\s+)?release\s+party|"
        r"launch\s+party|record\s+release"
        r")\)\s*$",
        headliner,
        re.IGNORECASE,
    )
    if release_marker:
        artist = headliner[:release_marker.start()].strip()
        context = release_marker.group("context").strip().title()

        subtitle = _display_subtitle(
            event_title,
            original_headliner,
            context,
        )

        # A richer event_title that merely repeats this same structured
        # bill is not independent programme prose.
        if event_title and event.co_headliners:
            current_key = " ".join(event_title.casefold().split())
            original_key = " ".join(
                original_headliner.casefold().split()
            )
            if current_key.startswith(original_key + " + "):
                subtitle = context

        return artist, subtitle

    # Reversed tribute syntax:
    # "Hommage à X avec Artist A + Artist B"
    reversed_tribute = re.fullmatch(
        r"((?:hommage\s+[àa]|tribute\s+to)\s+.+?)"
        r"\s+(?:avec|with)\s+(.+)",
        headliner,
        re.IGNORECASE,
    )
    if reversed_tribute:
        programme = reversed_tribute.group(1).strip()
        artists = reversed_tribute.group(2).strip()
        return artists, _display_subtitle(
            event_title,
            original_headliner,
            programme,
        )

    # Explicit album/performance title after a separator.
    album_or_live = re.fullmatch(
        r"(.+?)\s+[-–—]\s+("
        r"(?:nouvel\s+album|nouveau\s+album|new\s+album|"
        r"album\s+release|record\s+release)\b.+"
        r"|.+\(\s*live\s*\)\s*"
        r")",
        headliner,
        re.IGNORECASE,
    )
    if album_or_live:
        programme = album_or_live.group(2).strip()
        return (
            album_or_live.group(1).strip(),
            _display_subtitle(
                event_title,
                original_headliner,
                programme,
            ),
        )

    # Artist followed directly by a quoted programme/show title.
    quoted_programme = re.fullmatch(
        r"(.+?)\s+[“«\"]([^”»\"]+)[”»\"]\s*",
        headliner,
    )
    if quoted_programme:
        programme = quoted_programme.group(2).strip()
        words = re.findall(
            r"[A-Za-zÀ-ÖØ-öø-ÿ0-9'’]+",
            programme,
        )
        if len(words) >= 3:
            return (
                quoted_programme.group(1).strip(),
                _display_subtitle(
                    event_title,
                    original_headliner,
                    programme,
                ),
            )

    # Programme syntax such as:
    # "Deadbeat Dubtechno Special: Artist live, Artist live, Artist"
    special_programme = re.fullmatch(
        r"(.+\bspecial)\s*:\s*(.+)",
        headliner,
        re.IGNORECASE,
    )
    if special_programme:
        programme = special_programme.group(1).strip()
        parts = [
            part.strip()
            for part in special_programme.group(2).split(",")
            if part.strip()
        ]
        live_count = sum(
            bool(re.search(r"\s+live\s*$", part, re.IGNORECASE))
            for part in parts
        )

        if len(parts) >= 2 and live_count >= 2:
            artists = " + ".join(
                re.sub(
                    r"\s+live\s*$",
                    "",
                    part,
                    flags=re.IGNORECASE,
                ).strip()
                for part in parts
            )
            return artists, _display_subtitle(
                event_title,
                original_headliner,
                programme,
            )

    # "Series/Promoter presents Artist"
    presentation = re.fullmatch(
        r"(.+?)\s+"
        r"(?:présente|présentent|presente|presentent|presents?|presented\s+by)"
        r"\s+(.+)",
        headliner,
        re.IGNORECASE,
    )
    if presentation:
        programme = presentation.group(1).strip()
        artists = presentation.group(2).strip()
        return artists, _display_subtitle(
            event_title,
            headliner,
            programme,
        )

    # "Release Party [theme] - Artist"
    release_party = re.fullmatch(
        r"((?:(?:album\s+)?release|launch)\s+party\b.*?)"
        r"\s+[-–—:]\s+(.+)",
        headliner,
        re.IGNORECASE,
    )
    if release_party:
        programme = release_party.group(1).strip()
        artists = release_party.group(2).strip()
        return artists, _display_subtitle(
            event_title,
            headliner,
            programme,
        )

    # Programme/series prefix before a colon. A multi-artist RHS is strong
    # evidence that the left side is contextual prose rather than a performer.
    colon = re.fullmatch(r"(.+?)\s*:\s*(.+)", headliner)
    if colon:
        prefix = colon.group(1).strip()
        artists = colon.group(2).strip()

        programme_prefix = bool(re.search(
            r"\b(?:festival|nights?|nuits?|soir[ée]e|showcase|session|"
            r"series|s[ée]rie|programme|program|release\s+party|women|"
            r"présente|présentent|presents?)\b",
            prefix,
            re.IGNORECASE,
        ))
        explicit_bill = bool(re.search(
            r"\s(?:\+|&|/)\s",
            artists,
        ))

        # A richer event_title from the same contextual programme is
        # corroborating source data, not an inferred artist split.
        #
        # Example grammar:
        #   Programme : Artist
        #   Programme : Artist + Artist B + Artist C
        #
        # If both share the same prefix and the fuller RHS explicitly
        # contains the current performer identity, publish that fuller bill.
        richer_bill = None

        if event_title:
            title_colon = re.fullmatch(
                r"(.+?)\s*:\s*(.+)",
                event_title.strip(),
            )

            if title_colon:
                title_prefix = title_colon.group(1).strip()
                title_artists = title_colon.group(2).strip()

                same_prefix = (
                    " ".join(title_prefix.casefold().split())
                    == " ".join(prefix.casefold().split())
                )

                current_artist_key = " ".join(
                    artists.casefold().split()
                )
                title_artist_key = " ".join(
                    title_artists.casefold().split()
                )

                fuller_explicit_bill = bool(re.search(
                    r"\s(?:\+|&|/)\s",
                    title_artists,
                ))

                if (
                    same_prefix
                    and fuller_explicit_bill
                    and current_artist_key
                    and current_artist_key in title_artist_key
                    and len(title_artist_key) > len(current_artist_key)
                ):
                    richer_bill = title_artists

        if programme_prefix or explicit_bill or richer_bill:
            public_artists = richer_bill or artists

            # If event_title was used only to recover the fuller bill,
            # the subtitle should be the contextual prefix rather than
            # repeating the complete raw title.
            if richer_bill:
                subtitle = prefix
            else:
                subtitle = _display_subtitle(
                    event_title,
                    headliner,
                    prefix,
                )

            return public_artists, subtitle

    # Explicit tour / anniversary branding.
    tour = re.fullmatch(
        r"(.+?)\s+[–—:-]\s+"
        r"(.+\b(?:tour|tourn[ée]e|anniversary)\b.*)",
        headliner,
        re.IGNORECASE,
    )
    if tour:
        artists = tour.group(1).strip()
        # Preserve the established public contract: the secondary field keeps
        # the complete original branded title, while the main line contains
        # only the performer identity.
        return artists, event_title or headliner

    # Explicit tribute / performance concepts.
    theme = re.fullmatch(
        r"(.+?)\s+[-–—]\s+"
        r"((?:hommage\s+[àa]|tribute\s+to|live\s+at|live\s+in|"
        r"spectacle\b|show\b).+)",
        headliner,
        re.IGNORECASE,
    )
    if theme:
        artists = theme.group(1).strip()
        programme = theme.group(2).strip()
        return artists, _display_subtitle(
            event_title,
            headliner,
            programme,
        )

    # Editorial en/em-dash followed by unmistakably sentence-like prose.
    # Require at least four words and at least three lower-case-leading words;
    # this deliberately avoids treating ordinary artist/co-bill names as prose.
    editorial = re.fullmatch(
        r"(.+?)\s+[–—]\s+(.+)",
        headliner,
    )
    if editorial:
        artists = editorial.group(1).strip()
        programme = editorial.group(2).strip()
        words = re.findall(
            r"[A-Za-zÀ-ÖØ-öø-ÿ0-9'’]+",
            programme,
        )
        lowercase_leading = sum(
            1
            for word in words
            if word and word[0].islower()
        )

        if len(words) >= 4 and lowercase_leading >= 3:
            return artists, _display_subtitle(
                event_title,
                headliner,
                programme,
            )

    return headliner, event_title

def event_to_data(event: ConcertEvent, rejected_images: set[str] | None = None, public_id: str | None = None) -> dict:
    # Aggregator artwork is not an official event/venue fallback.  DICE remains
    # useful for gap-filling event data, but its images are not published.
    image = (
        None if event.image_source == "DICE" or event.image_url in (rejected_images or set())
        else safe_image_url(event.image_url)
    )
    display_headliner, display_event_title = _display_title_parts(event)
    display_headliner = _artist_display_case(display_headliner)

    display_openers = [
        _artist_display_case(artist)
        for artist in (event.openers or [])
    ]

    # The browser renderer appends every `ch` artist after `h`.
    # If display normalization has already expanded `h` into the complete
    # structured bill, do not publish those same artists again in `ch`.
    display_bill_components = {
        " ".join(part.casefold().split())
        for part in re.split(r"\s+\+\s+", display_headliner)
        if part.strip()
    }

    display_co_headliners = [
        _artist_display_case(artist)
        for artist in (event.co_headliners or [])
        if " ".join(artist.casefold().split())
        not in display_bill_components
    ]

    return {
        "d": event.date[:10],
        "h": display_headliner,
        "o": display_openers,
        **({"ch": display_co_headliners} if display_co_headliners else {}),
        "v": event.venue,
        "c": event.city,
        "x": (
            event.genres_public if event.genres_public else
            [event.genre_public] if event.genre_public else
            ([] if event.genre_evidence is not None or event.festival_name else genre_categories(event.genre))
        ),
        "p": event.promoters or [],
        "t": safe_ticket_url(event.ticket_url),
        "f": bool(event.festival_name),
        "so": bool(event.sold_out),
        "fs": event.first_seen or "1970-01-01T00:00:00Z",
        "i": public_id or getattr(event, "_public_id", None) or canonical_event_identity(event)[:16],
        "ts": event.ticket_status or ("sold_out" if event.sold_out else ("tickets" if safe_ticket_url(event.ticket_url) else None)),
        "st": event.start_time,
        **({"an": event.announced_at} if event.announced_at else {}),
        **({"et": display_event_title} if display_event_title else {}),
        **({"sn": event.series_name} if event.series_name else {}),
        **({"im": image} if image else {}),
        **({"is": event.image_source} if image and event.image_source else {}),
        **({"ee": event.electric_eye_links} if event.electric_eye_links else {}),
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

    upcoming_events = [event for _, event in upcoming]
    rejected_images = repeated_generic_image_urls(upcoming_events)
    base_groups = defaultdict(list)
    for event in upcoming_events:
        base_groups[canonical_event_identity(event)[:16]].append(event)
    assigned = {}
    used_public_ids = set()

    for base, group in base_groups.items():
        ordered = sorted(group, key=lambda event: (
            0 if getattr(event, "_public_id", None) == base else 1,
            event.first_seen or "9999",
            event.start_time or "",
            event.event_title or "",
            event.ticket_url or "",
            event.source_names or [],
        ))

        for index, event in enumerate(ordered):
            preserved = getattr(event, "_public_id", None)

            if preserved and preserved not in used_public_ids:
                public_id = preserved
            elif index == 0 and base not in used_public_ids:
                public_id = base
            else:
                discriminator = "\x1f".join((
                    event.start_time or "",
                    event.event_title or "",
                    event.ticket_url or "",
                    ",".join(event.source_names or []),
                ))
                seed = base + "\x1f" + discriminator
                public_id = hashlib.sha256(
                    seed.encode("utf-8")
                ).hexdigest()[:16]

                salt = 1
                while public_id in used_public_ids:
                    public_id = hashlib.sha256(
                        (seed + "\x1f" + str(salt)).encode("utf-8")
                    ).hexdigest()[:16]
                    salt += 1

            assigned[id(event)] = public_id
            used_public_ids.add(public_id)

    return [
        event_to_data(event, rejected_images, assigned[id(event)])
        for event in upcoming_events
    ]


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


def build_data_asset(
    events: list[dict],
    published_at: str | None = None,
) -> tuple[str, str, str]:
    """Return deterministic filename, SHA-256 digest, and executable data asset."""

    serialized = serialize_data(events)
    published_at = published_at or datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    metadata = serialize_data({"publishedAt": published_at})
    asset = (
        "(function(){\n"
        '  "use strict";\n'
        f"  window.ElectricEyeConcertMeta = Object.freeze({metadata});\n"
        f"  window.ElectricEyeConcertData = Object.freeze({serialized});\n"
        "  document.dispatchEvent(new CustomEvent(\"ee:concert-data-ready\", "
        f"{{detail:{{count:{len(events)}}}}}));\n"
        "}());\n"
    )
    digest = hashlib.sha256(asset.encode("utf-8")).hexdigest()

    return f"calendar-data.{digest[:16]}.js", digest, asset


def build_current_pointer(
    data_filename: str,
    digest: str,
    count: int,
    *,
    published_at: str | None = None,
    state_sha256: str | None = None,
) -> str:
    manifest = serialize_data(
        {
            "data": data_filename,
            "sha256": digest,
            "count": count,
            "publishedAt": published_at or "",
            "state": "calendar-state.json" if state_sha256 else "",
            "stateSha256": state_sha256 or "",
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



def _clean_route_page(*, title: str, canonical: str, mount_id: str, renderer: str) -> str:
    safe_title = html.escape(title)
    safe_canonical = html.escape(canonical, quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{safe_title}</title>
  <link rel="canonical" href="{safe_canonical}">
  <link rel="stylesheet" href="/proof/artist-page.css">
</head>
<body>
  <main id="{mount_id}" class="ee-artist-results" aria-live="polite"></main>
  <script src="/proof/electric-eye-content-current.js"></script>
  <script src="/proof/calendar-current.js"></script>
  <script src="/proof/{renderer}"></script>
</body>
</html>
"""


def _archive_landing_page() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Electric Eye Archive</title>
  <style>
    body{margin:0;background:#fff;color:#15171a;font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    main{max-width:760px;margin:0 auto;padding:72px 24px}
    p:first-child{color:#c62828;font-size:.78rem;font-weight:850;letter-spacing:.15em;text-transform:uppercase}
    h1{font-size:clamp(2.5rem,7vw,5rem);letter-spacing:-.045em;line-height:1;margin:.2em 0}
    p{line-height:1.6}
    nav{display:flex;flex-wrap:wrap;gap:12px;margin-top:32px}
    a{padding:11px 15px;background:#15171a;color:#fff;text-decoration:none}
    a+a{background:#c62828}
  </style>
</head>
<body>
  <main>
    <p>Electric Eye</p>
    <h1>Archive</h1>
    <p>Artist coverage and concert connections from Electric Eye.</p>
    <nav>
      <a href="https://www.electriceyerock.com/">Electric Eye</a>
      <a href="https://www.electriceyerock.com/p/paris-area-concert-calendar.html">Concert Calendar</a>
    </nav>
  </main>
</body>
</html>
"""


def write_clean_routes(
    output_dir: str | Path,
    content_index: dict,
    events: list[dict],
) -> dict[str, int]:
    destination = Path(output_dir)

    for directory_name in ("artist", "concert"):
        directory = destination / directory_name
        if directory.exists():
            shutil.rmtree(directory)

    artist_count = 0
    for slug, artist in content_index["artists"].items():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            continue
        route = destination / "artist" / slug
        route.mkdir(parents=True, exist_ok=True)
        canonical = f"https://archive.electriceyerock.com/artist/{slug}/"
        (route / "index.html").write_text(
            _clean_route_page(
                title=f"{artist['n']} | Electric Eye",
                canonical=canonical,
                mount_id="ee-artist-results",
                renderer="artist-page.js",
            ),
            encoding="utf-8",
        )
        artist_count += 1

    concert_count = 0
    for event in events:
        if not event.get("ee"):
            continue
        event_id = event.get("i", "")
        if not re.fullmatch(r"[0-9a-f]{16}", event_id):
            continue
        route = destination / "concert" / event_id
        route.mkdir(parents=True, exist_ok=True)
        canonical = f"https://archive.electriceyerock.com/concert/{event_id}/"
        (route / "index.html").write_text(
            _clean_route_page(
                title=f"{event['h']} | Electric Eye Concert Coverage",
                canonical=canonical,
                mount_id="ee-coverage-results",
                renderer="coverage-page.js",
            ),
            encoding="utf-8",
        )
        concert_count += 1

    (destination / "index.html").write_text(
        _archive_landing_page(),
        encoding="utf-8",
    )

    return {"artists": artist_count, "concerts": concert_count}


def export_integration_prototype(
    events: list[ConcertEvent],
    output_dir: str = DEFAULT_INTEGRATION_DIR,
    today: date | None = None,
    published_at: str | None = None,
    state_sha256: str | None = None,
) -> dict[str, Path | str | int]:
    upcoming = prepare_upcoming_events(events, today=today)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    filename, digest, data_asset = build_data_asset(upcoming, published_at)

    shutil.copyfile(RENDERER_PATH, destination / RENDERER_PATH.name)
    shutil.copyfile(STYLES_PATH, destination / STYLES_PATH.name)
    for asset_name in SUPPORTING_STATIC_ASSETS:
        shutil.copyfile(STATIC_DIR / asset_name, destination / asset_name)
    (destination / filename).write_text(data_asset, encoding="utf-8")
    (destination / "calendar-current.js").write_text(
        build_current_pointer(
            filename,
            digest,
            len(upcoming),
            published_at=published_at,
            state_sha256=state_sha256,
        ),
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
