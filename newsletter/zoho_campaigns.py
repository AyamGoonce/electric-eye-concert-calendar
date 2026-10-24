"""Zoho Campaigns integration for Electric Eye newsletter approvals."""

import re

CAMPAIGN_PREFIX = "Electric Eye"
ORGANIZATION_ID = "20120321516"
ZOHO_CAMPAIGNS_BASE = "https://campaigns.zoho.eu"
ZOHO_ACCOUNTS_BASE = "https://accounts.zoho.eu"
ZOHO_API_BASE = f"{ZOHO_CAMPAIGNS_BASE}/api/v1.1"

WEEKLY_IDENTIFIER = re.compile(r"^\d{4}-W\d{2}$")
MONTHLY_IDENTIFIER = re.compile(r"^\d{4}-\d{2}$")


def campaign_name(frequency, identifier):
    """Build a deterministic campaign name for one published edition."""
    if frequency == "weekly" and WEEKLY_IDENTIFIER.fullmatch(identifier):
        return f"{CAMPAIGN_PREFIX} — Weekly Newsletter — {identifier}"

    if frequency == "monthly" and MONTHLY_IDENTIFIER.fullmatch(identifier):
        return f"{CAMPAIGN_PREFIX} — Monthly Newsletter — {identifier}"

    raise ValueError("Invalid newsletter frequency or edition identifier")


def campaign_editor_url(campaign_id):
    """Return the verified Zoho editor URL for a numeric campaign ID."""
    identifier = str(campaign_id)

    if not identifier.isdecimal():
        raise ValueError("Zoho campaign ID must be numeric")

    return (
        f"{ZOHO_CAMPAIGNS_BASE}/campaigns/newui/"
        f"org{ORGANIZATION_ID}#/portal/ws/0/channels/email-campaigns/"
        f"show/{identifier}/tabs/config"
    )


def find_existing_campaign(campaigns, frequency, identifier):
    """Find the campaign belonging to an edition, if one exists."""
    expected = campaign_name(frequency, identifier)

    matches = [
        campaign
        for campaign in campaigns
        if campaign.get("campaign_name") == expected
    ]

    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple Zoho campaigns already exist for {identifier}"
        )

    return matches[0] if matches else None


def refresh_access_token(refresh_token, client_id, client_secret, *, session=None):
    """Exchange a Zoho refresh token for a short-lived access token."""
    import requests

    session = session or requests.Session()
    response = session.post(
        f"{ZOHO_ACCOUNTS_BASE}/oauth/v2/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    token = data.get("access_token")

    if not token:
        raise RuntimeError(
            f"Zoho OAuth refresh failed: {data.get('error', 'no access token')}"
        )

    return token


def list_campaigns(access_token, *, session=None):
    """Read existing Zoho campaigns, including drafts, without modifying them."""
    import requests

    session = session or requests.Session()
    campaigns = []
    from_index = 1
    page_size = 100

    while True:
        response = session.get(
            f"{ZOHO_API_BASE}/recentcampaigns",
            headers={
                "Authorization": f"Zoho-oauthtoken {access_token}"
            },
            params={
                "resfmt": "JSON",
                "sort": "desc",
                "fromindex": from_index,
                "range": page_size,
                "status": "all",
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        if str(data.get("code", "0")) not in ("0", "200"):
            raise RuntimeError(
                f"Zoho campaign lookup failed with code {data['code']}"
            )

        page = data.get("recent_campaigns")

        if not isinstance(page, list):
            raise RuntimeError("Unexpected Zoho campaign lookup response")

        campaigns.extend(page)

        if len(page) < page_size:
            return campaigns

        from_index += page_size

        if from_index > 10000:
            raise RuntimeError("Zoho campaign pagination limit exceeded")


def create_campaign(
    access_token,
    *,
    frequency,
    identifier,
    mailing_list_key,
    topic_id,
    session=None,
):
    """Create a Zoho draft campaign. Never submit or send it."""
    import json
    import requests

    if not mailing_list_key or not topic_id:
        raise ValueError("Mailing list and subscription topic are required")

    name = campaign_name(frequency, identifier)

    template_url = (
        "https://newsletter.electriceyerock.com/"
        f"templates/{frequency}.html"
    )

    subject = (
        f"Electric Eye — Weekly Newsletter — {identifier}"
        if frequency == "weekly"
        else f"Electric Eye — Monthly Newsletter — {identifier}"
    )

    session = session or requests.Session()

    response = session.post(
        f"{ZOHO_API_BASE}/createCampaign",
        headers={
            "Authorization": f"Zoho-oauthtoken {access_token}"
        },
        data={
            "resfmt": "JSON",
            "campaignname": name,
            "from_email": "info@electriceyerock.com",
            "from_name": "Electric Eye",
            "subject": subject,
            "content_url": template_url,
            "list_details": json.dumps({str(mailing_list_key): []}),
            "topicId": str(topic_id),
        },
        timeout=45,
    )

    response.raise_for_status()
    result = response.json()

    if str(result.get("code")) != "200":
        raise RuntimeError(
            f"Zoho campaign creation failed: "
            f"{result.get('message', 'unknown error')}"
        )

    key = result.get("campaignKey")

    if not key:
        raise RuntimeError(
            "Zoho reported campaign creation success "
            "but did not return a campaign key"
        )

    return {
        "campaign_name": name,
        "campaign_key": key,
        "frequency": frequency,
        "identifier": identifier,
    }


def resolve_audience(access_token, *, session=None):
    """Resolve the exact Electric Eye mailing list and subscription topic."""
    import json
    import requests

    session = session or requests.Session()
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }

    lists_response = session.get(
        f"{ZOHO_API_BASE}/getmailinglists",
        headers=headers,
        params={
            "resfmt": "JSON",
            "fromindex": 1,
            "range": 100,
        },
        timeout=30,
    )
    lists_response.raise_for_status()
    lists_data = lists_response.json()

    if str(lists_data.get("code", "0")) not in ("0", "200"):
        raise RuntimeError("Zoho mailing list lookup failed")

    lists = lists_data.get("list_of_details")
    if not isinstance(lists, list):
        raise RuntimeError("Unexpected Zoho mailing list response")

    matching_lists = [
        item for item in lists
        if item.get("listname") == "Electric Eye Newsletter"
    ]

    if len(matching_lists) != 1:
        raise RuntimeError(
            "Expected exactly one Electric Eye Newsletter mailing list"
        )

    topics_response = session.get(
        f"{ZOHO_API_BASE}/topics",
        headers=headers,
        params={
            "details": json.dumps({
                "from_index": 0,
                "range": 100,
            })
        },
        timeout=30,
    )
    topics_response.raise_for_status()
    topics_data = topics_response.json()

    if str(topics_data.get("code", "0")) not in ("0", "200"):
        raise RuntimeError("Zoho subscription topic lookup failed")

    topics = topics_data.get("topicDetails")
    if not isinstance(topics, list):
        raise RuntimeError("Unexpected Zoho subscription topic response")

    matching_topics = [
        item for item in topics
        if item.get("topicName") == "Electric Eye Newsletter"
    ]

    if len(matching_topics) != 1:
        raise RuntimeError(
            "Expected exactly one Electric Eye Newsletter subscription topic"
        )

    list_key = matching_lists[0].get("listkey")
    topic_id = matching_topics[0].get("topicId")

    if not list_key or not topic_id:
        raise RuntimeError("Zoho audience identifiers are missing")

    return {
        "mailing_list_key": str(list_key),
        "topic_id": str(topic_id),
    }


def prepare_campaign(
    frequency,
    identifier,
    *,
    read_token,
    create_token,
    session=None,
):
    """Find or create one draft for an edition; never send it."""
    import requests
    import time

    session = session or requests.Session()

    existing = find_existing_campaign(
        list_campaigns(read_token, session=session),
        frequency,
        identifier,
    )

    if existing is not None:
        campaign = existing
        action = "existing"
    else:
        audience = resolve_audience(read_token, session=session)

        created = create_campaign(
            create_token,
            frequency=frequency,
            identifier=identifier,
            mailing_list_key=audience["mailing_list_key"],
            topic_id=audience["topic_id"],
            session=session,
        )

        action = "created"
        campaign = None

        # Zoho may take a moment to include a new campaign
        # in the recent-campaigns listing.
        for attempt in range(5):
            campaign = find_existing_campaign(
                list_campaigns(read_token, session=session),
                frequency,
                identifier,
            )

            if campaign is not None:
                if campaign.get("campaign_key") != created["campaign_key"]:
                    raise RuntimeError(
                        "Campaign lookup returned an unexpected campaign key"
                    )
                break

            if attempt < 4:
                time.sleep(2)

        if campaign is None:
            raise RuntimeError(
                "Draft was created, but Zoho has not yet returned "
                "its numeric campaign ID. Do not create another draft."
            )

    status = str(campaign.get("campaign_status", "")).strip()

    if status.lower() != "draft":
        raise RuntimeError(
            f"Campaign for {identifier} is already in status "
            f"{status!r}; refusing to request approval."
        )

    campaign_id = campaign.get("campaignId")
    campaign_key = campaign.get("campaign_key")

    if not campaign_id or not campaign_key:
        raise RuntimeError("Existing Zoho campaign has missing identifiers")

    return {
        "action": action,
        "campaign_name": campaign_name(frequency, identifier),
        "campaign_key": campaign_key,
        "campaign_id": str(campaign_id),
        "campaign_status": campaign.get("campaign_status"),
        "editor_url": campaign_editor_url(campaign_id),
        "frequency": frequency,
        "identifier": identifier,
    }
