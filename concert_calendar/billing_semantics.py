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
                # The referenced artist in a tribute production is context,
                # not performer identity.  A title-level performer connector
                # is required before description prose may name another act.
                if re.search(r"\b(?:tribute|hommage)\b", value, re.I) and not re.search(
                    r"\b(?:avec|with|feat\.?|ft\.?)\s+" + re.escape(artist) + r"(?=\W|$)",
                    value,
                    re.I,
                ):
                    return value
                return artist

    return value

def _retain_original(event, original):
    event.raw_title = event.raw_title or original
    event.identity_aliases = _stable_unique([*(event.identity_aliases or []), original])


# A fully quoted, explicitly marked tour label belongs to the programme,
# not the performing artist. Other quoted album titles/project names stay opaque.
QUOTED_TOUR_SUFFIX_RE = re.compile(
    r'^(?P<artist>.+?)\s+'
    r'(?:"(?P<straight>[^"]+)"|“(?P<curly>[^”]+)”|«\s*(?P<french>[^»]+?)\s*»)'
    r'\s*$'
)


def quoted_tour_title_parts(value: str) -> tuple[str, str] | None:
    match = QUOTED_TOUR_SUFFIX_RE.fullmatch(_clean(value))
    if not match:
        return None
    artist = _clean(match.group("artist"))
    title = _clean(match.group("straight") or match.group("curly") or match.group("french"))
    if not artist or not re.search(
        r"\b(?:tour|tournée|tournee)\b", title, re.IGNORECASE
    ):
        return None
    return artist, title


def explicit_title_role_context(event: ConcertEvent) -> bool:
    """Normalize marked support, release and exact-venue prose only.

    No inference from '+' or '&' characters; a source must explicitly label
    the support role, an artist-specific release, or its own venue suffix.
    """
    title = _clean(event.headliner)
    support = re.fullmatch(
        r"(?P<artist>.+?)\s*\(\s*(?:premi[èe]re\s+partie|"
        r"1(?:[èe]re|re|ere)\s+partie|opening\s+act|support\s+act)"
        r"\s*:\s*(?P<support>[^()]+)\s*\)",
        title, re.IGNORECASE,
    )
    if support:
        artist = _clean(support.group("artist"))
        guest = _clean(support.group("support"))
        if artist and guest:
            _retain_original(event, title)
            event.headliner = artist
            event.openers = _stable_unique([*(event.openers or []), guest])
            return True

    # "Artist à Venue": compare against this record's independently supplied
    # venue identity. Never strip a location from an arbitrary artist title.
    venue = _clean(event.venue)
    match = re.fullmatch(r"(?P<artist>.+?)\s+[àa]\s+(?P<location>.+)", title, re.I)
    if match and venue:
        from concert_calendar.venues import normalize_venue_key
        # Venue keys accept official aliases, not merely substring matches.
        if normalize_venue_key(match.group("location")) == normalize_venue_key(venue):
            artist = _clean(match.group("artist"))
            if artist:
                _retain_original(event, title)
                event.headliner = artist
                return True

    release = re.fullmatch(
        r"(?P<artist>.+?)\s+[–—-]\s+"
        r"(?P<context>(?:album\s+)?release\s+party\b.+)",
        title, re.IGNORECASE,
    )
    if release and _clean(release.group("artist")):
        _retain_original(event, title)
        event.headliner = _clean(release.group("artist"))
        event.event_title = event.event_title or _clean(release.group("context"))
        return True
    return False


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

    explicit_title_role_context(event)
    # Source listing stamps such as "Artist I 14.11.26" identify the
    # already-known event date. Require equality with that event's date.
    listing_date = re.fullmatch(
        r"(?P<artist>.+?)\s+(?:I|\|)\s+"
        r"(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{2}|\d{4})",
        _clean(event.headliner),
    )
    if listing_date:
        year = listing_date.group("year")
        if len(year) == 2:
            year = "20" + year
        candidate_date = (
            f"{int(year):04d}-{int(listing_date.group('month')):02d}-"
            f"{int(listing_date.group('day')):02d}"
        )
        if candidate_date == event.date[:10]:
            _retain_original(event, event.headliner)
            event.headliner = listing_date.group("artist").strip()

    original = event.headliner
    primary = _evidenced_headliner(event)
    if primary != original:
        _retain_original(event, original)
        event.headliner = primary
        context = PERFORMANCE_LABEL_RE.sub("", event.event_title or original).strip()
        if re.match(r"(?:hommage\s+[àa]|tribute\s+to)\b", context, re.I):
            context = re.sub(r"\s+(?:avec|with)\s+" + re.escape(primary) + r"(?=\s|$)", "", context, flags=re.I)
        event.event_title = context if _key(context) != _key(primary) else None
    # The quotation marks delimit an explicit tour designation, unlike
    # arbitrary punctuation or a quoted album/project name.
    quoted_tour = quoted_tour_title_parts(event.headliner)
    if quoted_tour:
        artist, tour_title = quoted_tour
        _retain_original(event, event.headliner)
        event.headliner = artist
        event.event_title = event.event_title or tour_title

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

    # A labelled open-stage programme is not the first musician.
    open_stage = None if reviewed_wrapper_lock else re.fullmatch(
        r"(?P<series>sc[èe]ne\s+ouverte)\s*\+\s*(?P<billing>.+)",
        value, re.IGNORECASE,
    )
    if open_stage:
        _retain_original(event, value)
        event.event_title = event.event_title or open_stage.group("series")
        event.headliner = open_stage.group("billing").strip()
        value = event.headliner

    # "Series/Promoter presents Artist"
    presentation = None if reviewed_wrapper_lock else re.fullmatch(
        r"(?P<context>.+?)\s+"
        r"(?:(?:présente|présentent|presente|presentent)\s*:?\s+|"
        r"presents?\s+)"
        r"(?P<artist>.+)",
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

    # Branded promoters explicitly inviting named acts are presenting a
    # programme, not performing under the entire ticketing headline.
    # No unlabelled generic 'Artist invites Artist' construction is touched.
    invitation = None if reviewed_wrapper_lock else re.fullmatch(
        r"(?P<brand>.+?)\s+invites?\s*:?[ \t]+(?P<guests>.+)",
        value, re.IGNORECASE,
    )
    if invitation and re.search(
        r"\b(?:music|records?|concerts?|clubs?|collectif|festival|label|soir[ée]e)\b",
        invitation.group("brand"), re.IGNORECASE,
    ):
        branded_guests = [
            _clean(name) for name in re.split(
                r"\s*,\s*|\s+b2b\s+", invitation.group("guests"),
                flags=re.IGNORECASE,
            )
        ]
        if 2 <= len(branded_guests) <= 8 and all(
            name and 2 <= len(name) <= 75
            and not re.search(r"\b(?:guest|tba|surprise)\b", name, re.I)
            for name in branded_guests
        ):
            _retain_original(event, value)
            event.event_title = event.event_title or invitation.group("brand").strip()
            event.headliner = branded_guests[0]
            event.performers = _stable_unique(branded_guests)
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

    # A tribute descriptor such as "Strangelove - The Depeche Mode
    # Experience" is programme context, not part of the act's identity.
    experience = None if reviewed_wrapper_lock else re.fullmatch(
        r"(?P<artist>.+?)\s+[–—-]\s+"
        r"(?P<context>The\s+.+\s+(?:Experience|Tribute|Show))",
        value, re.IGNORECASE,
    )
    if experience and _clean(experience.group("artist")):
        _retain_original(event, value)
        event.headliner = experience.group("artist").strip()
        event.event_title = event.event_title or experience.group("context").strip()
        value = event.headliner

    # A terminal release label explicitly assigns the release to the artist
    # before it.  Keep bills with trailing '+ ARTIST' opaque: that would need
    # independent role evidence from the source.
    release_suffix = None if reviewed_wrapper_lock else re.fullmatch(
        r"(?P<artist>.+?)\s+"
        r"(?P<context>(?:(?:album\s+)?release|launch)\s+party"
        r"(?:\s+(?:[IVX]+|\d+|[\"“«][^\"”»]+[\"”»]))?)\s*",
        value,
        re.IGNORECASE,
    )
    if release_suffix:
        _retain_original(event, value)
        event.headliner = release_suffix.group("artist").strip()
        event.event_title = event.event_title or value
        value = event.headliner

    # Source-marked release/country metadata: not a general punctuation split.
    # An explicitly labelled, delimited tour suffix is contextual wording,
    # not an artist. Arbitrary hyphenated subtitles remain untouched.
    tour = re.fullmatch(
        r"(?P<artist>.+?)(?:\s+[–—-]\s+|\s*:\s*)"
        r"(?P<context>.+\btour)\s*",
        value,
        re.I,
    )
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


# Only explicitly labelled CURRENT musical credits are performer evidence.
# Unlabelled prose, influences and songs mentioned in a programme are not.
MUSIC_CREDIT_RE = re.compile(
    r"^(?:piano|chant|voix|vocals?|guitare|guitar|basse|bass|"
    r"batterie|drums?|violon|violin|saxophone|trompette|trumpet)"
    r"\s*[:–—-]?\s+"
    r"(?P<name>[A-ZÀ-ÖØ-Ý][\wÀ-ÖØ-öø-ÿ'’.-]+"
    r"(?:\s+[A-ZÀ-ÖØ-Ý][\wÀ-ÖØ-öø-ÿ'’.-]+){1,4})"
    r"\s*$",
    re.IGNORECASE,
)


def performers_from_explicit_music_credits(description: str | None) -> list[str]:
    """Recognize independently labelled musician credits, not descriptive prose."""
    artists = []
    for raw_line in (description or "").splitlines():
        line = _clean(raw_line).strip("•*- ")
        match = MUSIC_CREDIT_RE.fullmatch(line)
        if match:
            artists.append(match.group("name"))
    # One isolated name is insufficient to reinterpret an opaque show title.
    return _stable_unique(artists) if len(_stable_unique(artists)) >= 2 else []


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
        # Some upstream records repeat their complete raw *event title* as a
        # single 'performer'. That is not independent artist metadata. Do not
        # allow it to reverse a verified title-wrapper correction above.
        if (
            len(performers) == 1
            and event.raw_title
            and _key(performers[0]) == _key(event.raw_title)
            and _key(event.headliner) != _key(event.raw_title)
        ):
            performers = [event.headliner]
        if not performers and event.description:
            performers = performers_from_explicit_music_credits(event.description)
            if performers and not event.event_title:
                event.event_title = event.raw_title or event.headliner

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
