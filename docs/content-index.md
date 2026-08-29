# Electric Eye content index

The build reads Electric Eye's public Blogger summary feed. Calendar inventory never creates an artist identity. An artist is admitted only when an explicit concert-review, album-review, or interview title is corroborated by an Electric Eye post label; that reviewed vocabulary then associates other labeled Electric Eye posts.

`electric-eye-artist-lookup.js` is the compact article-page asset. It contains canonical names, slugs, approved aliases, and the artist-page base URL. `electric-eye-content.<hash>.js` is the full results-page asset. Its top-level fields are `schema`, `generatedAt`, `artists`, `articles`, and `diagnostics`. Artist records contain `n` (name), `al` (aliases), `ar` (article indexes), and optional `crh` (latest eligible concert-review hero). Article records contain `u`, `t`, `d`, `y`, `a`, and optional `im`.

The full index is loaded only by the artist and event-coverage results pages. Calendar links use one reusable `coverage.html?event=<public-id>` route. Its unique article set is the union of every safely matched artist on the event; duplicate URLs appear once. Ordinary posts load only the compact lookup and the DOM auto-linker. The linker defaults to one link per artist per article and skips existing links, scripts, styles, code, forms, embeds, navigation, widgets, ads, and explicit `data-ee-no-autolink` / `ee-no-autolink` opt-outs.

The auto-linker is hosted but not installed in Blogger. The exact theme snippet and insertion point are maintained in `docs/blogger-artist-integration.html`.
