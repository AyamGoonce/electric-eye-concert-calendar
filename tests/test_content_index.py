import unittest
from pathlib import Path

from concert_calendar.content_index import build_index, classify_article, enrich_events
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
