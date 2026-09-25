import tempfile
import unittest
from pathlib import Path

from concert_calendar.venue_export import (
    build_venue_data_asset,
    write_venue_assets,
)


class VenueExportTests(unittest.TestCase):

    def test_data_asset_exposes_venue_data(self):
        index = {
            "Bataclan": {
                "name": "Bataclan",
                "events": [],
                "articles": [],
            }
        }

        filename, digest, asset = build_venue_data_asset(index)

        self.assertTrue(filename.startswith("venue-data."))
        self.assertEqual(len(digest), 64)
        self.assertIn("window.ElectricEyeVenueData", asset)
        self.assertIn("Bataclan", asset)

    def test_writes_versioned_asset_and_pointer(self):
        index = {
            "Bataclan": {
                "name": "Bataclan",
                "events": [],
                "articles": [],
            }
        }

        with tempfile.TemporaryDirectory() as directory:
            result = write_venue_assets(directory, index)

            self.assertTrue(result["data"].exists())
            self.assertTrue(result["pointer"].exists())

            pointer = Path(result["pointer"]).read_text(
                encoding="utf-8"
            )

            self.assertIn(result["filename"], pointer)
            self.assertIn("ElectricEyeVenueManifest", pointer)


if __name__ == "__main__":
    unittest.main()
