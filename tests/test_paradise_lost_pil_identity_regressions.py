"""Concert billing and Electric Eye article identity regressions."""
import unittest

from concert_calendar.artist_billings import resolve_artist_billings
from concert_calendar.content_index import enrich_events
from concert_calendar.deduplication import deduplicate_events
from concert_calendar.models import ConcertEvent
from concert_calendar.production_export import event_to_data


def make_event(headliner, date="2027-11-28", venue="La Cigale"):
    return ConcertEvent(
        date=date, headliner=headliner, venue=venue,
        city="Paris", department="75", source_names=[venue],
    )


class ParadiseLostBillingTests(unittest.TestCase):
    def test_verified_three_act_bill_preserves_support_roles(self):
        record = make_event(
            "Paradise Lost + Voivod + Dool", "2027-11-21",
            "Élysée Montmartre",
        )
        resolve_artist_billings([record])
        self.assertEqual("Paradise Lost", record.headliner)
        self.assertEqual(["Voivod", "Dool"], record.openers)
        self.assertIsNone(record.co_headliners)
        self.assertEqual(
            ["Paradise Lost", "Voivod", "Dool"],
            record.performers,
        )
        exported = event_to_data(record)
        self.assertEqual("Paradise Lost", exported["h"])
        self.assertEqual(["Voivod", "Dool"], exported["o"])
        self.assertNotIn("ch", exported)

    def test_unverified_flat_bill_does_not_promote_supports(self):
        record = make_event(
            "Paradise Lost + Voivod + Dool", "2027-11-22",
            "Élysée Montmartre",
        )
        # The exact verified lineup is scoped to 21 November.
        # Without separate artist evidence, we must not copy support roles.
        resolve_artist_billings([record], identity_catalog={})
        self.assertEqual("Paradise Lost + Voivod + Dool", record.headliner)
        self.assertIsNone(record.openers)

    def test_dedup_pipeline_still_retains_support_roles(self):
        record = make_event(
            "Paradise Lost + Voivod + Dool", "2027-11-21",
            "Élysée Montmartre",
        )
        result = deduplicate_events([record])
        self.assertEqual(1, len(result))
        self.assertEqual("Paradise Lost", result[0].headliner)
        self.assertEqual(["Voivod", "Dool"], result[0].openers)
        self.assertIsNone(result[0].co_headliners)


class PublicImageLtdArticlesTests(unittest.TestCase):
    def test_all_supported_variants_link_to_same_editorial_artist(self):
        index = {
            "artists": {
                "public-image-ltd": {
                    "n": "Public Image Ltd.", "al": ["PiL", "P.I.L.", "Public Image Limited"],
                    "ar": [1, 2], "crh": None,
                },
            },
        }
        variants = (
            "Public Image Ltd", "Public Image Ltd.", "Public Image",
            "Public Image Limited", "Public Image, Ltd.",
            "Public Image, Ltd", "P.I.L.", "P.I.L", "PiL", "PIL",
        )
        for variant in variants:
            with self.subTest(variant=variant):
                record = make_event(variant)
                enrich_events([record], index)
                self.assertIsNotNone(record.electric_eye_links)
                self.assertEqual("public-image-ltd", record.electric_eye_links[0]["slug"])
                self.assertEqual(2, record.electric_eye_links[0]["count"])
                self.assertEqual("public-image-ltd", record.electric_eye_links[0]["slug"])
                self.assertEqual("public-image-ltd", event_to_data(record)["ee"][0]["slug"])

    def test_unrelated_public_image_phrase_does_not_link(self):
        index = {"artists": {"public-image-ltd": {
            "n": "Public Image Ltd.", "al": [], "ar": [1, 2], "crh": None,
        }}}
        record = make_event("Public Image Art Exhibition")
        enrich_events([record], index)
        self.assertIsNone(record.electric_eye_links)


if __name__ == "__main__":
    unittest.main()
