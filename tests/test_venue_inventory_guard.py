import unittest

from concert_calendar.automation import (
    ProductionValidationError,
    validate_venue_inventory_regression,
)


def event(
    number,
    *,
    venue="Le Zénith Paris – La Villette",
    date="2026-10-01",
    headliner=None,
    ticket=None,
    start_time=None,
):
    return {
        "d": date,
        "h": headliner or f"Artist {number}",
        "v": venue,
        "t": ticket if ticket is not None else f"https://tickets.example/{number}",
        "st": start_time,
    }


class VenueInventoryGuardTests(unittest.TestCase):
    def test_catastrophic_large_venue_drop_is_rejected(self):
        published = [event(i) for i in range(100)]
        candidate = [event(i) for i in range(25)]

        with self.assertRaisesRegex(
            ProductionValidationError,
            r"Le Zénith Paris .* 25/100 retained",
        ):
            validate_venue_inventory_regression(candidate, published)

    def test_same_ticket_multi_session_collapse_is_not_a_regression(self):
        venue = "Sunset/Sunside — Sunside"
        published = []
        candidate = []

        for i in range(30):
            ticket = f"https://tickets.example/sunset/{i}"
            title = f"Jazz Product {i}"

            published.append(
                event(
                    i,
                    venue=venue,
                    headliner=title,
                    ticket=ticket,
                    start_time="19:00",
                )
            )
            published.append(
                event(
                    i,
                    venue=venue,
                    headliner=title,
                    ticket=ticket,
                    start_time="21:00",
                )
            )

            candidate.append(
                event(
                    i,
                    venue=venue,
                    headliner=title,
                    ticket=ticket,
                    start_time=None,
                )
            )

        validate_venue_inventory_regression(candidate, published)

    def test_small_venue_inventory_is_not_guarded(self):
        published = [event(i, venue="Small Venue") for i in range(10)]
        candidate = [event(0, venue="Small Venue")]

        validate_venue_inventory_regression(candidate, published)

    def test_explicit_large_change_override_bypasses_guard(self):
        published = [event(i) for i in range(100)]
        candidate = [event(i) for i in range(1)]

        validate_venue_inventory_regression(
            candidate,
            published,
            allow_large_change=True,
        )

    def test_date_rollover_is_excluded_from_baseline(self):
        published = [
            event(
                i,
                date="2026-09-20",
                venue="Le Zénith Paris – La Villette",
            )
            for i in range(80)
        ]
        published += [
            event(
                100 + i,
                date="2026-10-01",
                venue="Le Zénith Paris – La Villette",
            )
            for i in range(25)
        ]

        candidate = [
            event(
                100 + i,
                date="2026-10-01",
                venue="Le Zénith Paris – La Villette",
            )
            for i in range(25)
        ]

        validate_venue_inventory_regression(candidate, published)


if __name__ == "__main__":
    unittest.main()
