import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from concert_calendar.genre_index import (
    build_genre_index,
    normalized_phrase_in_text,
)


def make_content_index(artists, articles):
    return {
        "artists": artists,
        "articles": articles,
    }


def article(title, labels, artists, article_type="other"):
    return {
        "t": title,
        "l": labels,
        "a": artists,
        "y": article_type,
    }


class GenreIndexEvidenceTests(unittest.TestCase):
    def build(self, artists, articles):
        with tempfile.TemporaryDirectory() as tmp:
            mappings = Path(tmp) / "genre_mappings.json"
            mappings.write_text(
                json.dumps({"artists": []}),
                encoding="utf-8",
            )

            with (
                patch(
                    "concert_calendar.genre_index.resolve_musicbrainz_genres",
                    return_value={},
                ),
                patch(
                    "concert_calendar.genre_index.musicbrainz_relationship_genres",
                    return_value={},
                ),
                patch(
                    "concert_calendar.genre_index.wikidata_detailed_lookup",
                    return_value={},
                ),
                patch(
                    "concert_calendar.genre_index.apple_detailed_lookup",
                    return_value={},
                ),
            ):
                return build_genre_index(
                    mappings_path=mappings,
                    content_index=make_content_index(artists, articles),
                )

    @staticmethod
    def genres_for(index, artist):
        return {
            genre["name"]
            for genre in index["genres"]
            if artist in genre.get("directArtists", [])
        }

    def test_artist_named_in_title_accepts_article_genre_labels(self):
        articles = [
            article(
                "Album Review: Jason Isbell - Foxes in the Snow",
                [
                    "Album Review",
                    "Americana",
                    "Country",
                    "Folk",
                    "Jason Isbell",
                ],
                ["jason-isbell"],
                "album_review",
            ),
            article(
                "Jason Isbell & the 400 Unit @ Café de la Danse, Paris",
                [
                    "Alt-Country",
                    "Americana",
                    "Country",
                    "Folk",
                    "Rock",
                    "Southern Rock",
                ],
                ["400-unit", "jason-isbell"],
                "concert_review",
            ),
        ]
        artists = {
            "jason-isbell": {
                "n": "Jason Isbell",
                "ar": [0, 1],
                "identity": {"genres": []},
            }
        }

        index = self.build(artists, articles)
        genres = self.genres_for(index, "Jason Isbell")

        self.assertIn("Alt-Country", genres)
        self.assertIn("Americana", genres)
        self.assertIn("Country", genres)
        self.assertIn("Folk", genres)
        self.assertIn("Rock", genres)

    def test_generic_roundup_does_not_leak_genres_to_artist(self):
        articles = [
            article(
                "December 22nd, 2023: The Best of 2023",
                [
                    "Alt-Country",
                    "Americana",
                    "Classic Rock",
                    "Country",
                    "Death Metal",
                    "Folk",
                    "Heavy Metal",
                    "Metal",
                    "Rock",
                ],
                ["400-unit", "jason-isbell", "rhiannon-giddens"],
                "other",
            )
        ]
        artists = {
            "jason-isbell": {
                "n": "Jason Isbell",
                "ar": [0],
                "identity": {"genres": []},
            }
        }

        index = self.build(artists, articles)
        genres = self.genres_for(index, "Jason Isbell")

        self.assertNotIn("Death Metal", genres)
        self.assertNotIn("Heavy Metal", genres)
        self.assertNotIn("Metal", genres)
        self.assertNotIn("Classic Rock", genres)

    def test_generic_playlist_does_not_leak_marillion_genres(self):
        articles = [
            article(
                "Friday's Playlist: 2023 Concerts",
                [
                    "Blues Rock",
                    "Death Metal",
                    "Heavy Metal",
                    "Marillion",
                    "Metal",
                    "Rock",
                ],
                ["guns-n-roses", "marillion"],
                "playlist",
            )
        ]
        artists = {
            "marillion": {
                "n": "Marillion",
                "ar": [0],
                "identity": {"genres": []},
            }
        }

        index = self.build(artists, articles)
        genres = self.genres_for(index, "Marillion")

        self.assertNotIn("Blues Rock", genres)
        self.assertNotIn("Death Metal", genres)
        self.assertNotIn("Heavy Metal", genres)
        self.assertNotIn("Metal", genres)

    def test_marillion_keeps_dedicated_genres_without_playlist_contamination(self):
        articles = [
            article(
                "Friday's Playlist: 2023 Concerts",
                [
                    "Blues Rock",
                    "Death Metal",
                    "Heavy Metal",
                    "Marillion",
                    "Metal",
                    "Rock",
                ],
                ["guns-n-roses", "marillion"],
                "playlist",
            ),
            article(
                "Marillion @ Le Trianon, Paris - November 13th, 2023",
                [
                    "Marillion",
                    "Prog",
                    "Prog Rock",
                    "Progressive Rock",
                    "Rock",
                ],
                ["marillion"],
                "concert_review",
            ),
        ]
        artists = {
            "marillion": {
                "n": "Marillion",
                "ar": [0, 1],
                "identity": {"genres": []},
            }
        }

        index = self.build(artists, articles)
        genres = self.genres_for(index, "Marillion")

        self.assertIn("Progressive Rock", genres)
        self.assertIn("Rock", genres)
        self.assertNotIn("Blues Rock", genres)
        self.assertNotIn("Death Metal", genres)
        self.assertNotIn("Heavy Metal", genres)
        self.assertNotIn("Metal", genres)

    def test_artist_named_in_multi_artist_title_can_use_labels(self):
        articles = [
            article(
                "Dimmu Borgir, Behemoth and Dark Funeral To Perform Black Metal Ritual",
                ["Black Metal", "Metal"],
                ["behemoth", "dark-funeral", "dimmu-borgir"],
                "news",
            )
        ]
        artists = {
            "behemoth": {
                "n": "Behemoth",
                "ar": [0],
                "identity": {"genres": []},
            }
        }

        index = self.build(artists, articles)
        genres = self.genres_for(index, "Behemoth")

        self.assertIn("Black Metal", genres)
        self.assertIn("Metal", genres)

    def test_playlist_title_genre_requires_matching_genre_label(self):
        articles = [
            article(
                "Friday's Playlist: Rap and Hip Hop",
                ["Hip Hop", "Playlist", "Public Enemy"],
                ["public-enemy"],
                "playlist",
            )
        ]
        artists = {
            "public-enemy": {
                "n": "Public Enemy",
                "ar": [0],
                "identity": {"genres": []},
            }
        }

        index = self.build(artists, articles)
        genres = self.genres_for(index, "Public Enemy")

        self.assertIn("Hip-Hop", genres)

    def test_non_playlist_title_genre_does_not_apply_to_unnamed_artist(self):
        articles = [
            article(
                "Swedish Rock Invasion Hits Paris with Blues Pills",
                ["Rock", "Blues Pills", "Spiders"],
                ["blues-pills", "spiders"],
                "news",
            )
        ]
        artists = {
            "spiders": {
                "n": "Spiders",
                "ar": [0],
                "identity": {"genres": []},
            }
        }

        index = self.build(artists, articles)
        genres = self.genres_for(index, "Spiders")

        self.assertNotIn("Rock", genres)

    def test_phrase_matching_uses_token_boundaries(self):
        self.assertTrue(
            normalized_phrase_in_text(
                "Ash",
                "Ash @ Le Trabendo, Paris",
            )
        )
        self.assertFalse(
            normalized_phrase_in_text(
                "Ash",
                "Nashville Rock Night",
            )
        )


if __name__ == "__main__":
    unittest.main()
