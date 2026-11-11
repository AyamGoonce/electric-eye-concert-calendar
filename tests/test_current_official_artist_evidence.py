"""Corroborate separators from independent official venue solo artist identities."""
import unittest
from concert_calendar.artist_billings import resolve_artist_billings, current_official_standalone_artist_evidence
from concert_calendar.models import ConcertEvent


def event(title, source, date="2027-01-01", venue="File7"):
    return ConcertEvent(
        date=date, headliner=title, venue=venue,
        city="Magny-le-Hongre", department="77",
        source_names=[source],
    )


class CurrentOfficialArtistEvidenceTests(unittest.TestCase):
    def test_verified_independent_solo_bills_resolve_full_multi_artist_bill(self):
        combined = event("REVNOIR + Solitaris + TRVMA", "DICE", "2027-02-10")
        records = [
            combined,
            event("REVNOIR", "File7", "2027-01-01"),
            event("Solitaris", "File7", "2027-01-02"),
            event("TRVMA", "File7", "2027-01-03"),
        ]
        resolve_artist_billings(records, identity_catalog={})
        self.assertEqual("REVNOIR", combined.headliner)
        self.assertEqual(["Solitaris", "TRVMA"], combined.co_headliners)
        self.assertEqual(["REVNOIR", "Solitaris", "TRVMA"], combined.performers)

    def test_dice_only_single_artist_listings_are_not_standalone_confirmation(self):
        combined = event("REVNOIR + Solitaris", "DICE", "2027-02-10")
        records = [
            combined,
            event("REVNOIR", "DICE", "2027-01-01"),
            event("Solitaris", "DICE", "2027-01-02"),
        ]
        resolve_artist_billings(records, identity_catalog={})
        self.assertEqual("REVNOIR + Solitaris", combined.headliner)

    def test_unrecognized_constituent_prevents_partial_guessing(self):
        combined = event("REVNOIR + Solitaris + Unknown Artist", "DICE", "2027-02-10")
        records = [
            combined,
            event("REVNOIR", "File7"),
            event("Solitaris", "File7", "2027-01-02"),
        ]
        resolve_artist_billings(records, identity_catalog={})
        self.assertEqual("REVNOIR + Solitaris + Unknown Artist", combined.headliner)

    def test_known_whole_artist_project_remains_opaque(self):
        combined = event("Florence + The Machine", "DICE", "2027-02-10")
        records = [
            combined,
            event("Florence", "File7"),
            event("The Machine", "File7", "2027-01-02"),
        ]
        resolve_artist_billings(records, identity_catalog={
            "florence the machine": "Florence + The Machine",
        })
        self.assertEqual("Florence + The Machine", combined.headliner)
        self.assertIsNone(combined.co_headliners)

    def test_already_structured_billing_does_not_become_false_standalone(self):
        item = event("Full Bill", "File7")
        item.performers = ["Separate Act", "Another Act"]
        self.assertNotIn("full bill", current_official_standalone_artist_evidence([item]))


if __name__ == "__main__":
    unittest.main()
