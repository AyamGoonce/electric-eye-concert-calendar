from dataclasses import dataclass
from typing import Optional


@dataclass
class ConcertEvent:
    date: str
    headliner: str
    venue: str
    city: str
    department: str

    openers: Optional[list[str]] = None
    co_headliners: Optional[list[str]] = None
    promoters: Optional[list[str]] = None
    genre: Optional[str] = None
    facebook_event_url: Optional[str] = None
    ticket_url: Optional[str] = None
    festival_name: Optional[str] = None
    authoritative_billing: bool = False
    sold_out: bool = False
    first_seen: Optional[str] = None
    genre_public: Optional[str] = None
    genre_source: Optional[str] = None
    genre_method: Optional[str] = None
    genre_evidence: Optional[list[dict]] = None
    ticket_status: Optional[str] = None
    start_time: Optional[str] = None
    announced_at: Optional[str] = None
    event_title: Optional[str] = None
    series_name: Optional[str] = None
    image_url: Optional[str] = None
    image_source: Optional[str] = None
    electric_eye_links: Optional[list[dict]] = None
