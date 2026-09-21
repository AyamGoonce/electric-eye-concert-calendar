import re
import unicodedata
from html import unescape

from concert_calendar.models import ConcertEvent


PERFORMANCE_LABEL_RE = re.compile(
    r"\s+[–—-]\s*"
    r"(?P<hour>[01]?\d|2[0-3])"
    r"\s*h\s*"
    r"(?P<minute>[0-5]\d)?"
    r"\s*$",
    re.IGNORECASE,
)


def _clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", unescape(value or "")).strip()


def _key(value: str | None) -> str:
    return unicodedata.normalize("NFC", _clean(value)).casefold()


def _stable_unique(values):
    result = []
    seen = set()

    for value in values:
        cleaned = _clean(value)
        identity = _key(cleaned)

        if not identity or identity in seen:
            continue

        seen.add(identity)
        result.append(cleaned)

    return result


EXPLICIT_DESCRIPTION_PERFORMER_RE = re.compile(
    r"\b(?:anim[eé]e?|men[eé]e?|dirig[eé]e?)"
    r"\s+par\s+"
    r"(?P<artist>"
    r"[A-ZÀ-ÖØ-Ý][\wÀ-ÖØ-öø-ÿ'’.-]+"
    r"(?:\s+[A-ZÀ-ÖØ-Ý][\wÀ-ÖØ-öø-ÿ'’.-]+){0,5}"
    r")",
)


def _evidenced_headliner(event: ConcertEvent) -> str:
    """
    Resolve source performer evidence for canonical pre-dedup semantics.

    Independently worded source description evidence may identify the actual
    performer behind a programme/show title. The extracted name must also
    occur in that title; description prose alone cannot replace billing.
    """
    value = _clean(event.headliner)

    match = PERFORMANCE_LABEL_RE.search(value)

    if match and event.start_time:
        parsed_time = (
            f"{int(match.group('hour')):02d}:{match.group('minute') or '00'}"
        )

        if parsed_time == event.start_time:
            value = value[:match.start()].strip() or value

    description = _clean(event.description)

    if description and re.search(r"\b(?:hommage|tribute|jam|programme)\b", value, re.I):
        performer_match = EXPLICIT_DESCRIPTION_PERFORMER_RE.search(
            description
        )

        if performer_match:
            artist = _clean(
                performer_match.group("artist")
            ).rstrip(".,;:!?")

            if (
                artist
                and artist.casefold() in value.casefold()
            ):
                return artist

    return value

def _retain_original(event, original):
    event.raw_title = event.raw_title or original
    event.identity_aliases = _stable_unique([*(event.identity_aliases or []), original])


def normalize_event_semantics(event):
    """Resolve explicit source semantics before dedup, content and state."""
    # A reviewed event-scoped title may explicitly preserve wording that
    # resembles one of the strong wrapper grammars added below.  This lock
    # applies only to those wrappers; existing tour, time and metadata
    # semantics must continue to run normally.
    reviewed_wrapper_lock = getattr(
        event,
        "_reviewed_wrapper_semantics_locked",
        False,
    )

    original = event.headliner
    primary = _evidenced_headliner(event)
    if primary != original:
        _retain_original(event, original)
        event.headliner = primary
        context = PERFORMANCE_LABEL_RE.sub("", event.event_title or original).strip()
        if re.match(r"(?:hommage\s+[àa]|tribute\s+to)\b", context, re.I):
            context = re.sub(r"\s+(?:avec|with)\s+" + re.escape(primary) + r"(?=\s|$)", "", context, flags=re.I)
        event.event_title = context if _key(context) != _key(primary) else None
    # Strong grammatical wrappers are source semantics, not punctuation guesses.
    value = event.headliner

    # Terminal unnamed guest wording is presentation copy, not artist identity.
    # A named guest is deliberately untouched because the pattern must end here.
    unnamed_special_guest = (
        None
        if reviewed_wrapper_lock
        else re.fullmatch(
            r"(?P<artist>.+?)\s+with\s+(?:very\s+)?special\s+guests?\s*",
            value,
            re.IGNORECASE,
        )
    )
    if unnamed_special_guest:
        original = value
        _retain_original(event, original)
        event.headliner = unnamed_special_guest.group("artist").strip()
        event.event_title = event.event_title or original
        value = event.headliner

    # "Series/Promoter presents Artist"
    presentation = None if reviewed_wrapper_lock else re.fullmatch(
        r"(?P<context>.+?)\s+"
        r"(?:présente|présentent|presente|presentent|presents?)"
        r"\s+(?P<artist>.+)",
        value,
        re.IGNORECASE,
    )
    if presentation:
        _retain_original(event, value)
        event.headliner = presentation.group("artist").strip()
        event.event_title = (
            event.event_title or presentation.group("context").strip()
        )
        value = event.headliner

    # "Release Party [theme] - Artist"
    release_party = None if reviewed_wrapper_lock else re.fullmatch(
        r"(?P<context>(?:(?:album\s+)?release|launch)\s+party\b.*?)"
        r"\s+[-–—:]\s+(?P<artist>.+)",
        value,
        re.IGNORECASE,
    )
    if release_party:
        _retain_original(event, value)
        event.headliner = release_party.group("artist").strip()
        event.event_title = (
            event.event_title or release_party.group("context").strip()
        )
        value = event.headliner

    # Explicit album-release wording after a separator is programme context.
    album_context = None if reviewed_wrapper_lock else re.fullmatch(
        r"(?P<artist>.+?)\s+[-–—]\s+"
        r"(?P<context>(?:nouvel\s+album|nouveau\s+album|new\s+album|"
        r"album\s+release|record\s+release)\b.+)",
        value,
        re.IGNORECASE,
    )
    if album_context:
        _retain_original(event, value)
        event.headliner = album_context.group("artist").strip()
        event.event_title = (
            event.event_title or album_context.group("context").strip()
        )
        value = event.headliner

    # Source-marked release/country metadata: not a general punctuation split.
    # An explicitly labelled, delimited tour suffix is contextual wording,
    # not an artist. Arbitrary hyphenated subtitles remain untouched.
    tour = re.fullmatch(r"(?P<artist>.+?)\s+[–—-]\s+(?P<context>.+\btour)\s*", value, re.I)
    if tour:
        _retain_original(event, value)
        event.headliner = tour['artist'].strip()
        event.event_title = event.event_title or value
        value = event.headliner
    metadata = re.search(r"\s+\((?P<label>(?:album\s+)?release\s+party|launch\s+party|record\s+release|IT|FR|BE|DE|ES|PT|NL|UK|US|USA|CA|AU|JP|SE|NO|FI|DK|CH)\)\s*$", value, re.I)
    if metadata:
        _retain_original(event, value)
        event.headliner = value[:metadata.start()].strip()
        if " " in metadata['label']:
            event.event_title = metadata['label'].title()


def apply_structured_performer_semantics(
    events: list[ConcertEvent],
) -> None:
    """
    Promote explicit source-provided performer metadata into calendar billing.

    This function never splits a title on punctuation. A scraper must already
    have supplied event.performers from independent source evidence.
    """
    for event in events:
        normalize_event_semantics(event)
        performers = _stable_unique(event.performers or [])

        if not performers:
            continue

        event.performers = performers
        headliner_key = _key(event.headliner)

        matching_primary = next(
            (
                performer
                for performer in performers
                if _key(performer) == headliner_key
            ),
            None,
        )

        primary = matching_primary or performers[0]

        if _key(event.headliner) != _key(primary):
            original_headliner = event.headliner
            _retain_original(event, original_headliner)

        event.headliner = primary

        opener_keys = {
            _key(opener)
            for opener in (event.openers or [])
            if _key(opener)
        }

        co_headliners = _stable_unique([
            *(event.co_headliners or []),
            *[
                performer
                for performer in performers
                if (
                    _key(performer) != _key(primary)
                    and _key(performer) not in opener_keys
                )
            ],
        ])

        event.co_headliners = co_headliners or None
