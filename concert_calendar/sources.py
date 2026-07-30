from concert_calendar.models import ConcertEvent


def load_events() -> list[ConcertEvent]:
    return [
        ConcertEvent(
            date="2026-10-23",
            headliner="Tony Iommi",
            venue="L’Olympia Bruno Coquatrix",
            city="Paris",
            department="75",
            openers=["Support artist"],
            promoters=["Gérard Drouot Productions"],
        )
    ]