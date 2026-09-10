import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

from scripts.resolve_genres import resolve_calendar_asset


class GenreResolverFailureCacheTests(unittest.TestCase):
    def test_transport_failure_is_not_cached_as_unresolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "calendar.js"
            cache = root / "cache.json"

            asset.write_text(
                'window.ElectricEyeConcertData = Object.freeze('
                '[{"h":"Example Artist","x":[],"f":null}]);\n',
                encoding="utf-8",
            )

            with patch(
                "scripts.resolve_genres.musicbrainz_batch",
                side_effect=requests.RequestException("503"),
            ):
                result = resolve_calendar_asset(
                    asset,
                    batch_size=1,
                    cache_path=cache,
                )

            self.assertEqual(0, result["resolved_artists"])

            if cache.exists():
                self.assertEqual(
                    {},
                    json.loads(cache.read_text(encoding="utf-8")),
                )


if __name__ == "__main__":
    unittest.main()
