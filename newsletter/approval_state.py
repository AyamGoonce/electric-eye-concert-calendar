"""Persistent approval-notification records in the newsletter repository."""

import base64
import json
import os
from datetime import datetime, timezone

import requests

from newsletter.github_publish import API_BASE, TIMEOUT
from newsletter.publishing import edition_path
from newsletter.zoho_campaigns import campaign_editor_url, campaign_name


def approval_path(frequency, identifier):
    """Return a validated, edition-specific approval-record path."""
    campaign_name(frequency, identifier)
    return f"approvals/{frequency}/{identifier}.json"


def github_headers(token):
    """Build authenticated GitHub Contents API headers."""
    if not token:
        raise RuntimeError("NEWSLETTER_PUBLISH_TOKEN is not configured")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def notification_exists(frequency, identifier, *, token=None, session=None):
    """Check whether the approval notification was previously recorded."""
    path = approval_path(frequency, identifier)
    credential = token or os.environ.get("NEWSLETTER_PUBLISH_TOKEN")
    headers = github_headers(credential)
    session = session or requests.Session()

    response = session.get(
        f"{API_BASE}/contents/{path}",
        headers=headers,
        params={"ref": "main"},
        timeout=TIMEOUT,
    )

    if response.status_code == 200:
        return True
    if response.status_code == 404:
        return False

    response.raise_for_status()
    raise RuntimeError("Could not determine approval notification state")


def verify_published_edition(frequency, identifier, *, token=None, session=None):
    """Require the immutable edition to exist before requesting approval."""
    campaign_name(frequency, identifier)
    credential = token or os.environ.get("NEWSLETTER_PUBLISH_TOKEN")
    headers = github_headers(credential)
    session = session or requests.Session()

    response = session.get(
        f"{API_BASE}/contents/{edition_path({'frequency': frequency, 'identifier': identifier})}",
        headers=headers,
        params={"ref": "main"},
        timeout=TIMEOUT,
    )

    if response.status_code == 404:
        raise RuntimeError("Newsletter edition has not been published")
    response.raise_for_status()

    if response.status_code != 200:
        raise RuntimeError("Could not verify the published newsletter edition")

    return True


def record_notification(campaign, *, token=None, session=None):
    """Create a permanent notification record; never overwrite one."""
    frequency = campaign["frequency"]
    identifier = campaign["identifier"]
    path = approval_path(frequency, identifier)
    name = campaign_name(frequency, identifier)
    campaign_id = str(campaign["campaign_id"])

    if campaign.get("campaign_name") != name:
        raise ValueError("Campaign name does not match edition")

    if str(campaign.get("campaign_status", "")).strip().lower() != "draft":
        raise ValueError("Only Draft campaigns can be recorded")

    if campaign.get("editor_url") != campaign_editor_url(campaign_id):
        raise ValueError("Campaign editor URL does not match ID")

    credential = token or os.environ.get("NEWSLETTER_PUBLISH_TOKEN")
    headers = github_headers(credential)
    session = session or requests.Session()

    record = {
        "schema_version": 1,
        "frequency": frequency,
        "identifier": identifier,
        "campaign_id": campaign_id,
        "campaign_name": name,
        "notification_recipient": "eric@electriceyerock.com",
        "notified_at": datetime.now(timezone.utc).isoformat(),
    }

    payload = {
        "message": f"Record Electric Eye newsletter approval {identifier}",
        "content": base64.b64encode(
            (json.dumps(record, indent=2) + "\n").encode("utf-8")
        ).decode("ascii"),
        "branch": "main",
    }

    response = session.put(
        f"{API_BASE}/contents/{path}",
        headers=headers,
        json=payload,
        timeout=TIMEOUT,
    )

    if response.status_code == 201:
        return {
            "action": "created",
            "path": path,
            "commit": response.json()["commit"]["sha"],
        }

    if response.status_code in (409, 422):
        raise RuntimeError(
            "Approval record creation conflicted with another write; "
            "check repository state before retrying"
        )

    response.raise_for_status()
    raise RuntimeError("Unexpected approval-record creation response")
