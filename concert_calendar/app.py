from concert_calendar.models import ConcertEvent


def run() -> None:
    print("Île-de-France Concert Calendar")

    concert = ConcertEvent(
        date="2026-10-23",
        headliner="Tony Iommi",
        venue="L’Olympia Bruno Coquatrix",
        city="Paris",
        department="75",
        openers=["Support artist"],
        promoters=["Gérard Drouot Productions"],
    )

    print(concert)