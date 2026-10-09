"""Standalone HTML preview renderer for Electric Eye newsletters."""

from datetime import date
from html import escape
import json


SECTION_TITLES = {
    "concert_review": "Concert Reviews",
    "album_review": "Album Reviews",
    "interview": "Interviews",
    "news": "News",
    "playlist": "Friday's Playlists",
}

SECTION_URLS = {
    "concert_review": "https://www.electriceyerock.com/p/concert-photos-reviews.html",
    "album_review": "https://www.electriceyerock.com/p/album-reviews.html",
    "interview": "https://www.electriceyerock.com/p/interviews.html",
    "news": "https://www.electriceyerock.com/p/news.html",
    "playlist": "https://www.electriceyerock.com/p/fridays-playlist.html",
}

CALENDAR_URL = "https://www.electriceyerock.com/p/paris-area-concert-calendar.html"


def html(value):
    return escape(str(value or ""), quote=True)


def render_article(article):
    image = article.get("image")
    image_html = (
        f'<img src="{html(image)}" alt="" loading="lazy">'
        if image else ""
    )

    return f"""
    <article class="ee-article">
      <a class="ee-article-image" href="{html(article['url'])}">
        {image_html}
      </a>
      <div class="ee-article-body">
        <div class="ee-date">{html(article['date'])}</div>
        <h3><a href="{html(article['url'])}">{html(article['title'])}</a></h3>
        <p>{html(article.get('summary', ''))}</p>
        <a class="ee-read" href="{html(article['url'])}">Read article →</a>
      </div>
    </article>
    """


def render_section(kind, articles):
    if not articles:
        return ""

    title = SECTION_TITLES[kind]
    initial = 8

    cards = []
    for index, article in enumerate(articles):
        hidden = " ee-extra" if index >= initial else ""
        cards.append(
            f'<div class="ee-entry{hidden}">{render_article(article)}</div>'
        )

    button = (
        '<button class="ee-expand" type="button" aria-expanded="false">'
        f'Show all {len(articles)} articles ↓</button>'
        if len(articles) > initial else ""
    )

    return f"""
    <section class="ee-section">
      <div class="ee-section-heading">
        <h2><a href="{html(SECTION_URLS[kind])}">{html(title)}</a></h2>
        <span>{len(articles)} articles</span>
      </div>
      <div class="ee-article-grid">{''.join(cards)}</div>
      {button}
    </section>
    """


def render_concert(concert):
    return f"""
    <li class="ee-concert">
      <time datetime="{html(concert['date'])}">{html(concert['date'])}</time>
      <div>
        <a href="{html(concert['url'])}">{html(concert['artist'])}</a>
        <small>{html(concert['venue'])}</small>
      </div>
      <a class="ee-calendar-link" href="{html(concert['url'])}">View →</a>
    </li>
    """


def render_concerts(concerts):
    if not concerts:
        return ""

    rows = []
    for index, concert in enumerate(concerts):
        hidden = " ee-extra" if index >= 8 else ""
        rows.append(
            f'<div class="ee-entry{hidden}">{render_concert(concert)}</div>'
        )

    button = (
        '<button class="ee-expand" type="button" aria-expanded="false">'
        f'Show all {len(concerts)} concerts ↓</button>'
        if len(concerts) > 10 else ""
    )

    return f"""
    <section class="ee-section ee-calendar">
      <div class="ee-section-heading">
        <h2><a href="{CALENDAR_URL}">Concert Calendar: newly-added shows</a></h2>
        <span>{len(concerts)} concerts</span>
      </div>
      <p class="ee-intro">
        Newly added concerts at selected Paris-area venues.
      </p>
      <ul class="ee-concert-list">{''.join(rows)}</ul>
      {button}
      <p class="ee-calendar-footer">
        <a href="https://www.electriceyerock.com/p/paris-area-concert-calendar.html">
          Explore the complete Paris Area Concert Calendar →
        </a>
      </p>
    </section>
    """


def render_newsletter(snapshot):
    """Return a complete, standalone HTML document."""
    identifier = snapshot["identifier"]
    is_monthly = snapshot["frequency"] == "monthly"

    if is_monthly:
        year, month = map(int, identifier.split("-"))
        edition_title = date(year, month, 1).strftime("%B %Y")
        frequency_title = "Monthly Newsletter"
    else:
        edition_title = identifier
        frequency_title = "Weekly Newsletter"

    sections = "".join(
        render_section(kind, snapshot["articles"].get(kind, []))
        for kind in SECTION_TITLES
    )

    sections += render_concerts(snapshot["concerts"])

    stylesheet = """
    :root {
      color-scheme: dark;
      --bg: #111114;
      --panel: #1b1b20;
      --line: #35353d;
      --text: #f0f0f1;
      --muted: #aaaaaf;
      --accent: #d82323;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 16px/1.6 Arial, Helvetica, sans-serif;
    }
    a { color: inherit; text-decoration: none; }
    a:hover { color: var(--accent); }
    .ee-wrapper { max-width: 1140px; margin: auto; padding: 30px 24px 90px; }
    .ee-header {
      text-align: center;
      padding: 65px 20px 55px;
      border-bottom: 1px solid var(--line);
    }
    .ee-brand {
      display: inline-block;
      color: var(--text);
      text-transform: uppercase;
      font-size: clamp(42px, 8vw, 92px);
      font-weight: 900;
      letter-spacing: -.06em;
      line-height: 1;
    }
    .ee-kicker {
      color: var(--accent);
      letter-spacing: .22em;
      text-transform: uppercase;
      margin-top: 26px;
      font-size: 12px;
      font-weight: 700;
    }
    .ee-header h1 { font-size: clamp(26px, 4vw, 46px); margin: 10px 0; }
    .ee-header p { color: var(--muted); margin: 0; }
    .ee-socials {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 22px;
      margin-top: 24px;
    }
    .ee-socials a {
      color: var(--text);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 34px;
      height: 34px;
    }
    .ee-socials a:hover { color: var(--accent); }
    .ee-socials svg {
      width: 25px;
      height: 25px;
      fill: currentColor;
    }
    .ee-forum {
      text-align: center;
      margin-top: 65px;
      padding: 25px 15px;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      font-size: 18px;
      font-weight: bold;
    }
    .ee-forum a { color: var(--accent); }
    .ee-section { padding-top: 55px; }
    .ee-section-heading {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 15px;
      border-bottom: 2px solid var(--accent);
      margin-bottom: 25px;
    }
    .ee-section-heading h2 { font-size: 28px; margin: 0 0 12px; }
    .ee-section-heading span { color: var(--muted); font-size: 13px; }
    .ee-article-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
    }
    .ee-article {
      background: var(--panel);
      border: 1px solid var(--line);
      height: 100%;
      overflow: hidden;
    }
    .ee-article-image {
      display: block;
      aspect-ratio: 3 / 2;
      background: #29292f;
      overflow: hidden;
    }
    .ee-article-image img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .ee-article-body { padding: 13px; }
    .ee-date {
      color: var(--accent);
      font-size: 12px;
      letter-spacing: .08em;
      margin-bottom: 9px;
    }
    .ee-article h3 { font-size: 16px; line-height: 1.35; margin: 0 0 8px; }
    .ee-article p { color: #c6c6ca; font-size: 12px; line-height: 1.5; margin: 0 0 12px; }
    .ee-read { color: var(--accent); font-size: 13px; font-weight: bold; }
    .ee-extra { display: none; }
    .ee-expand {
      display: block;
      margin: 28px auto 0;
      color: var(--accent);
      background: transparent;
      border: 1px solid var(--accent);
      padding: 12px 28px;
      cursor: pointer;
      font: inherit;
    }
    .ee-expand:hover { background: var(--accent); color: #111; }
    .ee-intro { color: var(--muted); }
    .ee-concert-list { list-style: none; padding: 0; }
    .ee-concert {
      display: grid;
      grid-template-columns: 110px minmax(0, 1fr) 70px;
      align-items: center;
      gap: 18px;
      padding: 14px 0;
      border-bottom: 1px solid var(--line);
    }
    .ee-concert time { color: var(--accent); font-size: 13px; }
    .ee-concert small { display: block; color: var(--muted); }
    .ee-calendar-link { color: var(--accent); font-size: 13px; text-align: right; }
    .ee-calendar-footer { margin-top: 30px; color: var(--accent); }
    .ee-footer {
      text-align: center;
      margin-top: 70px;
      padding-top: 25px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 13px;
    }
    @media (min-width: 681px) and (max-width: 950px) {
      .ee-article-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 680px) {
      .ee-wrapper { padding: 15px 15px 60px; }
      .ee-header { padding: 40px 10px; }
      .ee-article-grid { grid-template-columns: 1fr; }
      .ee-section-heading h2 { font-size: 23px; }
      .ee-concert { grid-template-columns: 85px minmax(0, 1fr); }
      .ee-calendar-link { display: none; }
    }
    """

    script = """
    (function() {
      'use strict';

      var parentOrigin = 'https://www.electriceyerock.com';

      function reportHeight() {
        if (window.parent === window) return;

        var wrapper = document.querySelector('.ee-wrapper');
        if (!wrapper) return;

        var height = Math.ceil(wrapper.getBoundingClientRect().height);

        window.parent.postMessage({
          type: 'electric-eye-newsletter-height',
          height: height
        }, parentOrigin);
      }

      document.querySelectorAll('.ee-expand').forEach(function(button) {
        button.addEventListener('click', function() {
          var section = button.closest('.ee-section');
          var expanded = button.getAttribute('aria-expanded') === 'true';

          section.querySelectorAll('.ee-extra').forEach(function(item) {
            item.style.display = expanded ? 'none' : 'block';
          });

          button.setAttribute('aria-expanded', String(!expanded));
          button.textContent = expanded ? 'Show all ↓' : 'Show fewer ↑';

          reportHeight();
        });
      });

      window.addEventListener('load', function() {
        reportHeight();

        if (window.parent !== window) {
          window.parent.postMessage({
            type: 'electric-eye-newsletter-ready'
          }, parentOrigin);
        }
      });

      if ('ResizeObserver' in window) {
        var wrapper = document.querySelector('.ee-wrapper');
        if (wrapper) {
          new ResizeObserver(reportHeight).observe(wrapper);
        }
      }

      reportHeight();
    }());
    """
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>Electric Eye — {html(edition_title)} Newsletter</title>
  <style>{stylesheet}</style>
</head>
<body>
  <main class="ee-wrapper">
    <header class="ee-header">
      <a class="ee-brand" href="https://www.electriceyerock.com/" aria-label="Electric Eye homepage">Electric Eye</a>
      <div class="ee-kicker">{html(frequency_title)}</div>
      <h1>{html(edition_title)}</h1>
      <p>Concerts, reviews, interviews, news and playlists.</p>
      <nav class="ee-socials" aria-label="Electric Eye social media">
        <a href="https://www.facebook.com/ElectricEyeRock/"
           aria-label="Electric Eye on Facebook"
           title="Facebook" target="_blank" rel="noopener noreferrer">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.51 1.49-3.9 3.77-3.9 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.77l-.44 2.89h-2.33v6.99A10 10 0 0 0 22 12Z"/>
          </svg>
        </a>
        <a href="https://www.instagram.com/electric_eye_photo/"
           aria-label="Electric Eye on Instagram"
           title="Instagram" target="_blank" rel="noopener noreferrer">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <rect x="2" y="2" width="20" height="20" rx="5"
                  fill="none" stroke="currentColor" stroke-width="2"/>
            <circle cx="12" cy="12" r="4.5"
                    fill="none" stroke="currentColor" stroke-width="2"/>
            <circle cx="18" cy="6" r="1.2"/>
          </svg>
        </a>
      </nav>
    </header>
    {sections}
    <aside class="ee-forum">
      <a href="https://www.electriceyerock.com/p/forums.html">
        Join the conversation at the Electric Eye Forums →
      </a>
    </aside>
    <footer class="ee-footer">
      <p>Electric Eye - A music site with an emphasis on all things electric.</p>
      <p><a href="https://www.electriceyerock.com/">Visit Electric Eye →</a></p>
    </footer>
  </main>
  <script>{script}</script>
</body>
</html>"""
