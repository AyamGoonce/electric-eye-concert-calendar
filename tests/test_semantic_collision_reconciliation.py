import unittest
from datetime import datetime, timezone

from concert_calendar.automation import (
    ProductionValidationError,
    validate_semantic_collisions,
)
from concert_calendar.deduplication import (
    deduplicate_events,
    high_confidence_collision_pairs,
)
from concert_calendar.event_state import reconcile_state
from concert_calendar.models import ConcertEvent


def event(
    date,
    headliner,
    venue,
    source,
    *,
    start_time=None,
    ticket_url=None,
):
    return ConcertEvent(
        date=date,
        headliner=headliner,
        venue=venue,
        city="Paris",
        department="75",
        source_names=[source],
        start_time=start_time,
        ticket_url=ticket_url,
    )


class PhysicalEventTitleVariantTests(unittest.TestCase):
    def test_accor_branded_bill_and_promoter_artist_merge(self):
        rich = event(
            "2026-10-17",
            "LE GRAND BAL - YOUSSOU NDOUR & LE SUPER ÉTOILE DE DAKAR",
            "Accor Arena",
            "Accor Arena",
            start_time="19:00",
            ticket_url="https://official.example/youssou",
        )
        short = event(
            "2026-10-17",
            "Youssou Ndour",
            "Accor Arena",
            "Alias Production",
            ticket_url="https://promoter.example/youssou",
        )

        merged = deduplicate_events([rich, short])

        self.assertEqual(1, len(merged))
        self.assertEqual(
            "LE GRAND BAL - YOUSSOU NDOUR & LE SUPER ÉTOILE DE DAKAR",
            merged[0].headliner,
        )
        self.assertEqual("19:00", merged[0].start_time)
        self.assertEqual(
            {"Accor Arena", "Alias Production"},
            set(merged[0].source_names),
        )
        self.assertIn("Youssou Ndour", merged[0].identity_aliases)

    def test_grand_rex_duo_and_promoter_artist_merge(self):
        rich = event(
            "2027-03-24",
            "ANGELIQUE KIDJO AND YOUSSOU NDOUR",
            "Le Grand Rex",
            "Le Grand Rex",
            start_time="20:00",
        )
        short = event(
            "2027-03-24",
            "Youssou Ndour",
            "Le Grand Rex",
            "Alias Production",
        )

        merged = deduplicate_events([rich, short])

        self.assertEqual(1, len(merged))
        self.assertEqual(
            "ANGELIQUE KIDJO AND YOUSSOU NDOUR",
            merged[0].headliner,
        )
        self.assertIn("Youssou Ndour", merged[0].identity_aliases)

    def test_reviewed_artist_alias_merges_without_event_specific_rule(self):
        short = event(
            "2026-10-11",
            "Dexys",
            "Élysée Montmartre",
            "Alias Production",
        )
        historical_name = event(
            "2026-10-11",
            "DEXYS MIDNIGHT RUNNERS",
            "Élysée Montmartre",
            "Élysée Montmartre",
        )

        merged = deduplicate_events([short, historical_name])

        self.assertEqual(1, len(merged))
        self.assertEqual("Dexys", merged[0].headliner)
        self.assertIn("DEXYS MIDNIGHT RUNNERS", merged[0].identity_aliases)

    def test_richer_historical_route_and_earliest_first_seen_survive(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        prior_rich = event(
            "2026-10-17",
            "LE GRAND BAL - YOUSSOU NDOUR & LE SUPER ÉTOILE DE DAKAR",
            "Accor Arena",
            "Accor Arena",
            start_time="19:00",
        )
        prior_short = event(
            "2026-10-17",
            "Youssou Ndour",
            "Accor Arena",
            "Alias Production",
        )
        previous = reconcile_state(
            [prior_rich, prior_short],
            None,
            now=now,
        )
        rich_public_id = prior_rich._public_id
        previous["events"][prior_short._state_identity]["first_seen"] = (
            "2026-08-20T11:02:59Z"
        )
        previous["events"][prior_rich._state_identity]["first_seen"] = (
            "2026-08-26T13:45:57Z"
        )

        current = deduplicate_events([
            event(
                "2026-10-17",
                "LE GRAND BAL - YOUSSOU NDOUR & LE SUPER ÉTOILE DE DAKAR",
                "Accor Arena",
                "Accor Arena",
                start_time="19:00",
            ),
            event(
                "2026-10-17",
                "Youssou Ndour",
                "Accor Arena",
                "Alias Production",
            ),
        ])
        reconcile_state(
            current,
            previous,
            now=datetime(2026, 9, 21, tzinfo=timezone.utc),
        )

        self.assertEqual(rich_public_id, current[0]._public_id)
        self.assertEqual("2026-08-20T11:02:59Z", current[0].first_seen)


class CollisionSafetyTests(unittest.TestCase):
    def test_explicit_different_performance_times_remain_distinct(self):
        early = event(
            "2026-10-31",
            "TIGERCUB – 16H",
            "La Boule Noire",
            "La Boule Noire",
        )
        late = event(
            "2026-10-31",
            "TIGERCUB – 20H",
            "La Boule Noire",
            "La Boule Noire",
        )
        plain = event(
            "2026-10-31",
            "Tigercub",
            "La Boule Noire",
            "AEG Presents France",
        )

        result = deduplicate_events([plain, early, late])

        self.assertEqual(2, len(result))
        self.assertEqual(
            {"tigercub", "tigercub – 20h"},
            {item.headliner.casefold() for item in result},
        )
        self.assertEqual([], high_confidence_collision_pairs(result))

    def test_same_date_venue_without_related_artist_does_not_merge(self):
        rows = [
            event("2027-01-01", "Artist One", "Example Hall", "Venue"),
            event("2027-01-01", "Artist Two", "Example Hall", "Promoter"),
        ]
        self.assertEqual(2, len(deduplicate_events(rows)))

    def test_same_source_punctuation_is_not_enough(self):
        rows = [
            event(
                "2027-01-01",
                "The Devil And The Almighty Blues",
                "Example Hall",
                "Venue",
            ),
            event(
                "2027-01-01",
                "The Devil And The Almighty Blues + Skyjoggers",
                "Example Hall",
                "Venue",
            ),
        ]
        self.assertEqual(2, len(deduplicate_events(rows)))

    def test_gate_fails_with_precise_high_confidence_diagnostic(self):
        rows = [
            event(
                "2027-03-24",
                "ANGELIQUE KIDJO AND YOUSSOU NDOUR",
                "Le Grand Rex",
                "Le Grand Rex",
                start_time="20:00",
                ticket_url="https://venue.example/duo",
            ),
            event(
                "2027-03-24",
                "Youssou Ndour",
                "Le Grand Rex",
                "Alias Production",
                ticket_url="https://promoter.example/youssou",
            ),
        ]

        with self.assertRaisesRegex(
            ProductionValidationError,
            r"2027-03-24.*Le Grand Rex.*ANGELIQUE.*Alias Production",
        ):
            validate_semantic_collisions(rows)

    def test_gate_ignores_unrelated_and_distinct_performance_rows(self):
        rows = [
            event(
                "2027-01-01",
                "Artist One – 16H",
                "Example Hall",
                "Venue",
            ),
            event(
                "2027-01-01",
                "Artist One – 20H",
                "Example Hall",
                "Promoter",
            ),
            event(
                "2027-01-01",
                "Artist Two",
                "Example Hall",
                "Venue",
            ),
        ]

        validate_semantic_collisions(rows)


if __name__ == "__main__":
    unittest.main()
