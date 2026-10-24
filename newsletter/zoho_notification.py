"""Administrative approval notifications for Electric Eye newsletters."""

import os
import smtplib
import ssl
from email.message import EmailMessage
from html import escape
from urllib.parse import urlparse

from newsletter.zoho_campaigns import campaign_editor_url, campaign_name


SMTP_HOST = "smtppro.zoho.eu"
SMTP_PORT = 465
ADMIN_EMAIL = "eric@electriceyerock.com"
ADMIN_SENDER = "Electric Eye Notifications"


def build_approval_message(campaign):
    """Build an administrative email for a verified Zoho draft."""
    frequency = campaign["frequency"]
    identifier = campaign["identifier"]
    name = campaign_name(frequency, identifier)
    campaign_id = campaign["campaign_id"]

    if campaign.get("campaign_name") != name:
        raise ValueError("Campaign name does not match the newsletter edition")

    if str(campaign.get("campaign_status", "")).strip().lower() != "draft":
        raise ValueError("Only Draft campaigns can request approval")

    url = campaign_editor_url(campaign_id)
    if campaign.get("editor_url") != url:
        raise ValueError("Campaign editor URL does not match its numeric ID")

    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "campaigns.zoho.eu":
        raise ValueError("Unexpected Zoho campaign editor URL")

    label = frequency.capitalize()
    subject = f"Electric Eye — {label} Newsletter {identifier} Ready for Approval"

    message = EmailMessage()
    message["From"] = f"{ADMIN_SENDER} <{ADMIN_EMAIL}>"
    message["To"] = ADMIN_EMAIL
    message["Subject"] = subject

    message.set_content(
        f"{label} Newsletter: {identifier}\n"
        f"Campaign: {name}\n"
        "Status: Draft\n\n"
        f"Open Campaign in Zoho: {url}\n\n"
        "Inspect the campaign, then select Review and Launch → Send "
        "in Zoho Campaigns. Subscriber delivery is not automatic.\n"
    )

    message.add_alternative(f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:32px 16px;background:#f2f2f2;
             font-family:Arial,Helvetica,sans-serif;color:#222;">
  <div style="max-width:580px;margin:auto;background:#fff;
              border:1px solid #ddd;padding:32px;">
    <h1 style="margin:0 0 8px;font-size:26px;">ELECTRIC EYE</h1>
    <p style="margin:0 0 28px;color:#777;font-size:13px;
              letter-spacing:1px;">NEWSLETTER APPROVAL</p>
    <h2 style="font-size:21px;">{escape(label)} Newsletter</h2>
    <p>A Zoho Campaigns draft is ready for your review.</p>
    <p><strong>Edition:</strong> {escape(identifier)}<br>
       <strong>Campaign:</strong> {escape(name)}<br>
       <strong>Status:</strong> Draft</p>
    <p style="margin:34px 0;">
      <a href="{escape(url, quote=True)}"
         style="background:#111;color:#fff;text-decoration:none;
                display:inline-block;padding:15px 24px;
                font-weight:bold;">Open Campaign in Zoho</a>
    </p>
    <p>Inspect the campaign and select
       <strong>Review and Launch → Send</strong> in Zoho Campaigns.</p>
    <p style="color:#777;font-size:13px;">
       No newsletter has been sent to subscribers automatically.
    </p>
  </div>
</body>
</html>""", subtype="html")

    return message


def send_approval_notification(campaign, *, smtp_factory=None):
    """Send the approval request only to the administrator."""
    password = os.environ.get("ZOHO_MAIL_APP_PASSWORD")
    if not password:
        raise RuntimeError("ZOHO_MAIL_APP_PASSWORD is not configured")

    message = build_approval_message(campaign)
    factory = smtp_factory or smtplib.SMTP_SSL

    with factory(
        SMTP_HOST,
        SMTP_PORT,
        context=ssl.create_default_context(),
        timeout=30,
    ) as smtp:
        smtp.login(ADMIN_EMAIL, password)
        smtp.send_message(message)

    return {
        "recipient": ADMIN_EMAIL,
        "campaign_id": str(campaign["campaign_id"]),
        "subject": str(message["Subject"]),
    }
