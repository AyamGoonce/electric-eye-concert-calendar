import unittest
from datetime import date, datetime, timedelta, timezone

from concert_calendar.event_state import reconcile_state
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import prepare_upcoming_events


NOW = datetime(2026, 9, 29, 12, tzinfo=timezone.utc)


def event(**values):
    defaults = {
        "date": "2027-03-06",
        "headliner": "Example Artist",
        "venue": "Example Venue",
        "city": "Paris",
        "department": "75",
    }
    defaults.update(values)
    return ConcertEvent(**defaults)


def reconcile_update(old, current):
    previous = reconcile_state([old], None, now=NOW)
    published = prepare_upcoming_events([old], today=date(2026, 9, 29))
    original_id = published[0]["i"]
    original_first_seen = old.first_seen
    reconcile_state(
        [current],
        previous,
        now=NOW + timedelta(hours=6),
        previous_public_events=published,
    )
    return original_id, original_first_seen


class PublicIdContinuityTests(unittest.TestCase):
    def assert_continuity(self, old, current):
        original_id, original_first_seen = reconcile_update(old, current)
        self.assertEqual(original_id, current._public_id)
        self.assertEqual(original_first_seen, current.first_seen)

    def test_unchanged_event_gaining_explicit_time_keeps_public_id(self):
        self.assert_continuity(event(), event(start_time="20:00"))

    def test_spelling_and_accent_correction_keeps_public_id(self):
        self.assert_continuity(
            event(headliner="Jose Gonzalez"),
            event(headliner="José Gonzalez"),
        )

    def test_richer_supported_bill_keeps_public_id(self):
        self.assert_continuity(
            event(headliner="Sananda Maitreya"),
            event(headliner="Sananda Maitreya & The Sugar Plum Pharaohs"),
        )

    def test_unambiguous_festival_day_enrichment_keeps_public_id(self):
        ticket = "https://tickets.example/event/pitchfork-day-one"
        self.assert_continuity(
            event(
                headliner="Pitchfork Music Festival Paris",
                venue="Popup venue",
                ticket_url=ticket,
                festival_name="Pitchfork Music Festival Paris",
            ),
            event(
                headliner="Pitchfork Music Festival Paris — Jour 1",
                venue="Le Trabendo",
                ticket_url=ticket,
                festival_name="Pitchfork Music Festival Paris",
                performers=["Artist One", "Artist Two"],
            ),
        )

    def test_stable_ticket_product_id_survives_slug_and_billing_change(self):
        self.assert_continuity(
            event(
                date="2026-10-01",
                headliner="Emilie Calmé with very special guest",
                venue="Sunset/Sunside — Sunside",
                ticket_url=(
                    "https://billetterie.sunset-sunside.com/event/"
                    "826553-emilie-calme-with-very-special-guest-nouvel-album-alice"
                ),
            ),
            event(
                date="2026-10-01",
                headliner="Emilie Calmé invite Shai Maestro",
                venue="Sunset/Sunside — Sunside",
                ticket_url=(
                    "https://billetterie.sunset-sunside.com/event/"
                    "826553-emilie-calme-invite-shai-maestro-nouvel-album-alice"
                ),
            ),
        )

    def test_flat_bill_to_structured_bill_keeps_public_id(self):
        self.assert_continuity(
            event(
                date="2026-10-01",
                headliner="The Devil And The Almighty Blues + Skyjoggers",
                venue="Backstage By The Mill",
            ),
            event(
                date="2026-10-01",
                headliner="The Devil And The Almighty Blues",
                co_headliners=["Skyjoggers"],
                venue="Backstage By The Mill",
            ),
        )

    def test_venue_alias_change_keeps_public_id(self):
        self.assert_continuity(
            event(
                date="2027-05-20",
                headliner="Bénabar",
                venue="Le Dôme de Paris",
                ticket_url="https://www.ledomedeparis.com/fr/spectacle/347/benabar",
            ),
            event(
                date="2027-05-20",
                headliner="Bénabar",
                venue="Dôme de Paris – Palais des Sports",
                ticket_url="https://caramba.trium.fr/fr/t/-/event/66207",
            ),
        )

    def test_different_ticket_product_does_not_force_continuity(self):
        old = event(
            date="2026-10-01",
            headliner="Old Artist",
            venue="Sunset/Sunside — Sunside",
            ticket_url=(
                "https://billetterie.sunset-sunside.com/event/"
                "826553-old-artist"
            ),
        )
        current = event(
            date="2026-10-01",
            headliner="Different Artist",
            venue="Sunset/Sunside — Sunside",
            ticket_url=(
                "https://billetterie.sunset-sunside.com/event/"
                "826554-different-artist"
            ),
        )

        original_id, _ = reconcile_update(old, current)
        self.assertNotEqual(original_id, current._public_id)

    def test_changed_structured_bill_does_not_force_continuity(self):
        old = event(
            date="2026-10-01",
            headliner="Alpha + Beta",
            venue="Example Venue",
        )
        current = event(
            date="2026-10-01",
            headliner="Alpha",
            co_headliners=["Gamma"],
            venue="Example Venue",
        )

        original_id, _ = reconcile_update(old, current)
        self.assertNotEqual(original_id, current._public_id)

    def test_venue_alias_alone_does_not_force_continuity(self):
        old = event(
            date="2027-05-20",
            headliner="Bénabar",
            venue="Le Dôme de Paris",
        )
        current = event(
            date="2027-05-20",
            headliner="Different Artist",
            venue="Dôme de Paris – Palais des Sports",
        )

        original_id, _ = reconcile_update(old, current)
        self.assertNotEqual(original_id, current._public_id)

    def test_one_old_route_is_not_assigned_to_two_current_performances(self):
        old = event()
        previous = reconcile_state([old], None, now=NOW)
        published = prepare_upcoming_events([old], today=date(2026, 9, 29))
        early = event(start_time="19:00", performance_marker="early show")
        late = event(start_time="21:00", performance_marker="late show")

        reconcile_state(
            [early, late],
            previous,
            now=NOW + timedelta(hours=6),
            previous_public_events=published,
        )

        self.assertEqual(2, len({early._public_id, late._public_id}))
        self.assertEqual(1, sum(
            item._public_id == published[0]["i"] for item in (early, late)
        ))


if __name__ == "__main__":
    unittest.main()
