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
