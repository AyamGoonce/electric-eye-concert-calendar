from dataclasses import dataclass
from typing import Optional@dataclass
class ConcertEvent:
    date: str
    headliner: str
    venue: str
    city: str
    department: str

    openers: Optional[list[str]] = None
    promoters: Optional[list[str]] = None
    genre: Optional[str] = None
    facebook_event_url: Optional[str] = None
    ticket_url: Optional[str] = None