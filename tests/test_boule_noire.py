import unittest
from unittest.mock import patch

from concert_calendar.scrapers import boule_noire


class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        return None


PRIMARY_HTML = """
<div id="programmation">
  <article class="elementor-post__card">
    <div class="elementor-post__text">
      <h3 class="elementor-post__title">
        <a href="https://laboule-noire.fr/existing/">Existing Artist</a>
      </h3>
      <div class="elementor-post__excerpt">
        <p>SAMEDI 24 OCTOBRE 2026 – 19H30</p>
      </div>
    </div>
  </article>

  <article class="elementor-post__card">
    <div class="elementor-post__text">
      <h3 class="elementor-post__title">
        <a href="https://laboule-noire.fr/moved/">Moved Artist</a>
      </h3>
      <div class="elementor-post__excerpt">
        <p>MARDI 27 OCTOBRE 2026 – 19H30</p>
      </div>
    </div>
  </article>
</div>
"""

IMPRESSION_HTML = """
<div id="programmation-impression">
  <article class="elementor-post category-en-cours">
    <div class="elementor-post__text">
      <p class="elementor-post__title">
        <a href="https://laboule-noire.fr/existing/">Existing Artist</a>
      </p>
      <div class="elementor-post__excerpt">
        <p>SAMEDI 24 OCTOBRE 2026 – 19H30</p>
      </div>
    </div>
  </article>

  <article class="elementor-post category-en-cours">
    <div class="elementor-post__text">
      <p class="elementor-post__title">
        <a href="https://laboule-noire.fr/gs/">Gs</a>
      </p>
      <div class="elementor-post__excerpt">
        <p>DIMANCHE 25 OCTOBRE 2026 – 19H30</p>
      </div>
    </div>
  </article>

  <article class="elementor-post category-annule">
    <div class="elementor-post__text">
      <p class="elementor-post__title">
        <a href="https://laboule-noire.fr/cancelled/">Cancelled Artist</a>
      </p>
      <div class="elementor-post__excerpt">
        <p>LUNDI 26 OCTOBRE 2026 – 19H30</p>
      </div>
    </div>
  </article>

  <article class="elementor-post category-reporte">
    <div class="elementor-post__text">
      <p class="elementor-post__title">
        <a href="https://laboule-noire.fr/moved/">Moved Artist</a>
      </p>
      <div class="elementor-post__excerpt">
        <p>MARDI 27 OCTOBRE 2026 – 19H30</p>
      </div>
    </div>
  </article>
</div>
"""


class BouleNoireCompletenessTests(unittest.TestCase):
    @patch("concert_calendar.scrapers.boule_noire.requests.Session")
    def test_impression_index_recovers_missing_active_event_only(self, session_cls):
        session = session_cls.return_value

        def fake_get(url, **kwargs):
            if url == boule_noire.PROGRAMME_URL:
                return FakeResponse(PRIMARY_HTML)
            if url == "https://laboule-noire.fr/impression/":
                return FakeResponse(IMPRESSION_HTML)
            raise AssertionError(f"Unexpected URL: {url}")

        session.get.side_effect = fake_get

        events = boule_noire.load_events()

        by_name = {event.headliner: event for event in events}

        self.assertEqual(set(by_name), {"Existing Artist", "Gs"})
        self.assertEqual(by_name["Gs"].date, "2026-10-25")
        self.assertEqual(
            by_name["Gs"].ticket_url,
            "https://laboule-noire.fr/gs/",
        )


if __name__ == "__main__":
    unittest.main()
