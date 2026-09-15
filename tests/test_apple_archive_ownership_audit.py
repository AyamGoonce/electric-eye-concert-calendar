import importlib.util
import gzip
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_apple_archive_ownership.py"
SPEC = importlib.util.spec_from_file_location("apple_archive_audit", SCRIPT)
audit_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(audit_module)


def item(stable_id, creator, artist_id):
    return {
        "stableId": stable_id,
        "title": stable_id,
        "creator": creator,
        "appleArtistId": artist_id,
        "category": "LISTEN",
    }


def payload(post_id, title, primary, artist_id, items, ownership=None, keys=None):
    result = {
        "postId": post_id,
        "subject": {"title": title, "primaryArtists": primary},
        "identity": {"level": "HIGH", "artistId": artist_id},
        "categories": [{"category": "LISTEN", "items": items}],
    }
    if ownership is not None:
        result["diagnostics"] = {
            "ownershipVersion": ownership,
            "artistKeys": keys or [],
            "sourceArtistKeys": keys or [],
            "recommendationMode": "ARTIST_RELATIONSHIP",
        }
    return result


class AppleArchiveOwnershipAuditTests(unittest.TestCase):
    def setUp(self):
        artists = []
        for name in (
            "Dopelord", "Varukers", "Whiplash", "Charli xcx", "Stevie Wonder",
            "Green Lung", "The Dresden Dolls", "Jeff Tweedy", "The Obsessed",
        ):
            artists.append({
                "canonicalName": name,
                "slug": audit_module.slug(name),
                "aliases": [],
                "alternateSpellings": [],
                "members": [],
                "associatedActs": ["Wilco"] if name == "Jeff Tweedy" else [],
            })
        self.registry = {"structuralLabels": ["Paris", "concert review"], "artists": artists}
        self.monitors = {
            "5758447714051230467": ("Dopelord", None),
            "5310330220034938391": ("Varukers", "432942256"),
            "1969525538088714658": ("Whiplash", "432942256"),
        }
        self.controls = {
            "3770317650417472214": "Stevie Wonder",
            "805696197317024340": "Green Lung",
            "5595601640915382763": "The Dresden Dolls",
            "7327006856375945885": "Jeff Tweedy",
            "1449716375692518163": "The Obsessed",
        }

    def build_fixture(self):
        posts = []
        rows = []
        static = {}
        for post_id, (name, artist_id) in self.monitors.items():
            title = f"{name} @ Tattoo Planetarium, Paris - January 31st, 2026"
            posts.append({"postId": post_id, "title": title, "url": "/" + post_id, "labels": [name, "Paris"]})
            legacy = payload(
                post_id, title, [name, "Mondial du Tatouage", "Paris"], artist_id,
                [item("contaminated", "Charli xcx", "432942256")],
            )
            rows.append({"postId": post_id, "status": "READY", "generatedAt": "2026-01-01", "payload": legacy})
            static[post_id] = legacy
        for index, (post_id, name) in enumerate(self.controls.items(), 1):
            title = f"{name} returns"
            posts.append({"postId": post_id, "title": title, "url": "/" + post_id, "labels": [name]})
            current = payload(
                post_id, title, [name], str(1000 + index),
                [item("healthy-" + post_id, name, str(1000 + index))], 2, [audit_module.slug(name)],
            )
            rows.append({"postId": post_id, "status": "READY", "generatedAt": "2026-09-01", "payload": current})
            static[post_id] = {key: value for key, value in current.items() if key != "diagnostics"}
        return posts, rows, static

    def test_monitoring_articles_and_controls_are_classified_sensibly(self):
        posts, rows, static = self.build_fixture()
        result = audit_module.build_audit(posts, rows, [], self.registry, static)
        records = {record["postId"]: record for record in result["records"]}
        for post_id, (name, _) in self.monitors.items():
            record = records[post_id]
            self.assertEqual(name, record["detectedAuthoritativeSubject"])
            self.assertIn("LEGACY_OWNERSHIP", record["flags"])
            self.assertIn("CHARLI_CONTAMINATION_SUSPECTED", record["flags"])
            self.assertIn("CONTEXT_AS_ARTIST", record["flags"])
            self.assertNotIn("HEALTHY_V2", record["flags"])
        for post_id, name in self.controls.items():
            record = records[post_id]
            self.assertEqual(name, record["detectedAuthoritativeSubject"])
            self.assertIn("HEALTHY_V2", record["flags"])
            self.assertFalse(record["staticDiagnosticsPresent"])
            self.assertNotIn("STATIC_BACKEND_MISMATCH", record["flags"])

    def test_historical_recovery_requires_non_circular_exact_subject_evidence(self):
        bad = payload("1", "Example Artist returns", ["Example Artist"], "432942256", [item("x", "Charli xcx", "432942256")])
        good = payload("2", "Other Artist returns", ["Other Artist"], "222", [item("y", "Other Artist", "222")])
        rows = [
            {"postId": "1", "status": "READY", "payload": bad},
            {"postId": "2", "status": "READY", "payload": good},
        ]
        groups = audit_module.historical_recovery_groups(rows)
        self.assertFalse(groups["example artist"]["exactEvidence"])
        self.assertTrue(groups["other artist"]["exactEvidence"])

    def test_complete_population_and_orphan_do_not_abort(self):
        posts = [{"postId": "1", "title": "Artist returns", "url": "/1", "labels": ["Artist"]}]
        rows = [
            {"postId": "1", "status": "EMPTY", "payload": {"postId": "1", "categories": []}},
            {"postId": "488372604587833294", "status": "ERROR", "payload": {"postId": "488372604587833294", "categories": []}},
        ]
        registry = {"structuralLabels": [], "artists": [{"canonicalName": "Artist", "slug": "artist", "aliases": []}]}
        result = audit_module.build_audit(posts, rows, [], registry, {"9": {"postId": "9", "categories": []}})
        records = {record["postId"]: record for record in result["records"]}
        self.assertEqual("EMPTY", records["1"]["backendStatus"])
        self.assertEqual("ORPHAN_DELETED", records["488372604587833294"]["taxonomy"])
        self.assertIn("ORPHAN_BLOGGER_NOT_FOUND", records["488372604587833294"]["flags"])
        self.assertIn("9", result["staticPublicationGaps"]["staticOnly"])

    def test_legitimate_charli_article_is_observed_not_blacklisted(self):
        post = {"postId": "1", "title": "Charli xcx returns", "url": "/1", "labels": ["Charli xcx"]}
        current = payload("1", post["title"], ["Charli xcx"], "432942256", [item("brat", "Charli xcx", "432942256")], 2, ["charli-xcx"])
        result = audit_module.build_audit([post], [{"postId": "1", "status": "READY", "payload": current}], [], self.registry, {"1": current})
        record = result["records"][0]
        self.assertIn("CHARLI_PRESENT", record["flags"])
        self.assertNotIn("CHARLI_CONTAMINATION_SUSPECTED", record["flags"])

    def test_shared_ownership_id_collision_is_reported(self):
        posts = [
            {"postId": "1", "title": "Dopelord returns", "url": "/1", "labels": ["Dopelord"]},
            {"postId": "2", "title": "Whiplash returns", "url": "/2", "labels": ["Whiplash"]},
        ]
        rows = [
            {"postId": "1", "status": "READY", "payload": payload("1", posts[0]["title"], ["Dopelord"], "432942256", [item("a", "Charli xcx", "432942256")], 2, ["dopelord"])},
            {"postId": "2", "status": "READY", "payload": payload("2", posts[1]["title"], ["Whiplash"], "432942256", [item("b", "Charli xcx", "432942256")], 2, ["whiplash"])},
        ]
        result = audit_module.build_audit(posts, rows, [], self.registry, {})
        self.assertEqual("432942256", result["appleArtistIdCollisions"][0]["appleArtistId"])
        self.assertEqual(["dopelord", "whiplash"], result["appleArtistIdCollisions"][0]["authoritativeSubjects"])
        self.assertTrue(all("SHARED_SUSPICIOUS_APPLE_ID" in record["flags"] for record in result["records"]))

    def test_snapshot_and_static_parsers_are_read_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot.json"
            snapshot.write_text(json.dumps({
                "payloadRows": [["1", "/1", "2026", "FR", json.dumps({"postId": "1", "categories": []}), "EMPTY", "", 0]],
                "artistRows": [["artist", "Artist", 1, 1, "123", "", "HIGH", "RESOLVED", json.dumps({"categories": []})]],
            }))
            static_root = root / "proof"
            static_root.mkdir()
            static_file = static_root / "apple-payload-1.js"
            static_file.write_text("window.__EE_APPLE_STATIC_PAYLOAD__={\"postId\":\"1\",\"categories\":[]};if(window.__eeAppleStaticReceive)window.__eeAppleStaticReceive(window.__EE_APPLE_STATIC_PAYLOAD__);\n")
            before_snapshot = snapshot.read_bytes()
            before_static = static_file.read_bytes()
            payload_rows, artist_rows = audit_module.load_backend_snapshot(snapshot)
            static = audit_module.load_static_payloads(static_root)
            self.assertEqual("EMPTY", payload_rows[0]["status"])
            self.assertEqual("123", artist_rows[0]["appleArtistId"])
            self.assertIn("1", static)
            self.assertEqual(before_snapshot, snapshot.read_bytes())
            self.assertEqual(before_static, static_file.read_bytes())

    def test_snapshot_loader_accepts_gzip_and_ignores_optional_header_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = Path(temporary) / "snapshot.json.gz"
            value = {
                "payloadRows": [
                    ["postId", "canonicalUrl", "generatedAt", "storefront", "payloadJson", "status", "error"],
                    ["1", "/1", "2026", "FR", json.dumps({"postId": "1", "categories": []}), "READY", ""],
                ],
                "artistRows": [
                    ["artistKey", "canonicalName", "registrySchemaVersion", "catalogueSchemaVersion", "appleArtistId", "musicBrainzId", "identityConfidence", "status", "catalogueJson"],
                    ["artist", "Artist", 1, 1, "123", "", "HIGH", "RESOLVED", json.dumps({"categories": []})],
                ],
            }
            with gzip.open(snapshot, "wt", encoding="utf-8") as target:
                json.dump(value, target)

            before = snapshot.read_bytes()
            payload_rows, artist_rows = audit_module.load_backend_snapshot(snapshot)

            self.assertEqual(["1"], [row["postId"] for row in payload_rows])
            self.assertEqual(["artist"], [row["artistKey"] for row in artist_rows])
            self.assertEqual(before, snapshot.read_bytes())

    def test_exact_artist_label_corroborated_by_title_is_a_strong_subject_signal(self):
        post = {
            "postId": "1",
            "title": "Doom Metal Legends The Obsessed in Paris in the Fall!",
            "labels": ["The Obsessed", "Paris"],
        }

        detected = audit_module.detect_subject(post, self.registry)

        self.assertEqual("ORDINARY_SINGLE_SUBJECT", detected["taxonomy"])
        self.assertEqual("The Obsessed", detected["name"])

    def test_v2_single_source_artist_corroborated_by_title_beats_context_label(self):
        post = {
            "postId": "1",
            "title": "Doom Metal Legends The Obsessed in Paris in the Fall!",
            "labels": ["Paris"],
        }
        current = payload(
            "1", post["title"], ["The Obsessed"], "39276087",
            [item("x", "The Obsessed", "39276087")], 2, ["the-obsessed"],
        )
        result = audit_module.build_audit(
            [post], [{"postId": "1", "status": "READY", "payload": current}], [],
            self.registry, {"1": current},
        )

        record = result["records"][0]
        self.assertEqual("The Obsessed", record["detectedAuthoritativeSubject"])
        self.assertIn("HEALTHY_V2", record["flags"])


if __name__ == "__main__":
    unittest.main()
