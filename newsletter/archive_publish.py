"""Publish the complete newsletter archive from existing GitHub editions."""

import os

import requests

from newsletter.archive import build_archive, render_archive_json
from newsletter.archive_page import render_archive_page
from newsletter.page_publish import API_BASE, TIMEOUT, publish_page


def publish_archive(*, token=None, session=None):
    """Discover published editions and update the public archive."""
    credential = token or os.environ.get("NEWSLETTER_PUBLISH_TOKEN")
    if not credential:
        raise RuntimeError("NEWSLETTER_PUBLISH_TOKEN is not configured")

    session = session or requests.Session()
    headers = {
        "Authorization": f"Bearer {credential}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    paths = []

    for frequency in ("weekly", "monthly"):
        response = session.get(
            f"{API_BASE}/contents/{frequency}",
            params={"ref": "main"},
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        entries = response.json()

        if not isinstance(entries, list):
            raise RuntimeError(
                f"Unexpected GitHub directory response: {frequency}"
            )

        # GitHub's Contents API limits directory listings to 1,000.
        # Fail rather than silently publish an incomplete archive.
        if len(entries) >= 1000:
            raise RuntimeError(
                f"Newsletter directory requires pagination: {frequency}"
            )

        for entry in entries:
            if entry.get("type") == "file":
                paths.append(entry["path"])

    archive = build_archive(paths)

    # Publish data first so the page never references missing data.
    data_result = publish_page(
        "archives/index.json",
        render_archive_json(archive),
        token=credential,
        session=session,
    )

    page_result = publish_page(
        "archives/index.html",
        render_archive_page(),
        token=credential,
        session=session,
    )

    return {
        "data": data_result,
        "page": page_result,
        "counts": {
            frequency: len(archive["editions"][frequency])
            for frequency in ("weekly", "monthly")
        },
    }
