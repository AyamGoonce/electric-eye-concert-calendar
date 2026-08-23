# Île-de-France Concert Calendar

An automated concert calendar for the Electric Eye website.

## Status

Production calendar acquisition, normalization, validation, and static export
are implemented. GitHub Actions performs autonomous production refreshes; see
[Production automation](docs/production.md).

## Goal

Collect, normalize and publish concert listings from multiple public sources across Île-de-France.

The hosted calendar supports bookmarkable views such as
[`?q=Afghan Whigs`](https://ayamgoonce.github.io/electric-eye-concert-calendar/proof/?q=Afghan%20Whigs),
[`?venue=Bataclan`](https://ayamgoonce.github.io/electric-eye-concert-calendar/proof/?venue=Bataclan),
and
[`?genre=Metal / Hard Rock`](https://ayamgoonce.github.io/electric-eye-concert-calendar/proof/?genre=Metal%20%2F%20Hard%20Rock).

Genre may be repeated to select several categories; the selections are ORed
with each other and ANDed with search, venue, and date filters. Every event also
has a stable `#event-…` link, Copy/Share actions, and an `.ics` download. Public
genres come only from reviewed source or exact artist evidence and otherwise
remain blank.

For a manual cloud refresh on macOS, compile the portable helper with:

```sh
osacompile -l JavaScript -o "$HOME/Desktop/Update Concert Calendar.app" \
  "scripts/Update Concert Calendar.js"
```

The app uses the already authenticated GitHub CLI to request the existing
workflow; it does not run scrapers locally or store credentials.
