import unittest

from concert_calendar.venue_articles import build_venue_article_associations


def entry(title, url, date="2026-01-01", labels=None):
    return {
        "title": {"$t": title},
        "published": {"$t": date + "T12:00:00.000Z"},
        "category": [
            {"term": label}
            for label in (labels or ["Concert Review"])
        ],
        "link": [
            {
                "rel": "alternate",
                "type": "text/html",
                "href": url,
            }
        ],
    }


class VenueArticleAssociationTests(unittest.TestCase):

    def test_structured_review_resolves_known_venue(self):
        entries = [
            entry(
                "Artist @ Le Trianon, Paris – March 1st, 2026",
                "https://www.electriceyerock.com/2026/03/test.html",
            )
        ]

        result, diagnostics = build_venue_article_associations(
            entries,
            known_venues={"Le Trianon"},
            include_diagnostics=True,
        )

        self.assertEqual(len(result["Le Trianon"]), 1)
        self.assertEqual(
            result["Le Trianon"][0]["title"],
            "Artist @ Le Trianon, Paris – March 1st, 2026",
        )
        self.assertEqual(diagnostics["unresolvedReviews"], [])

    def test_historical_alias_resolves_to_canonical_venue(self):
        entries = [
            entry(
                "Artist @ Zénith, Paris - January 2nd, 2020",
                "https://www.electriceyerock.com/2020/01/test.html",
            )
        ]

        result = build_venue_article_associations(
            entries,
            known_venues={"Le Zénith Paris – La Villette"},
        )

        self.assertEqual(
            len(result["Le Zénith Paris – La Villette"]),
            1,
        )

    def test_non_review_is_ignored(self):
        entries = [
            entry(
                "Artist announces Paris show",
                "https://www.electriceyerock.com/2026/01/news.html",
                labels=["News"],
            )
        ]

        result, diagnostics = build_venue_article_associations(
            entries,
            known_venues={"Bataclan"},
            include_diagnostics=True,
        )

        self.assertEqual(result["Bataclan"], [])
        self.assertEqual(diagnostics["concertReviews"], 0)

    def test_unresolved_review_is_reported_not_guessed(self):
        entries = [
            entry(
                "Artist @ Imaginary Hall, Paris – March 1st, 2026",
                "https://www.electriceyerock.com/2026/03/unknown.html",
            )
        ]

        result, diagnostics = build_venue_article_associations(
            entries,
            known_venues={"Bataclan"},
            include_diagnostics=True,
        )

        self.assertEqual(result["Bataclan"], [])
        self.assertEqual(
            diagnostics["unresolvedReviews"],
            [
                {
                    "title": "Artist @ Imaginary Hall, Paris – March 1st, 2026",
                    "venue": "Imaginary Hall",
                    "city": "Paris",
                }
            ],
        )

    def test_explicit_hellfest_review_without_at_sign(self):
        entries = [
            entry(
                "Hellfest 2026",
                "https://www.electriceyerock.com/2026/06/hellfest-2026.html",
            )
        ]

        result = build_venue_article_associations(
            entries,
            known_venues={"Hellfest"},
        )

        self.assertEqual(len(result["Hellfest"]), 1)


if __name__ == "__main__":
    unittest.main()
