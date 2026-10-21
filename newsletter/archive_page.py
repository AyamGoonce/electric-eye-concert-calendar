"""Public archive page for Electric Eye newsletters."""


def render_archive_page():
    """Render a page populated from the published archive index."""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Newsletter Archives | Electric Eye</title>
  <meta name="description"
        content="Browse all Electric Eye weekly and monthly newsletters.">
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: #111114;
      color: #eee;
      font: 16px/1.6 Arial, sans-serif;
    }
    main {
      max-width: 920px;
      margin: 0 auto;
      padding: 48px 24px 80px;
    }
    h1 { font-size: 2rem; margin-bottom: 8px; }
    h2 {
      margin-top: 42px;
      padding-bottom: 10px;
      border-bottom: 1px solid #444;
    }
    a { color: #eee; }
    a:hover { color: #e33232; }
    .home { color: #e33232; text-decoration: none; }
    ul { list-style: none; padding: 0; }
    li { padding: 10px 0; border-bottom: 1px solid #292929; }
    .empty { color: #aaa; }
  </style>
</head>
<body>
  <main>
    <p><a class="home" href="https://www.electriceyerock.com/">
      ELECTRIC EYE
    </a></p>
    <h1>Newsletter Archives</h1>
    <p>Browse previous weekly and monthly editions.</p>

    <section>
      <h2>Weekly Editions</h2>
      <ul id="weekly"><li class="empty">Loading…</li></ul>
    </section>

    <section>
      <h2>Monthly Editions</h2>
      <ul id="monthly"><li class="empty">Loading…</li></ul>
    </section>
  </main>

  <script>
    (async function () {
      "use strict";

      try {
        const response = await fetch("./index.json", {
          cache: "no-cache"
        });
        if (!response.ok) throw new Error("Archive unavailable");

        const archive = await response.json();

        for (const frequency of ["weekly", "monthly"]) {
          const list = document.getElementById(frequency);
          const entries = archive.editions[frequency] || [];
          list.replaceChildren();

          if (!entries.length) {
            const empty = document.createElement("li");
            empty.className = "empty";
            empty.textContent = "No editions published yet.";
            list.appendChild(empty);
            continue;
          }

          for (const entry of entries) {
            const expected = frequency === "weekly"
              ? /^weekly\\/\\d{4}-W\\d{2}\\.html$/
              : /^monthly\\/\\d{4}-\\d{2}\\.html$/;

            if (!expected.test(entry.path)) continue;

            const li = document.createElement("li");
            const link = document.createElement("a");
            link.href = new URL("../" + entry.path, location.href);
            link.textContent = entry.label;
            li.appendChild(link);
            list.appendChild(li);
          }
        }
      } catch (error) {
        for (const frequency of ["weekly", "monthly"]) {
          document.getElementById(frequency).textContent =
            "The archive is temporarily unavailable.";
        }
      }
    }());
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    print(render_archive_page())
