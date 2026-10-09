"""Latest-edition metadata for Electric Eye newsletters."""

from datetime import date

from newsletter.publishing import edition_path


def build_manifest(weekly=None, monthly=None):
    """Build a manifest from successfully published edition identifiers."""
    editions = {}

    for frequency, identifier in (
        ("weekly", weekly),
        ("monthly", monthly),
    ):
        if identifier is None:
            continue

        snapshot = {
            "frequency": frequency,
            "identifier": identifier,
        }
        path = edition_path(snapshot)

        if frequency == "weekly":
            year, week = identifier.split("-W")
            date.fromisocalendar(int(year), int(week), 1)
        else:
            year, month = identifier.split("-")
            date(int(year), int(month), 1)

        editions[frequency] = {
            "identifier": identifier,
            "path": path,
        }

    return {
        "schema_version": 1,
        "editions": editions,
    }


def latest_edition(manifest):
    """Return the most recently completed edition, preferring weekly on ties."""
    editions = manifest.get("editions", {})
    candidates = []

    for frequency, item in editions.items():
        identifier = item["identifier"]

        if frequency == "weekly":
            year, week = map(int, identifier.split("-W"))
            start = date.fromisocalendar(year, week, 1)
            completed = start.toordinal() + 7
            priority = 1

        elif frequency == "monthly":
            year, month = map(int, identifier.split("-"))
            completed = (
                date(year + 1, 1, 1)
                if month == 12
                else date(year, month + 1, 1)
            ).toordinal()
            priority = 0

        else:
            raise ValueError("Unsupported newsletter frequency")

        candidates.append((completed, priority, item))

    if not candidates:
        return None

    return max(candidates, key=lambda candidate: candidate[:2])[2]


def merge_manifest(existing, published):
    """Merge a successfully published edition without losing newer references."""
    if not isinstance(existing, dict):
        raise ValueError("Existing manifest must be an object")

    if existing.get("schema_version") != 1:
        raise ValueError("Unsupported existing manifest schema")

    editions = existing.get("editions")
    if not isinstance(editions, dict):
        raise ValueError("Existing manifest has invalid editions")

    frequency = published.get("frequency")
    identifier = published.get("identifier")
    path = edition_path(published)

    if frequency not in ("weekly", "monthly"):
        raise ValueError("Unsupported edition frequency")

    # Validate the actual calendar period, not merely the identifier pattern.
    if frequency == "weekly":
        year, week = map(int, identifier.split("-W"))
        date.fromisocalendar(year, week, 1)
    else:
        year, month = map(int, identifier.split("-"))
        date(year, month, 1)

    result = {
        "schema_version": 1,
        "editions": {
            key: dict(value)
            for key, value in editions.items()
        },
    }

    current = result["editions"].get(frequency)

    if current is not None:
        current_identifier = current.get("identifier")
        expected_path = edition_path({
            "frequency": frequency,
            "identifier": current_identifier,
        })

        if current.get("path") != expected_path:
            raise ValueError("Existing manifest contains an invalid path")

        if current_identifier >= identifier:
            return result

    result["editions"][frequency] = {
        "identifier": identifier,
        "path": path,
    }

    return result


def render_latest_javascript(manifest):
    """Render cross-origin-readable latest-edition metadata for Blogger."""
    import json

    latest = latest_edition(manifest)
    if latest is None:
        raise ValueError("Cannot publish latest.js without an edition")

    # JSON is valid JavaScript expression syntax. Escape characters that
    # could terminate a script element if this data is ever embedded.
    data = json.dumps(
        {
            "schema_version": 1,
            "latest": latest,
            "editions": manifest["editions"],
        },
        ensure_ascii=True,
        separators=(",", ":"),
    ).replace("<", "\\u003c")

    return "window.ElectricEyeNewsletterLatest = Object.freeze(" + data + ");\n"
