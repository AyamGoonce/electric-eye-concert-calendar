import tempfile
import unittest
from pathlib import Path

import concert_calendar.content_index as content_index
from concert_calendar.content_index import build_index, classify_article, enrich_events, write_assets
from concert_calendar.models import ConcertEvent


def entry(title, labels, date="2026-01-01", image=None):
    value = {
        "id": {"$t": "tag:blogger.com,1999:blog-1.post-123456"},
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
    def test_editorial_prefix_labels_never_seed_pseudo_artists(self):
        index = build_index([
            entry(
                "Album Review: Alter Bridge - Alter Bridge",
                ["Album Review", "Alter Bridge"],
                "2026-01-01",
            ),
            entry(
                "Album Review: Kreator - Krushers Of The World",
                ["Album Review", "Kreator"],
                "2026-01-02",
            ),
            entry(
                "Album Review - The Hellacopters - Overdriver",
                ["Album Review", "The Hellacopters"],
                "2026-01-03",
            ),
            entry(
                "Concert Review: Example Artist live in Paris",
                ["Concert Review", "Example Artist"],
                "2026-01-04",
            ),
        ], generated_at="2026-01-05T00:00:00Z")

        self.assertNotIn("album-review", index["artists"])
        self.assertNotIn("concert-review", index["artists"])
        self.assertEqual(["alter-bridge"], index["articles"][0]["a"])
        self.assertEqual(["kreator"], index["articles"][1]["a"])
        self.assertEqual(["the-hellacopters"], index["articles"][2]["a"])

    def test_obituary_category_does_not_create_band_match_without_title_evidence(self):
        index = build_index([
            entry(
                "Obituary @ Bataclan, Paris - January 1st, 2026",
                ["Concert Review", "Obituary"],
                "2026-01-01",
            ),
            entry(
                "Frank Beard, ZZ Top drummer, dies aged 76",
                ["News", "Obituary", "Frank Beard", "ZZ Top"],
                "2026-01-02",
            ),
        ], generated_at="2026-01-03T00:00:00Z")

        self.assertIn("obituary", index["artists"])
        self.assertEqual([0], index["artists"]["obituary"]["ar"])
        self.assertIn("obituary", index["articles"][0]["a"])
        self.assertNotIn("obituary", index["articles"][1]["a"])

        beat = build_index([
            entry("BEAT @ Bataclan, Paris - January 1st, 2026", ["Concert Review", "BEAT"]),
        ], generated_at="2026-01-03T00:00:00Z")
        self.assertIn("beat", beat["artists"])
        self.assertIn("beat", beat["articles"][0]["a"])

    def test_titled_subjects_do_not_inherit_billmates_or_members(self):
        index = build_index([
            entry("Garbage @ Le Zénith, Paris - May 25th, 2026", ["Concert Review", "Garbage", "Skunk Anansie"], "2026-01-01"),
            entry("Skunk Anansie @ Le Zénith, Paris - May 25th, 2026", ["Concert Review", "Garbage", "Skunk Anansie"], "2026-01-02"),
            entry("Garbage and Skunk Anansie in Paris in May", ["Concert", "Garbage", "Skunk Anansie"], "2026-01-03"),
            entry("A Conversation with Drink The Sea - Video Interview (video)", ["Interview", "Drink The Sea", "Alain Johannes", "Loading Data"], "2026-01-04"),
            entry("Loading Data @ Point Éphémère, Paris - December 18, 2014", ["Concert Review", "Loading Data"], "2026-01-05"),
            entry("Hollywood Vampires return to Paris", ["Hollywood Vampires", "Alice Cooper", "Joe Perry", "Johnny Depp"], "2026-01-06"),
        ], generated_at="2026-01-07T00:00:00Z")

        self.assertEqual(["garbage"], index["articles"][0]["a"])
        self.assertEqual(["skunk-anansie"], index["articles"][1]["a"])
        self.assertEqual({"garbage", "skunk-anansie"}, set(index["articles"][2]["a"]))
        self.assertEqual(["drink-the-sea"], index["articles"][3]["a"])
        self.assertEqual(["loading-data"], index["articles"][4]["a"])
        self.assertEqual(["hollywood-vampires"], index["articles"][5]["a"])

    def test_schema_two_identity_record_and_human_exports(self):
        index = build_index([
            entry("BEAT @ Bataclan, Paris - January 1st, 2026", ["Concert Review", "BEAT"]),
        ], generated_at="2026-01-01T00:00:00Z")
        identity = index["artists"]["beat"]["identity"]
        self.assertEqual(2, index["schema"])
        self.assertEqual("BEAT", identity["canonicalName"])
        self.assertEqual("common_word", identity["ambiguityClass"])
        self.assertIn("Tony Levin", identity["members"])
        self.assertEqual(["123456"], identity["articleIds"])

        with tempfile.TemporaryDirectory() as directory:
            write_assets(directory, index)
            json_export = Path(directory, "artist-index.json").read_text()
            csv_export = Path(directory, "artist-index.csv").read_text()
            associations = Path(directory, "artist-article-associations.csv").read_text()
        self.assertIn('"canonicalName": "BEAT"', json_export)
        self.assertIn('"structuralLabels": [', json_export)
        self.assertIn('"obituary"', json_export)
        self.assertIn("canonicalName,slug,aliases", csv_export)
        self.assertIn("beat,BEAT,123456", associations)

    def test_article_url_rejects_unsafe_scheme(self):
        unsafe = entry("Unsafe article", ["News"])
        unsafe["link"][0]["href"] = "javascript:alert(1)"

        index = build_index([unsafe], generated_at="2026-01-01T00:00:00Z")

        self.assertEqual(index["articles"], [])

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

    def test_manual_artist_article_association_survives_automatic_miss(self):
        manual_url = "https://www.electriceyerock.com/2026/01/manual-artist.html"
        item = entry("A genuinely miscellaneous post", ["News"], "2026-01-04")
        item["link"][0]["href"] = manual_url

        content_index.MANUAL_ARTIST_ARTICLES["Engelbert Humperdinck"] = {manual_url}
        try:
            index = build_index(
                [item],
                generated_at="2026-01-01T00:00:00Z",
            )
        finally:
            del content_index.MANUAL_ARTIST_ARTICLES["Engelbert Humperdinck"]

        self.assertIn("engelbert-humperdinck", index["artists"])
        self.assertEqual(
            index["lookup"]["engelbert humperdinck"],
            "engelbert-humperdinck",
        )
        self.assertEqual(index["artists"]["engelbert-humperdinck"]["ar"], [0])

    def test_prose_ambiguous_artist_remains_available_to_structured_lookup(self):
        index = build_index([
            entry("Live @ Bataclan, Paris - January 1st, 2026", ["Concert Review", "Live"]),
        ], generated_at="2026-01-01T00:00:00Z")
        self.assertIn("live", index["artists"])
        self.assertEqual("live", index["lookup"]["live"])
        self.assertIn("Live", index["diagnostics"]["proseAutolinkExclusions"])

    def test_down_stays_indexed_and_compact_but_is_excluded_from_free_prose(self):
        index = build_index([
            entry("Down @ Bataclan, Paris - January 1st, 2026", ["Concert Review", "Down"]),
        ], generated_at="2026-01-01T00:00:00Z")
        event = ConcertEvent(
            date="2027-01-01", headliner="Down", venue="Bataclan",
            city="Paris", department="75",
        )
        enrich_events([event], index)

        self.assertIn("down", index["artists"])
        self.assertEqual("down", index["lookup"]["down"])
        self.assertEqual("down", event.electric_eye_links[0]["slug"])
        self.assertEqual("Down", event.electric_eye_links[0]["display"])
        with tempfile.TemporaryDirectory() as directory:
            write_assets(directory, index)
            compact = Path(directory, "electric-eye-artist-lookup.js").read_text()
        self.assertIn('"Down":"down"', compact)
        self.assertIn('"proseAutolinkExclusions":["down"]', compact)

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
        self.assertEqual(event.electric_eye_links[0]["display"], "The Example")
        self.assertEqual(event.electric_eye_links[0]["role"], "headliner")
        self.assertEqual(event.image_source, "Electric Eye concert review")
        self.assertEqual(event.electric_eye_links[0]["total"], 1)

    def test_multi_artist_event_uses_unique_aggregate_article_count(self):
        entries = [
            entry("Alpha @ Bataclan, Paris - January 1st, 2026", ["Concert Review", "Alpha"], "2026-01-01"),
            entry("Beta @ Bataclan, Paris - January 2nd, 2026", ["Concert Review", "Beta"], "2026-01-02"),
            entry("Alpha and Beta announce dates", ["News", "Alpha", "Beta"], "2026-01-03"),
        ]
        index = build_index(entries, generated_at="2026-01-01T00:00:00Z")
        event = ConcertEvent(date="2027-01-01", headliner="Alpha", openers=["Beta"], venue="Bataclan", city="Paris", department="75")
        enrich_events([event], index)
        self.assertEqual(len(event.electric_eye_links), 2)
        self.assertEqual(event.electric_eye_links[0]["total"], 3)
        self.assertEqual(["headliner", "opener"], [item["role"] for item in event.electric_eye_links])

    def test_support_review_hero_never_replaces_official_event_image(self):
        image = "https://blogger.googleusercontent.com/example/s72-c/photo.jpg"
        index = build_index([entry("Support @ Club, Paris - January 1st, 2026", ["Concert Review", "Support"], image=image)])
        event = ConcertEvent(date="2027-01-01", headliner="Unindexed", openers=["Support"], venue="Bataclan", city="Paris", department="75", image_url="https://official.example/event.jpg", image_source="Bataclan")
        enrich_events([event], index)
        self.assertEqual(event.image_url, "https://official.example/event.jpg")
        self.assertEqual(event.image_source, "Bataclan")

    def test_reviewed_legacy_house_title_classification(self):
        self.assertEqual(classify_article("Band @ Bataclan, Paris - June 30th, 2025", []), "concert_review")
        self.assertEqual(classify_article("Interview: Band", []), "interview")
        self.assertEqual(classify_article("Album Review: Band - Record", []), "album_review")
        self.assertEqual(classify_article("Band announces dates", ["News"]), "news")
        self.assertEqual(classify_article("Band To Perform At Le Zénith Next Fall", []), "news")
        self.assertEqual(classify_article("A genuinely miscellaneous post", []), "other")

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
        self.assertIn('rootSelector:".post-body, .entry-content"', script)
        for excluded in (
            "a,script,style,noscript,code,pre",
            "button,input,select,textarea",
            "iframe,object,embed",
            "nav,[role='navigation'],[role='button']",
            ".ad,.adsbygoogle",
            "[data-ee-no-autolink], .ee-no-autolink",
        ):
            self.assertIn(excluded, script)
        self.assertNotIn(".widget", script)
        self.assertNotIn("ElectricEyeContentIndex", script)

    def test_autolinker_allows_blogger_post_body_inside_blog_widget(self):
        script = Path("concert_calendar/static/artist-autolinker.js").read_text()
        blogger_fixture = """
          <div class="widget Blog">
            <div class="post-body"><p>Sparks played in Paris.</p></div>
          </div>
          <aside class="widget"><p>Sparks sidebar item.</p></aside>
        """

        self.assertIn('<div class="widget Blog">', blogger_fixture)
        self.assertIn('<div class="post-body">', blogger_fixture)
        self.assertNotIn(".widget", script)
        self.assertIn('document.querySelectorAll(config.rootSelector)', script)
        self.assertIn('link.href=data.artistPage+encodeURIComponent(slug)', script)

    def test_autolinker_sidebar_and_protected_content_contract(self):
        script = Path("concert_calendar/static/artist-autolinker.js").read_text()
        protected_fixture = """
          <aside class="widget">Sparks sidebar item.</aside>
          <div class="post-body">
            <a href="/existing">Sparks</a>
            <ins class="adsbygoogle">Sparks</ins>
            <iframe title="Sparks embed"></iframe>
            <p data-ee-no-autolink>Sparks opted out.</p>
          </div>
        """

        self.assertIn('<aside class="widget">', protected_fixture)
        self.assertIn('rootSelector:".post-body, .entry-content"', script)
        for protected in ("a,script,style,noscript", ".adsbygoogle", "iframe", "[data-ee-no-autolink]"):
            self.assertIn(protected, script)

    def test_artist_page_groups_articles_and_links_exact_calendar_event(self):
        script = Path("concert_calendar/static/artist-page.js").read_text()
        for heading in ("Concert Reviews", "Interviews", "Album Reviews", "News", "Playlists"):
            self.assertIn(heading, script)
        self.assertIn('"#event-"+event.i', script)

    def test_event_coverage_page_deduplicates_urls_and_uses_all_event_artists(self):
        script = Path("concert_calendar/static/coverage-page.js").read_text()
        self.assertIn("new Map()", script)
        self.assertIn("articles.get(article.u)", script)
        self.assertIn("(event.ee||[]).map", script)
        self.assertIn("Related artists:", script)


if __name__ == "__main__":
    unittest.main()
