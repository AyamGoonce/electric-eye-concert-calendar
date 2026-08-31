# Electric Eye content index

The build reads Electric Eye's public Blogger summary feed. Calendar inventory never creates an artist identity. An artist is admitted only when an explicit concert-review, album-review, or interview title is corroborated by an Electric Eye post label; that reviewed vocabulary then associates other labeled Electric Eye posts.

`concert_calendar/artist_identity_overrides.json` is the reviewed identity source: aliases, ambiguity classes, relationships, known IDs, exact article overrides, and manual URL associations. Blogger feed evidence remains the automatic source. Generated files are never edited by hand.

`electric-eye-artist-lookup.js` is the compact article-page asset. It contains canonical names, slugs, approved aliases, and the artist-page base URL. `electric-eye-content.<hash>.js` is the full results-page asset. Its top-level fields are `schema`, `generatedAt`, `artists`, `articles`, and `diagnostics`. Schema-2 artist records retain compact `n`, `al`, `ar`, and optional `crh` fields for the existing frontend and add a structured `identity` record containing relationships, genres, reviewed IDs, ambiguity, evidence, article counts, and update timestamps. Article records contain `u`, `t`, `d`, `y`, `a`, optional Blogger post ID `pi`, and optional `im`.

The same build writes `artist-index.json` and `artist-index.csv` for human and Apps Script use, plus normalized `artist-article-associations.csv`. Rebuild them through the ordinary production build or by calling `build_index()` and `write_assets()`. They are generated publication assets and should be committed only where the repository already commits a release snapshot; source changes belong in the Blogger evidence pipeline or `artist_identity_overrides.json`.

The full index is loaded only by the artist and event-coverage results pages. Calendar links use one reusable `coverage.html?event=<public-id>` route. Its unique article set is the union of every safely matched artist on the event; duplicate URLs appear once. Ordinary posts load only the compact lookup and the DOM auto-linker. The linker is scoped to individual article bodies, defaults to one link per artist per article, and skips existing links, scripts, styles, code, forms, embeds, navigation, ads, and explicit `data-ee-no-autolink` / `ee-no-autolink` opt-outs.

The auto-linker is hosted but not installed in Blogger. The exact theme snippet and insertion point are maintained in `docs/blogger-artist-integration.html`.
