"""Permanent landing pages for the latest Electric Eye newsletters."""

import json

FREQUENCIES = ("weekly", "monthly")


def render_landing_page(frequency):
    """Render a permanent entry point to the latest published edition."""
    if frequency not in FREQUENCIES:
        raise ValueError("Unsupported newsletter frequency")

    title = "Weekly" if frequency == "weekly" else "Monthly"

    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Electric Eye — Latest %s Newsletter</title>
  <meta name="robots" content="noindex,follow">
  <style>
    body {
      margin: 0;
      padding: 60px 20px;
      background: #111114;
      color: #f0f0f1;
      font: 16px/1.6 Arial, sans-serif;
      text-align: center;
    }
    a { color: #e33232; }
  </style>
</head>
<body>
  <h1>Electric Eye — %s Newsletter</h1>
  <p id="status">Opening the latest edition…</p>
  <p><a href="https://www.electriceyerock.com/">
    Visit Electric Eye
  </a></p>

  <script src="../latest.js"></script>
  <script>
    (function () {
      "use strict";
      var frequency = %s;
      var manifest = window.ElectricEyeNewsletterLatest;
      var edition = manifest &&
                    manifest.editions &&
                    manifest.editions[frequency];

      if (!edition ||
          !new RegExp("^" + frequency +
            "/[0-9]{4}-(?:W[0-9]{2}|[0-9]{2})[.]html$"
          ).test(edition.path)) {
        document.getElementById("status").textContent =
          "The latest edition is currently unavailable.";
        return;
      }

      window.location.replace(
        new URL("../" + edition.path, window.location.href).href
      );
    }());
  </script>
</body>
</html>
""" % (title, title, json.dumps(frequency))


def publish_landing_pages(*, token=None, session=None):
    """Publish both permanent newsletter entry pages."""
    from newsletter.page_publish import publish_page

    results = {}

    for frequency in FREQUENCIES:
        results[frequency] = publish_page(
            f"{frequency}/index.html",
            render_landing_page(frequency),
            token=token,
            session=session,
        )

    return results
