"""Build a complete archive of published Electric Eye newsletters."""

import json
import re
from datetime import date

from newsletter.publishing import edition_path

WEEKLY = re.compile(r"^weekly/(\d{4}-W\d{2})\.html$")
MONTHLY = re.compile(r"^monthly/(\d{4}-\d{2})\.html$")


def build_archive(paths):
    """Build an archive from actual published newsletter paths."""
    editions = {"weekly": [], "monthly": []}

    for path in set(paths):
        for frequency, pattern in (
            ("weekly", WEEKLY),
            ("monthly", MONTHLY),
        ):
            match = pattern.fullmatch(path)
            if not match:
                continue

            identifier = match.group(1)

            try:
                if frequency == "weekly":
                    year, week = map(int, identifier.split("-W"))
                    start = date.fromisocalendar(year, week, 1)
                    label = (
                        f"Week {week} — "
                        f"{start.strftime('%B')} {start.day}, {year}"
                    )
                else:
                    year, month = map(int, identifier.split("-"))
                    start = date(year, month, 1)
                    label = start.strftime("%B %Y")
            except ValueError:
                continue

            if edition_path({
                "frequency": frequency,
                "identifier": identifier,
            }) != path:
                continue

            editions[frequency].append({
                "identifier": identifier,
                "path": path,
                "label": label,
            })

    for frequency in editions:
        editions[frequency].sort(
            key=lambda item: item["identifier"],
            reverse=True,
        )

    return {"schema_version": 1, "editions": editions}


def render_archive_json(archive):
    return json.dumps(
        archive, ensure_ascii=False, indent=2
    ) + "\n"
