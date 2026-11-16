from __future__ import annotations

from collections import Counter, defaultdict
from html import unescape
import json
from pathlib import Path
import re
import unicodedata

from concert_calendar.models import ConcertEvent


BILLING_REVIEWS_PATH = Path(__file__).with_name("calendar_artist_billings.json")
IDENTITY_OVERRIDES_PATH = Path(__file__).with_name("artist_identity_overrides.json")
CONCERT_ASSOCIATIONS_PATH = Path(__file__).with_name("concert_review_associations.json")
AUTOMATIC_THRESHOLD = 90

PRESENTER_RE = re.compile(
    r"^(?P<presenter>.+?)\s+(?:presents?|presented\s+by|présente|"
    r"présentent|presente|presentent)\s*:\s*(?P<billing>.+)$",
    re.IGNORECASE,
)
CONTEXT_RE = re.compile(
    r"\b(?:hommage\s+[àa]|tribute\s+to|performing|plays?|feat\.?|"
    r"release\s+party|album\s+release|tour\b|festival|session|jam\b)\b",
    re.IGNORECASE,
)
GENERIC_PART_RE = re.compile(
    r"^(?:guest|guests|special guest|special guests|invité|invitée|invités|"
    r"invitées|1(?:re|ère) partie|première partie|tba|tbc|@)$",
    re.I,
)


def _clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", unescape(value or "")).strip()


def _key(value: str | None) -> str:
    value = unicodedata.normalize("NFKD", _clean(value)).casefold()
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("’", "'")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _stable_unique(values) -> list[str]:
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


def load_billing_reviews(path: Path = BILLING_REVIEWS_PATH) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != 1:
        raise ValueError("Unsupported calendar artist billing schema")
    return payload


def load_artist_identity_evidence() -> dict[str, str]:
    """Return deterministic reviewed Electric Eye identities and aliases."""
    overrides = json.loads(IDENTITY_OVERRIDES_PATH.read_text(encoding="utf-8"))
    associations = json.loads(CONCERT_ASSOCIATIONS_PATH.read_text(encoding="utf-8"))
    canonical = {}

    def add(name, display=None):
        identity = _key(name)
        if identity:
            canonical.setdefault(identity, _clean(display or name))

    for name in (overrides.get("artists") or {}):
        add(name)
    for name in (overrides.get("manualArticleAssociations") or {}):
        add(name)
    for names in (associations.get("associations") or {}).values():
        for name in names or []:
            add(name)
    for alias, target in (overrides.get("aliases") or {}).items():
        target_name = canonical.get(_key(target), _clean(target))
        add(target_name)
        canonical[_key(alias)] = target_name
    return canonical


def identity_catalog_from_content_index(index: dict) -> dict[str, str]:
    """Build an exact canonical/alias lookup from an existing content index."""
    catalog = load_artist_identity_evidence()
    for artist in (index.get("artists") or {}).values():
        canonical = _clean(artist.get("n"))
        if not canonical:
            continue
        catalog[_key(canonical)] = canonical
        for alias in artist.get("al") or []:
            if _key(alias):
                catalog[_key(alias)] = canonical
    return catalog


def _looks_like_flat_billing(value: str) -> bool:
    """Exclude apparent multi-act bills from standalone evidence."""
    return bool(re.search(
        r"\s+(?:\+|/|•|&|et|x|×|vs\.?|with|avec|ft\.?|feat\.?|featuring|[–—])\s+",
        value, re.I,
    ))


def current_official_standalone_artist_evidence(events: list[ConcertEvent]) -> dict[str, str]:
    """Use standalone artists explicitly billed by official venues this run.

    This is an additional identity catalog, not a punctuation parser.
    It never promotes titles with bill separators, series/event descriptions,
    or headliners that disagree with structured source performer identities.
    """
    from concert_calendar.venues import normalize_venue_key
    trusted = {}
    for event in events:
        name = _clean(event.headliner)
        if (
            not name
            or _looks_like_flat_billing(name)
            or re.search(r"\b(?:release\s+party|premi[èe]re\s+partie|festival)\b", name, re.I)
            or event.event_title and _key(event.event_title) == _key(name)
            or event.performers and any(_key(artist) != _key(name) for artist in event.performers)
        ):
            continue
        venue = normalize_venue_key(event.venue)
        if not venue or not any(
            normalize_venue_key(source) == venue for source in (event.source_names or [])
        ):
            continue
        trusted.setdefault(_key(name), name)
    return trusted


def current_structured_standalone_artist_evidence(events: list[ConcertEvent]) -> dict[str, str]:
    """Include independently named single artists from source performer fields.

    These names are supplied as individual identities by ticketing/venue
    sources, not guessed from separators. The complete billing still takes
    precedence if it is itself a known artist identity.
    """
    trusted = {}
    for event in events:
        names = _stable_unique(event.performers or [])
        if len(names) != 1 or _key(names[0]) != _key(event.headliner):
            continue
        name = names[0]
        if (
            not event.source_names
            or _looks_like_flat_billing(name)
            or re.search(r"\b(?:release party|festival|concert|programme)\b", name, re.I)
        ):
            continue
        trusted.setdefault(_key(name), name)
    return trusted


def _review_lookups(reviews: dict) -> tuple[dict, dict, dict]:
    canonical = {}
    for name, item in (reviews.get("canonicalIdentities") or {}).items():
        for value in [name, *((item or {}).get("aliases") or [])]:
            identity = _key(value)
            if identity:
                canonical[identity] = name
    billings = {
        _key(name): item for name, item in (reviews.get("reviewedBillings") or {}).items()
        if _key(name)
    }
    descriptions = {
        _key(name): item for name, item in (reviews.get("reviewedDescriptions") or {}).items()
        if _key(name)
    }
    return canonical, billings, descriptions


def _split_spaced_plus(value: str) -> list[str]:
    """Split spaced plus signs outside parentheses; never split bare `+`."""
    parts = []
    start = 0
    depth = 0
    for match in re.finditer(r"\s+\+\s+", value or ""):
        segment = value[start:match.start()]
        depth += segment.count("(") - segment.count(")")
        if depth == 0:
            parts.append(segment.strip())
            start = match.end()
    if parts:
        parts.append(value[start:].strip())
    return parts


def _exact_catalog_bill_candidates(value: str, identities: dict[str, str]) -> list[str]:
    """Resolve uniquely partitioned bills, with every member independently known.

    Delimiters are only candidate boundaries. A complete artist identity wins
    (e.g. Earth, Wind & Fire). Mixed separators are accepted only if exactly
    one partition of the entire billing matches the established catalogue.
    """
    title = _clean(value)
    if not title or _key(title) in identities:
        return []

    separators = list(re.finditer(
        r"\s+(?:\+|/|•|&|et|[–—-])\s+", title, flags=re.I
    ))
    if not separators or len(separators) > 8:
        return []

    # Each partition joins consecutive chunks back with their original
    # punctuation, so legitimate artist names containing '&' stay intact.
    chunks = []
    cursor = 0
    for match in separators:
        chunks.append(title[cursor:match.start()])
        cursor = match.end()
    chunks.append(title[cursor:])
    separators_text = [match.group(0) for match in separators]
    solutions = []

    def visit(position: int, chosen: list[str]) -> None:
        if len(solutions) > 1:
            return
        if position == len(chunks):
            if len(chosen) >= 2 and len(set(map(_key, chosen))) == len(chosen):
                solutions.append(chosen)
            return
        for stop in range(position + 1, len(chunks) + 1):
            component = chunks[position]
            for index in range(position, stop - 1):
                component += separators_text[index] + chunks[index + 1]
            component = _clean(component)
            if not _valid_parts([component, "placeholder"]):
                continue
            canonical = identities.get(_key(component))
            if canonical:
                visit(stop, [*chosen, canonical])

    visit(0, [])
    return solutions[0] if len(solutions) == 1 else []


def _valid_parts(parts: list[str]) -> bool:
    if len(parts) < 2:
        return False
    return all(
        _key(part)
        and len(_key(part)) >= 2
        and "+" not in part
        and not GENERIC_PART_RE.fullmatch(_clean(part))
        and part.count("(") == part.count(")")
        for part in parts
    )


def _set_resolution(
    event: ConcertEvent,
    artists: list[str],
    *,
    method: str,
    confidence: int,
    evidence: list[str],
    presenter: str | None = None,
    description: str | None = None,
    preserve_roles: bool = False,
) -> None:
    original = _clean(event.headliner)
    artists = _stable_unique(artists)
    event.raw_title = event.raw_title or original
    event.identity_aliases = _stable_unique([*(event.identity_aliases or []), original]) or None
    event.headliner = artists[0]
    if not preserve_roles:
        # A source-verified opener must not be silently promoted to
        # co-headliner when the same act also appears in a flat bill.
        opener_keys = {_key(name) for name in (event.openers or [])}
        event.co_headliners = _stable_unique(
            [*(event.co_headliners or []),
             *(name for name in artists[1:] if _key(name) not in opener_keys)]
        ) or None
    event.performers = artists
    if presenter:
        event.promoters = _stable_unique([*(event.promoters or []), presenter]) or None
    if description:
        event.event_title = event.event_title or description
    event._billing_resolution = {
        "original": original,
        "artists": artists,
        "method": method,
        "confidence": confidence,
        "evidence": evidence,
        **({"presenter": presenter} if presenter else {}),
        **({"description": description} if description else {}),
    }


def _source_profile(event: ConcertEvent, profiles: dict) -> tuple[str, dict] | None:
    for source in event.source_names or []:
        if source in profiles:
            return source, profiles[source] or {}
    return None


def _profile_candidate(
    value: str,
    profile: dict,
) -> tuple[str, list[str], str | None, str | None]:
    presenter = None
    description = None
    billing = _clean(value)
    if profile.get("presenterPrefix"):
        match = PRESENTER_RE.fullmatch(billing)
        if match:
            presenter = _clean(match.group("presenter"))
            billing = _clean(match.group("billing"))
    for pattern in profile.get("showTitleSuffixPatterns") or []:
        match = re.search(pattern, billing, re.IGNORECASE)
        if match and match.start() > 0:
            description = _clean(match.group(0))
            billing = _clean(billing[:match.start()])
            break
    candidate_plus = profile.get("candidateSpacedPlus") or profile.get("spacedPlus")
    return (
        billing,
        _split_spaced_plus(billing) if candidate_plus else [],
        presenter,
        description,
    )


def _same_event_groups(events: list[ConcertEvent]):
    groups = defaultdict(list)
    for event in events:
        groups[(event.date[:10], _key(event.venue))].append(event)
    return groups


def _billing_matches_roster(billing: str, artists: list[str]) -> bool:
    """Verify that the complete displayed bill matches every roster member."""
    if len(artists) < 2:
        return False
    separator = r"\s+(?:\+|/|•|&|et|[–—-])\s+"
    pattern = "^" + separator.join(
        re.escape(name).replace(r"\ ", r"\s+") for name in artists
    ) + "$"
    return re.fullmatch(pattern, _clean(billing), re.IGNORECASE) is not None


def _cross_source_artists(
    event: ConcertEvent,
    group: list[ConcertEvent],
    billing: str,
) -> tuple[list[str], list[str]]:
    """Accept independent roster evidence only for the *entire* billing."""
    event_sources = set(event.source_names or [])
    for candidate in group:
        if candidate is event:
            continue
        if event_sources and set(candidate.source_names or []) == event_sources:
            continue
        # Different stated start times can indicate different performances.
        # Keep those records untouched for the later dedicated time/venue
        # reconciler, which applies source-authority rules.
        if (
            event.start_time and candidate.start_time
            and event.start_time != candidate.start_time
        ):
            continue

        # A second source can corroborate the complete bill in either its
        # independently supplied performer array or explicit event roles.
        # Never treat another source's unsplit headline as role evidence.
        rosters = [_stable_unique(candidate.performers or [])]
        if (
            candidate.headliner
            and not _looks_like_flat_billing(candidate.headliner)
            and (candidate.co_headliners or candidate.openers)
        ):
            rosters.append(_stable_unique([
                candidate.headliner,
                *(candidate.co_headliners or []),
                *(candidate.openers or []),
            ]))
        for artists in rosters:
            if (
                _billing_matches_roster(billing, artists)
                and all(not GENERIC_PART_RE.fullmatch(name) for name in artists)
            ):
                return artists, _stable_unique(candidate.openers or [])
    return [], []


def _same_source_evidence(event: ConcertEvent, billing: str) -> tuple[list[str], list[str]]:
    """Return a bill supported by per-record source structure, never punctuation alone."""
    supplied = getattr(event, "_billing_evidence", None) or {}
    supplied_artists = _stable_unique(supplied.get("artists") or [])
    if (
        len(supplied_artists) >= 2
        and int(supplied.get("confidence") or 0) >= 95
        # A flat bill with recognized separators must account for *every*
        # listed act, even when the provider also sends a separate roster.
        and (
            not re.search(r"\s+(?:\+|/|•|&|et|[–—-])\s+", billing, re.I)
            or _billing_matches_roster(billing, supplied_artists)
        )
    ):
        return supplied_artists, list(
            supplied.get("evidence") or ["source supplied per-record billing evidence"]
        )

    parts = _split_spaced_plus(billing)
    if not _valid_parts(parts):
        return [], []
    role_names = {
        _key(name)
        for name in [*(event.openers or []), *(event.co_headliners or [])]
        if _key(name)
    }
    if role_names and all(_key(part) in role_names for part in parts[1:]):
        return parts, ["source supplied separate current-event roles for every trailing billing constituent"]
    return [], []


def _apply_profile_context(
    event: ConcertEvent,
    original: str,
    billing: str,
    presenter: str | None,
    description: str | None,
) -> None:
    """Apply deterministic wrapper semantics without asserting artist boundaries."""
    if billing != original:
        event.raw_title = event.raw_title or original
        event.identity_aliases = _stable_unique(
            [*(event.identity_aliases or []), original]
        ) or None
        event.headliner = billing
    if presenter:
        event.promoters = _stable_unique([*(event.promoters or []), presenter]) or None
    if description:
        event.event_title = event.event_title or description


def _record(diagnostics: dict, event: ConcertEvent) -> None:
    resolution = getattr(event, "_billing_resolution", None)
    if resolution:
        diagnostics.setdefault("records", []).append({
            **resolution,
            "date": event.date[:10],
            "venue": event.venue,
            "sources": list(event.source_names or []),
        })


def resolve_artist_billings(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
    *,
    reviews: dict | None = None,
    identity_catalog: dict[str, str] | None = None,
    external_evidence: dict[str, dict] | None = None,
    allow_inference: bool = True,
) -> None:
    """Resolve flat billings using explicit evidence and an auditable score."""
    reviews = reviews or load_billing_reviews()
    canonical, billings, descriptions = _review_lookups(reviews)
    identities = dict(
        load_artist_identity_evidence()
        if identity_catalog is None
        else identity_catalog
    )
    identities.update(canonical)
    # Official venue listings of standalone artists provide current, scoped
    # identity evidence for corroborating a longer source's separated bill.
    # Reviewed identities and aliases always take precedence.
    for key, value in current_official_standalone_artist_evidence(events).items():
        identities.setdefault(key, value)
    for key, value in current_structured_standalone_artist_evidence(events).items():
        identities.setdefault(key, value)
    # Expand the *current run* exact-identity catalogue only with
    # individually structured performer records and preserve provenance.
    # Reviewed identities, aliases and the published content index retain
    # precedence. Uncorroborated names are reported but not admitted.
    from concert_calendar.artist_identity_catalog import collect_structured_artist_evidence
    new_identities, identity_evidence_report = collect_structured_artist_evidence(
        events, existing=identities,
    )
    for key, display in new_identities.items():
        identities.setdefault(key, display)
    if diagnostics is not None:
        diagnostics["artist_identity_catalog"] = identity_evidence_report
    profiles = reviews.get("sourceProfiles") or {}
    external = {
        _key(name): item
        for name, item in {
            **(reviews.get("externalCorroborations") or {}),
            **(external_evidence or {}),
        }.items()
    }
    groups = _same_event_groups(events)
    audit = {"records": [], "unresolved": []}

    for event in events:
        original = _clean(event.headliner)
        identity = _key(original)
        structured = _stable_unique(event.performers or [])
        structured_is_flat = len(structured) == 1 and _key(structured[0]) == identity

        # Explicitly verified programme bills may correct a ticketing source
        # whose artist array contains a series name or is incomplete.
        # Scope these exceptions by the physical event, never title alone.
        scoped_review = billings.get(_key(event.raw_title)) or billings.get(identity)
        if scoped_review and scoped_review.get("eventDate"):
            if (
                event.date[:10] == scoped_review["eventDate"]
                and _key(event.venue) == _key(scoped_review.get("venue"))
            ):
                scoped_artists = _stable_unique(scoped_review.get("artists") or [])
                if len(scoped_artists) >= 2:
                    event.co_headliners = None
                    _set_resolution(
                        event, scoped_artists, method="reviewed_event",
                        confidence=100,
                        evidence=[scoped_review.get("evidence") or "verified current-event lineup"],
                        description=_clean(scoped_review.get("eventTitle")) or None,
                    )
                    event.event_title = _clean(scoped_review.get("eventTitle")) or event.event_title
                    _record(audit, event)
                    continue

        if len(structured) >= 2:
            # This source may supply individual performers while leaving the
            # display headliner as an opaque flat bill. Previous processing
            # recorded those performers but never applied them to the event.
            # Apply only when the complete bill matches the independently
            # supplied roster, preserving all named acts and existing roles.
            if (
                _billing_matches_roster(original, structured)
                and all(not GENERIC_PART_RE.fullmatch(name) for name in structured)
            ):
                _set_resolution(
                    event, structured, method="structured_source",
                    confidence=100,
                    evidence=["source supplied a separate, complete performer roster"],
                )
            else:
                event._billing_resolution = {
                    "original": event.raw_title or original,
                    "artists": structured,
                    "method": "structured_source",
                    "confidence": 100,
                    "evidence": ["source supplied separate performers; headline left intact"],
                }
            _record(audit, event)
            continue

        description_review = descriptions.get(identity)
        billing_review = billings.get(identity)
        if billing_review and billing_review.get("eventDate"):
            # A scoped lineup is not a reusable project identity.
            billing_review = None
        canonical_name = canonical.get(identity)
        if description_review and description_review.get("eventDate"):
            # An event-specific title correction must never leak into a
            # different appearance of the same artist or tour.
            if not (
                event.date[:10] == description_review["eventDate"]
                and _key(event.venue) == _key(description_review.get("venue"))
            ):
                description_review = None
        if description_review:
            artist = _clean(description_review.get("artist"))
            if artist:
                _set_resolution(
                    event, [artist], method="reviewed_registry", confidence=100,
                    evidence=[description_review.get("evidence") or "exact reviewed description"],
                    description=_clean(description_review.get("description")) or None,
                )
                _record(audit, event)
                continue
        if billing_review and (not structured or structured_is_flat):
            artists = _stable_unique(billing_review.get("artists") or [])
            if len(artists) >= 2:
                _set_resolution(
                    event, artists, method="reviewed_registry", confidence=100,
                    evidence=[billing_review.get("evidence") or "exact reviewed billing"],
                    description=_clean(billing_review.get("eventTitle")) or None,
                )
                _record(audit, event)
                continue
        if canonical_name:
            _set_resolution(
                event, [canonical_name], method="reviewed_registry", confidence=100,
                evidence=["exact reviewed project identity"],
            )
            _record(audit, event)
            continue

        # The final post-reconciliation pass exists only so exact reviewed
        # decisions can be reasserted. Merged source names are not fresh
        # evidence for a source-specific parse.
        if not allow_inference:
            continue

        profile_match = _source_profile(event, profiles)
        billing = original
        profile_parts = []
        presenter = None
        description = None
        if profile_match:
            source, profile = profile_match
            billing, profile_parts, presenter, description = _profile_candidate(
                original, profile
            )

        # A complete known project identity always protects its delimiters.
        if identity in identities or _key(billing) in identities:
            _apply_profile_context(
                event, original, billing, presenter, description
            )
            continue

        # A differently timed source record with explicit roles may be a
        # second performance or an earlier advertised doors/show time.
        # Avoid pre-emptively rewriting the venue's display identity; let
        # the specialized time reconciliation decide the event match first.
        conflicting_timed_role_peer = False
        if event.start_time:
            for peer in groups[(event.date[:10], _key(event.venue))]:
                if (
                    peer is event or not peer.start_time
                    or peer.start_time == event.start_time
                    or not (peer.openers or peer.co_headliners)
                    or _looks_like_flat_billing(peer.headliner)
                ):
                    continue
                peer_roles = _stable_unique([
                    peer.headliner, *(peer.co_headliners or []),
                    *(peer.openers or []),
                ])
                if _billing_matches_roster(billing, peer_roles):
                    conflicting_timed_role_peer = True
                    break
        if conflicting_timed_role_peer:
            _apply_profile_context(event, original, billing, presenter, description)
            continue

        # Strong corroboration must be evaluated before any source grammar
        # hint. The hint may identify candidate punctuation, but is not proof.
        corroborated, corroborated_openers = _cross_source_artists(
            event,
            groups[(event.date[:10], _key(event.venue))],
            billing,
        )
        if corroborated:
            # Explicit roles from the corroborating source are stronger than
            # the neutral hierarchy suggested by a flat display bill.
            if corroborated_openers:
                event.openers = _stable_unique([
                    *(event.openers or []), *corroborated_openers
                ]) or None
            _set_resolution(
                event, corroborated, method="cross_source", confidence=95,
                evidence=["another source supplied a complete separately credited roster for the same date and venue"],
                presenter=presenter, description=description,
            )
            _record(audit, event)
            continue

        same_source, same_source_evidence = _same_source_evidence(event, billing)
        if same_source:
            _set_resolution(
                event, same_source, method="same_source", confidence=95,
                evidence=same_source_evidence,
                presenter=presenter, description=description,
                preserve_roles=True,
            )
            _record(audit, event)
            continue

        parts = _split_spaced_plus(billing)
        catalog_bill = _exact_catalog_bill_candidates(billing, identities)
        if catalog_bill:
            _set_resolution(
                event, catalog_bill,
                method="canonical_identity", confidence=90,
                evidence=["every delimited constituent independently matches an established artist identity"],
                presenter=presenter, description=description,
            )
            _record(audit, event)
            continue

        external_item = external.get(identity) or external.get(_key(billing))
        if external_item:
            artists = _stable_unique(external_item.get("artists") or [])
            confidence = int(external_item.get("confidence") or 0)
            if len(artists) >= 2 and confidence >= AUTOMATIC_THRESHOLD:
                _set_resolution(
                    event, artists, method="external_corroboration", confidence=confidence,
                    evidence=list(external_item.get("evidence") or []),
                    presenter=presenter, description=description,
                )
                _record(audit, event)
                continue

        _apply_profile_context(event, original, billing, presenter, description)
        diagnostic_parts = profile_parts or parts
        if _valid_parts(diagnostic_parts):
            contextual = CONTEXT_RE.search(" ".join(diagnostic_parts)) or "|" in billing
            audit["unresolved"].append({
                "billing": original,
                "date": event.date[:10],
                "venue": event.venue,
                "sources": list(event.source_names or []),
                "confidence": 50,
                "reason": (
                    "contextual wrapper/title semantics require review"
                    if contextual
                    else "punctuation and source convention alone do not establish performer boundaries"
                ),
                **({
                    "supportingEvidence": [
                        f"{source} marks spaced plus as a candidate separator only"
                    ]
                } if profile_match and profile_parts else {}),
            })

    records = audit["records"]
    counts = Counter(item["method"] for item in records)
    method_names = (
        "structured_source", "reviewed_registry", "cross_source",
        "same_source", "canonical_identity", "external_corroboration",
        "source_profile",
    )
    automatic = [item["confidence"] for item in records if item["confidence"] < 100]
    resolved_artists = _stable_unique([
        artist for item in records for artist in item.get("artists") or []
    ])
    audit.update({
        "previouslyOpaqueOrProblematic": len(records) + len(audit["unresolved"]),
        "eventsResolved": len(records),
        "methods": {name: counts[name] for name in method_names},
        "sourceProfileOnlyResolutions": counts["source_profile"],
        "stillUnresolved": len(audit["unresolved"]),
        "automaticConfidenceAverage": round(sum(automatic) / len(automatic), 2) if automatic else None,
        "automaticConfidenceMinimum": min(automatic) if automatic else None,
        "automaticThreshold": AUTOMATIC_THRESHOLD,
        "nearThreshold": [
            item for item in records
            if item["confidence"] == AUTOMATIC_THRESHOLD
        ],
        "newCalendarArtists": sorted(
            [artist for artist in resolved_artists if _key(artist) not in identities],
            key=_key,
        ),
        "resolvedExistingIdentities": sorted(
            [artist for artist in resolved_artists if _key(artist) in identities],
            key=_key,
        ),
    })
    if diagnostics is not None:
        diagnostics["artist_billing_resolution"] = audit


def apply_reviewed_artist_billings(
    events: list[ConcertEvent],
    diagnostics: dict | None = None,
    *,
    reviews: dict | None = None,
    identity_catalog: dict[str, str] | None = None,
    external_evidence: dict[str, dict] | None = None,
    allow_inference: bool = True,
) -> None:
    """Backward-compatible entry point for the evidence-driven resolver."""
    resolve_artist_billings(
        events,
        diagnostics,
        reviews=reviews,
        identity_catalog=identity_catalog,
        external_evidence=external_evidence,
        allow_inference=allow_inference,
    )
