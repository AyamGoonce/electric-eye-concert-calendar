import unittest

from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.venues import normalize_event_venue


def event(
    date,
    headliner,
    venue,
    *,
    city="Paris",
    department="75",
    source,
    co_headliners=None,
    festival_name=None,
    ticket_url=None,
):
    return ConcertEvent(
        date=date,
        headliner=headliner,
        venue=venue,
        city=city,
        department=department,
        source_names=[source],
        co_headliners=co_headliners,
        festival_name=festival_name,
        ticket_url=ticket_url,
    )


class ReviewedDuplicateBillTests(unittest.TestCase):

    def test_finojet_full_bill_merges_with_structured_dice_bill(self):
        events = [
            event(
                "2026-10-09",
                "Finojet + Tom River",
                "Supersonic Records",
                source="Supersonic",
            ),
            event(
                "2026-10-09",
                "Finojet",
                "Supersonic Records",
                source="DICE",
                co_headliners=["Tom River"],
            ),
        ]

        result = deduplicate_events(events)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].headliner, "Finojet")
        self.assertEqual(result[0].co_headliners, ["Tom River"])
        self.assertEqual(set(result[0].source_names), {"Supersonic", "DICE"})

    def test_dutch_criminal_record_full_bill_merges_with_structured_bill(self):
        events = [
            event(
                "2026-10-17",
                "Dutch Criminal Record + Hotel Mira",
                "Supersonic Records",
                source="Supersonic",
            ),
            event(
                "2026-10-17",
                "Dutch Criminal Record",
                "Supersonic Records",
                source="DICE",
                co_headliners=["Hotel Mira"],
            ),
        ]

        result = deduplicate_events(events)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].headliner, "Dutch Criminal Record")
        self.assertEqual(result[0].co_headliners, ["Hotel Mira"])

    def test_sam_sauvage_alice_on_the_roof_merges(self):
        events = [
            event(
                "2026-10-16",
                "ALICE ON THE ROOF",
                "Théâtre de Rungis",
                city="Rungis",
                department="94",
                source="Zouave",
                ticket_url=(
                    "https://billetterie.seetickets.fr/"
                    "sam-sauvage-alice-on-the-roof-rungis"
                ),
            ),
            event(
                "2026-10-16",
                "Sam Sauvage",
                "Théâtre de Rungis",
                city="Rungis",
                department="94",
                source="DICE",
                co_headliners=["Alice On the Roof"],
                festival_name="Festival de Marne",
            ),
        ]

        result = deduplicate_events(events)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].headliner, "Sam Sauvage")
        self.assertEqual(result[0].co_headliners, ["Alice On the Roof"])

    def test_benjamin_biolay_alice_on_the_roof_merges(self):
        events = [
            event(
                "2026-10-17",
                "ALICE ON THE ROOF",
                "Pavillon Baltard",
                city="Nogent-sur-Marne",
                department="94",
                source="Zouave",
                ticket_url=(
                    "https://billetterie.seetickets.fr/"
                    "benjamin-biolay-alice-on-the-roof-nogent-sur-marne"
                ),
            ),
            event(
                "2026-10-17",
                "Benjamin Biolay",
                "Pavillon Baltard",
                city="Nogent-sur-Marne",
                department="94",
                source="DICE",
                co_headliners=["Alice On the Roof"],
                festival_name="Festival de Marne",
            ),
        ]

        result = deduplicate_events(events)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].headliner, "Benjamin Biolay")
        self.assertEqual(result[0].co_headliners, ["Alice On the Roof"])

    def test_charlie_winston_venue_alias_and_bill_merge(self):
        events = [
            event(
                "2026-10-10",
                "Charlie Winston",
                "FESTIVAL DE MARNE - THEATRE CLAUDE DEBUSSY",
                city="Maisons-Alfort",
                department="94",
                source="Zouave",
            ),
            event(
                "2026-10-10",
                "Charlie Winston",
                "Théâtre Claude Debussy",
                city="Créteil",
                department="94",
                source="DICE",
                co_headliners=["Lisa Li-Lund"],
            ),
        ]

        for item in events:
            normalize_event_venue(item)

        self.assertEqual(
            {item.venue for item in events},
            {"Théâtre Claude Debussy"},
        )
        self.assertEqual(
            {item.city for item in events},
            {"Maisons-Alfort"},
        )

        result = deduplicate_events(events)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].headliner, "Charlie Winston")
        self.assertEqual(result[0].venue, "Théâtre Claude Debussy")
        self.assertEqual(result[0].city, "Maisons-Alfort")
        self.assertEqual(result[0].department, "94")
        self.assertEqual(result[0].co_headliners, ["Lisa Li-Lund"])

    def test_two_different_naruto_programmes_remain_separate(self):
        events = [
            event(
                "2026-09-19",
                "NARUTO SYMPHONIC EXPERIENCE",
                "Le Grand Rex",
                source="Le Grand Rex",
            ),
            event(
                "2026-09-19",
                "NARUTO SHIPPUDEN SYMPHONIC EXPERIENCE",
                "Le Grand Rex",
                source="Le Grand Rex",
            ),
        ]

        result = deduplicate_events(events)

        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
