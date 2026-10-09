"""Tests for the isolated Electric Eye newsletter article extractor."""

import unittest

from newsletter.articles import clean_summary, extract_articles


def entry(post_id, title, published, labels, summary="Test summary", image=None):
    return {
        "id": {"$t": f"tag:blogger.com,1999:blog-123.post-{post_id}"},
        "title": {"$t": title},
        "published": {"$t": published},
        "category": [{"term": label} for label in labels],
        "link": [{
            "rel": "alternate",
            "type": "text/html",
            "href": f"https://www.electriceyerock.com/2026/09/article-{post_id}.html",
        }],
        "summary": {"$t": summary},
        "media$thumbnail": {"url": image} if image else {},
    }


PERIOD = {
    "start": "2026-09-01",
    "end_exclusive": "2026-10-01",
}


class NewsletterArticleTests(unittest.TestCase):

    def test_categories_and_empty_interviews(self):
        entries = [
            entry("1", "Live Review", "2026-09-12T12:00:00+02:00",
                  ["Concert Review"]),
            entry("2", "Album Review", "2026-09-14T12:00:00+02:00",
                  ["Album Review"]),
            entry("3", "New Single", "2026-09-16T12:00:00+02:00",
                  ["News"]),
            entry("4", "Friday's Playlist", "2026-09-18T12:00:00+02:00",
                  ["Friday's Playlist"]),
        ]
        result = extract_articles(entries, PERIOD)

        self.assertEqual(len(result["concert_review"]), 1)
        self.assertEqual(len(result["album_review"]), 1)
        self.assertEqual(len(result["news"]), 1)
        self.assertEqual(len(result["playlist"]), 1)
        self.assertEqual(result["interview"], [])

    def test_paris_timezone_boundary(self):
        entries = [
            entry("5", "September News",
                  "2026-09-30T21:30:00Z", ["News"]),
            entry("6", "October News",
                  "2026-09-30T22:30:00Z", ["News"]),
        ]
        result = extract_articles(entries, PERIOD)
        self.assertEqual(
            [article["id"] for article in result["news"]],
            ["5"],
        )

    def test_duplicate_articles(self):
        article = entry("7", "Interview",
                        "2026-09-20T12:00:00+02:00",
                        ["Interview"])
        result = extract_articles([article, article], PERIOD)
        self.assertEqual(len(result["interview"]), 1)

    def test_summary_and_image(self):
        image = "https://blogger.googleusercontent.com/test.jpg"
        article = entry(
            "8", "Concert Review",
            "2026-09-15T12:00:00+02:00",
            ["Concert Review"],
            summary="<p>A &amp; B <strong>live</strong>.</p>",
            image=image,
        )
        result = extract_articles([article], PERIOD)
        item = result["concert_review"][0]

        self.assertEqual(item["summary"], "A & B live.")
        self.assertEqual(item["image"], image)
        self.assertTrue(item["url"].startswith("https://"))

    def test_truncated_summary(self):
        result = clean_summary("This is a longer summary.", limit=15)
        self.assertEqual(result, "This is a…")


if __name__ == "__main__":
    unittest.main()
