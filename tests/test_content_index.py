import unittest
from pathlib import Path

from concert_calendar.content_index import build_index, enrich_events
from concert_calendar.models import ConcertEvent


def entry(title, labels, date="2026-01-01", image=None):
    value = {
        "title": {"$t": title},
        "published": {"$t": f"{date}T12:00:00+01:00"},
        "category": [{"term": label} for label in labels],
        "link": [{
            "rel": "alternate", "type": "text/html",
            "href": "https://www.electriceyerock.com/post-" + date,
        }],
    }
    if image:
        value["media$thumbnail"] = {"url": image}
    return value


class ContentIndexTests(unittest.TestCase):
    def test_calendar_only_artist_cannot_create_index_identity(self):
        index = build_index([
            entry("Some general news", ["News", "Calendar Only Band"]),
        ], generated_at="2026-01-01T00:00:00Z")
        self.assertEqual(index["artists"], {})

    def test_article_types_associations_and_concert_hero_rules(self):
        image = "https://blogger.googleusercontent.com/example/s72-c/photo.jpg"
        entries = [
            entry("The Example @ Bataclan, Paris - January 1st, 2026", ["Concert", "Review", "Concert Review", "The Example"], "2026-01-01", image),
            entry("Album Review: The Example - Record", ["Album Review", "The Example"], "2025-12-01", "https://blogger.googleusercontent.com/example/s72-c/cover.jpg"),
            entry("The Example announce a tour", ["News", "The Example"], "2025-11-01"),
        ]
        index = build_index(entries, generated_at="2026-01-01T00:00:00Z")
        artist = index["artists"]["the-example"]
        self.assertEqual(len(artist["ar"]), 3)
        self.assertEqual(artist["crh"]["d"], "2026-01-01")
        self.assertIn("/s320-c/", artist["crh"]["im"])
        self.assertEqual(
            [article["y"] for article in index["articles"]],
            ["concert_review", "album_review", "news"],
        )
        self.assertNotIn("im", index["articles"][1])

    def test_ambiguous_artist_is_not_put_in_public_lookup(self):
        index = build_index([
            entry("Live @ Bataclan, Paris - January 1st, 2026", ["Concert Review", "Live"]),
        ], generated_at="2026-01-01T00:00:00Z")
        self.assertIn("live", index["artists"])
        self.assertNotIn("live", index["lookup"])

    def test_exact_index_match_enriches_links_and_prefers_review_hero(self):
        image = "https://blogger.googleusercontent.com/example/s72-c/photo.jpg"
        index = build_index([
            entry("The Example @ Bataclan, Paris - January 1st, 2026", ["Concert Review", "The Example"], image=image),
        ], generated_at="2026-01-01T00:00:00Z")
        event = ConcertEvent(
            date="2027-01-01", headliner="The Example", venue="Bataclan",
            city="Paris", department="75", image_url="https://official.example/image.jpg",
            image_source="Bataclan",
        )
        enrich_events([event], index)
        self.assertEqual(event.electric_eye_links[0]["slug"], "the-example")
        self.assertEqual(event.electric_eye_links[0]["role"], "headliner")
        self.assertEqual(event.image_source, "Electric Eye concert review")

    def test_unindexed_artist_keeps_official_image_without_ee_link(self):
        index = build_index([], generated_at="2026-01-01T00:00:00Z")
        event = ConcertEvent(
            date="2027-01-01", headliner="Calendar Only", venue="Bataclan",
            city="Paris", department="75", image_url="https://official.example/image.jpg",
            image_source="Bataclan",
        )
        enrich_events([event], index)
        self.assertIsNone(event.electric_eye_links)
        self.assertEqual(event.image_source, "Bataclan")

    def test_autolinker_contract_is_compact_first_occurrence_and_dom_safe(self):
        script = Path("concert_calendar/static/artist-autolinker.js").read_text()
        self.assertIn("allOccurrences:false", script)
        self.assertIn("linked.has(slug)", script)
        for excluded in ("a,script,style,noscript,code,pre", "iframe", "embed", "[data-ee-no-autolink]"):
            self.assertIn(excluded, script)
        self.assertNotIn("ElectricEyeContentIndex", script)

    def test_artist_page_groups_articles_and_links_exact_calendar_event(self):
        script = Path("concert_calendar/static/artist-page.js").read_text()
        for heading in ("Concert Reviews", "Interviews", "Album Reviews", "News", "Playlists"):
            self.assertIn(heading, script)
        self.assertIn('"#event-" + event.i', script)


if __name__ == "__main__":
    unittest.main()
