import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "plan_apple_archive_repair.py"
SPEC = importlib.util.spec_from_file_location("apple_archive_repair_plan", SCRIPT)
planner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(planner)


def item(stable_id, creator, artist_id, category="LISTEN", title=None, provenance=None):
    value = {"stableId": stable_id, "creator": creator, "appleArtistId": artist_id, "category": category, "title": title or stable_id}
    if provenance:
        value["recommendationProvenance"] = provenance
    return value


def payload(post_id, title, primary, artist_id, items, ownership=None, keys=None):
    groups = []
    for category in planner.CATEGORIES:
        selected = [value for value in items if value["category"] == category]
        if selected:
            groups.append({"category": category, "items": selected})
    value = {"postId": post_id, "subject": {"title": title, "primaryArtists": primary}, "identity": {"level": "HIGH", "artistId": artist_id}, "categories": groups}
    if ownership:
        value["diagnostics"] = {"ownershipVersion": ownership, "artistKeys": keys or [], "sourceArtistKeys": keys or []}
    return value


class AppleArchiveRepairPlanTests(unittest.TestCase):
    def setUp(self):
        self.registry = {"artists": [
            {"canonicalName": "Anthrax", "slug": "anthrax", "members": ["Scott Ian", "Charlie Benante"]},
            {"canonicalName": "Dopelord", "slug": "dopelord"},
            {"canonicalName": "The Varukers", "slug": "the-varukers", "aliases": ["Varukers"]},
            {"canonicalName": "Whiplash", "slug": "whiplash"},
            {"canonicalName": "Charli xcx", "slug": "charli-xcx"},
            {"canonicalName": "Healthy Artist", "slug": "healthy-artist"},
        ]}

    def fixture(self):
        rows, audit_records, artists = [], [], []
        def add(post_id, subject, key, current, apple_id, items, flags=None, ownership=None, taxonomy="ORDINARY_SINGLE_SUBJECT", static=True, status="READY", catalogue=True, blogger=True, catalogue_id=None):
            catalogue_id = apple_id if catalogue_id is None else catalogue_id
            value = payload(post_id, subject + " returns", current, apple_id, items, ownership, [key]) if status == "READY" else {"postId": post_id, "categories": []}
            rows.append({"postId": post_id, "status": status, "generatedAt": "2026-01-01", "payload": value, "rowNumber": len(rows) + 2})
            audit_records.append({"postId": post_id, "url": "/" + post_id, "title": subject + " returns", "bloggerExists": blogger, "backendStatus": status, "taxonomy": taxonomy, "currentPrimaryArtists": current, "currentArtistKeys": [key], "currentSourceArtistKeys": [key] if ownership else [], "ownershipVersion": ownership, "detectedAuthoritativeSubject": subject if taxonomy == "ORDINARY_SINGLE_SUBJECT" else None, "detectedAuthoritativeArtistKey": key if taxonomy == "ORDINARY_SINGLE_SUBJECT" else None, "identityConfidence": "HIGH", "backendAppleArtistIds": [apple_id] if apple_id else [], "catalogueArtistKey": key if catalogue else None, "catalogueArtistName": subject if catalogue else None, "catalogueAppleArtistId": catalogue_id if catalogue else None, "historicalRecoveryExactEvidence": bool(items), "staticPayloadPresent": static, "flags": flags or []})
            if catalogue and key not in {row["artistKey"] for row in artists}:
                artists.append({"artistKey": key, "canonicalName": subject, "appleArtistId": catalogue_id, "status": "RESOLVED", "catalogue": {"categories": [{"category": "LISTEN", "items": [item("catalogue", subject, catalogue_id)]}]}})
        add("v2", "Healthy Artist", "healthy-artist", ["Healthy Artist"], "1", [item("v2", "Healthy Artist", "1")], ["HEALTHY_V2"], 2)
        related = item("s", "Scott Ian", "2", "READ")
        related["relevanceReason"] = "Scott Ian is a member of the primary artist discussed in the article."
        add("anthrax", "Anthrax", "anthrax", ["Anthrax", "Video"], "80417", [item("a", "Anthrax", "80417"), related], ["LEGACY_OWNERSHIP", "CONTEXT_AS_ARTIST"])
        add("dopelord", "Dopelord", "dopelord", ["Dopelord", "Paris"], "10", [item("d", "Dopelord", "10"), item("bad", "Charli xcx", "432942256")], ["CONTEXT_AS_ARTIST", "CHARLI_CONTAMINATION_SUSPECTED", "SHARED_SUSPICIOUS_APPLE_ID"])
        add("varukers", "The Varukers", "the-varukers", ["Varukers", "Paris"], "432942256", [item("bad", "Charli xcx", "432942256")], ["CONTEXT_AS_ARTIST", "SHARED_SUSPICIOUS_APPLE_ID"], catalogue=False)
        add("whiplash", "Whiplash", "whiplash", ["Whiplash", "Paris"], "432942256", [item("bad", "Charli xcx", "432942256")], ["CONTEXT_AS_ARTIST", "SHARED_SUSPICIOUS_APPLE_ID"], catalogue_id="63387553")
        add("legacy", "Healthy Artist", "healthy-artist", ["Healthy Artist"], "1", [item("l", "Healthy Artist", "1")], ["LEGACY_OWNERSHIP"])
        add("circular", "Dopelord", "dopelord", ["Dopelord"], "10", [item("x", "Other", "10")], ["HISTORICAL_RECOVERY_UNPROVEN"])
        add("unresolved", "Healthy Artist", "healthy-artist", ["Healthy Artist"], "", [], [], None, status="EMPTY", catalogue=False)
        add("playlist", "Playlist", "playlist", [], "", [], [], None, taxonomy="PLAYLIST_MULTI_ARTIST", catalogue=False)
        add("ambiguous", "Ambiguous", "ambiguous", [], "", [], [], None, taxonomy="AMBIGUOUS_NO_CLEAR_TITLE", catalogue=False)
        add("orphan", "Orphan", "orphan", [], "", [], [], None, taxonomy="ORPHAN_DELETED", catalogue=False, blogger=False)
        add("charli", "Charli xcx", "charli-xcx", ["Charli xcx"], "20", [item("brat", "Charli xcx", "20")], ["CHARLI_PRESENT"])
        add("static-gap", "Healthy Artist", "healthy-artist", ["Healthy Artist"], "1", [item("g", "Healthy Artist", "1")], ["LEGACY_OWNERSHIP"], None, static=False)
        rows.append({**rows[0], "generatedAt": "2025-01-01", "rowNumber": 99})
        return {"records": audit_records, "historicalRecoveryRisk": [{"postIds": ["circular"]}]}, rows, artists

    def test_required_repair_and_preservation_cases(self):
        ownership, rows, artists = self.fixture()
        result = planner.build_plan(ownership, rows, artists, self.registry)
        records = {row["postId"]: row for row in result["records"]}
        self.assertEqual("KEEP_V2", records["v2"]["ownershipAction"])
        self.assertEqual(("A", "MIGRATE_LEGACY_OWNERSHIP", 2), (records["anthrax"]["repairTier"], records["anthrax"]["ownershipAction"], records["anthrax"]["preservableExactItemCount"] + records["anthrax"]["preservableRelationshipItemCount"]))
        self.assertEqual(1, records["dopelord"]["rejectedContaminatedItemCount"])
        self.assertEqual(1, records["dopelord"]["preservableListenCount"])
        for key in ("varukers", "whiplash"):
            self.assertEqual("A", records[key]["repairTier"])
            self.assertEqual(0, records[key]["preservableListenCount"])
        self.assertTrue(records["varukers"]["requiresAppleResolution"])
        self.assertEqual("REUSE_TRUSTED_CATALOGUE", records["whiplash"]["catalogueAction"])
        self.assertEqual(("B", "MIGRATE_LEGACY_OWNERSHIP"), (records["legacy"]["repairTier"], records["legacy"]["ownershipAction"]))
        self.assertNotEqual("B", records["circular"]["repairTier"])
        self.assertEqual("C", records["unresolved"]["repairTier"])
        self.assertEqual("D", records["playlist"]["repairTier"])
        self.assertEqual("D", records["ambiguous"]["repairTier"])
        self.assertEqual("ORPHAN_NO_ACTION", records["orphan"]["ownershipAction"])
        self.assertEqual("B", records["charli"]["repairTier"])
        self.assertEqual("STATIC_CREATE_EXPECTED", records["static-gap"]["staticAction"])
        self.assertEqual(2, records["v2"]["duplicatePhysicalRowCount"])
        self.assertEqual(2, records["v2"]["selectedCanonicalRowNumber"])

    def test_healthy_v2_without_legacy_identity_level_and_strong_stored_subject_are_kept(self):
        ownership, rows, artists = self.fixture()
        v2 = next(record for record in ownership["records"] if record["postId"] == "v2")
        v2["identityConfidence"] = None
        v2["taxonomy"] = "ORDINARY_SINGLE_SUBJECT"
        result = planner.build_plan(ownership, rows, artists, self.registry)
        record = next(row for row in result["records"] if row["postId"] == "v2")
        self.assertEqual(("B", "KEEP_V2"), (record["repairTier"], record["ownershipAction"]))

    def test_python_tier_mirror_matches_step_four_boundaries(self):
        base = {"taxonomy": "ORDINARY_SINGLE_SUBJECT", "bloggerExists": True, "authoritativeSubject": "Artist", "authoritativeArtistKey": "artist", "identityConfidence": "HIGH", "hasRecommendations": True, "cataloguePresent": True, "catalogueResolved": True, "catalogueArtistKey": "artist", "catalogueArtistName": "Artist", "catalogueAppleArtistId": "1", "payloadAppleArtistId": "1", "catalogueValid": True, "exactSubjectEvidence": True}
        classify = lambda **changes: planner.repair_eligibility({**base, **changes})["tier"]
        self.assertEqual("B", classify())
        self.assertEqual("A", classify(contextPromotedAsArtist=True))
        self.assertEqual("A", classify(unprovenHistoricalRecovery=True))
        self.assertEqual("A", classify(exactSubjectEvidence=False))
        self.assertEqual("C", classify(catalogueResolved=False, catalogueAppleArtistId=""))
        self.assertEqual("C", classify(hasRecommendations=False))
        self.assertEqual("D", classify(taxonomy="PLAYLIST_MULTI_ARTIST"))


if __name__ == "__main__":
    unittest.main()
