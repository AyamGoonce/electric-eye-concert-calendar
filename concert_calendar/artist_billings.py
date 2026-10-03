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
        event.co_headliners = _stable_unique(
            [*(event.co_headliners or []), *artists[1:]]
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


def _cross_source_artists(
    event: ConcertEvent,
    group: list[ConcertEvent],
    billing: str,
) -> list[str]:
    opaque = _key(billing)
    event_sources = set(event.source_names or [])
    for candidate in group:
        artists = _stable_unique(candidate.performers or [])
        if candidate is event or len(artists) < 2:
            continue
        if event_sources and set(candidate.source_names or []) == event_sources:
            continue
        parts = _split_spaced_plus(billing)
        if _valid_parts(parts) and [_key(part) for part in parts] == [_key(part) for part in artists]:
            return artists
        if all(
            re.search(rf"(?<![a-z0-9]){re.escape(_key(name))}(?![a-z0-9])", opaque)
            for name in artists
        ):
            return artists
    return []


def _same_source_evidence(event: ConcertEvent, billing: str) -> tuple[list[str], list[str]]:
    """Return a bill supported by per-record source structure, never punctuation alone."""
    supplied = getattr(event, "_billing_evidence", None) or {}
    supplied_artists = _stable_unique(supplied.get("artists") or [])
    if len(supplied_artists) >= 2 and int(supplied.get("confidence") or 0) >= 95:
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

        if len(structured) >= 2:
            event._billing_resolution = {
                "original": event.raw_title or original,
                "artists": structured,
                "method": "structured_source",
                "confidence": 100,
                "evidence": ["source supplied separate performers"],
            }
            _record(audit, event)
            continue

        description_review = descriptions.get(identity)
        billing_review = billings.get(identity)
        canonical_name = canonical.get(identity)
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

        # Strong corroboration must be evaluated before any source grammar
        # hint. The hint may identify candidate punctuation, but is not proof.
        corroborated = _cross_source_artists(
            event,
            groups[(event.date[:10], _key(event.venue))],
            billing,
        )
        if corroborated:
            _set_resolution(
                event, corroborated, method="cross_source", confidence=95,
                evidence=["another source supplied separate performers for the same date and venue"],
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
        if _valid_parts(parts) and all(_key(part) in identities for part in parts):
            _set_resolution(
                event, [identities[_key(part)] for part in parts],
                method="canonical_identity", confidence=90,
                evidence=["every constituent is an exact Electric Eye identity or alias"],
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
