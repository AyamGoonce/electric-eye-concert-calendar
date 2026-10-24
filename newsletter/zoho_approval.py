"""Coordinate Zoho draft preparation and administrative approval."""

import os

from newsletter.approval_state import (
    notification_exists,
    record_notification,
    verify_published_edition,
)
from newsletter.zoho_campaigns import (
    campaign_name,
    prepare_campaign,
    refresh_access_token,
)
from newsletter.zoho_notification import send_approval_notification


def process_approval(
    frequency,
    identifier,
    *,
    publish_token=None,
    read_token=None,
    create_token=None,
    prepare_func=None,
    notify_func=None,
    exists_func=None,
    verify_func=None,
    record_func=None,
):
    """Prepare one draft, notify the administrator, and persist notification.

    Existing approval records prevent repeated notification attempts.
    SMTP and repository writes cannot be atomic: a successful email followed
    by a failed record write can result in another email on a later retry.
    """
    campaign_name(frequency, identifier)

    publish_token = publish_token or os.environ.get("NEWSLETTER_PUBLISH_TOKEN")
    if not publish_token:
        raise RuntimeError("NEWSLETTER_PUBLISH_TOKEN is not configured")

    exists = exists_func or notification_exists
    verify = verify_func or verify_published_edition
    prepare = prepare_func or prepare_campaign
    notify = notify_func or send_approval_notification
    record = record_func or record_notification

    verify(frequency, identifier, token=publish_token)

    if exists(frequency, identifier, token=publish_token):
        return {
            "action": "already_notified",
            "frequency": frequency,
            "identifier": identifier,
        }

    if prepare_func is None:
        client_id = os.environ.get("ZOHO_CAMPAIGNS_CLIENT_ID")
        client_secret = os.environ.get("ZOHO_CAMPAIGNS_CLIENT_SECRET")
        read_refresh = os.environ.get("ZOHO_CAMPAIGNS_READ_REFRESH_TOKEN")
        create_refresh = os.environ.get("ZOHO_CAMPAIGNS_CREATE_REFRESH_TOKEN")

        if not all((client_id, client_secret, read_refresh, create_refresh)):
            raise RuntimeError("Zoho Campaigns OAuth credentials are incomplete")

        read_token = refresh_access_token(
            read_refresh, client_id, client_secret
        )
        create_token = refresh_access_token(
            create_refresh, client_id, client_secret
        )

    campaign = prepare(
        frequency,
        identifier,
        read_token=read_token,
        create_token=create_token,
    )

    if exists(frequency, identifier, token=publish_token):
        return {
            "action": "already_notified",
            "frequency": frequency,
            "identifier": identifier,
        }

    delivery = notify(campaign)

    try:
        saved = record(campaign, token=publish_token)
    except Exception as exc:
        raise RuntimeError(
            "Administrative approval email was submitted to SMTP, "
            "but the permanent notification record could not be saved. "
            "Inspect the approval record before retrying; a retry may "
            "send another administrative email."
        ) from exc

    return {
        "action": "notified",
        "frequency": frequency,
        "identifier": identifier,
        "campaign_id": campaign["campaign_id"],
        "editor_url": campaign["editor_url"],
        "notification": delivery,
        "record": saved,
    }
