# Related on Apple generation-3 handoff

This directory is generated from the supplied 2026-08-30 live Blogger theme
and Apps Script source by `tools/build_apple_related_deliverables.py`. Do not
edit generated files directly. This repository pass does not deploy or mutate
Apps Script, Blogger, Sheets, properties, cursors, or triggers.

## Architecture

The canonical identity source is the existing Electric Eye content-index
pipeline. Reviewed data lives in
`concert_calendar/artist_identity_overrides.json`; the Blogger feed supplies
automatic article evidence. The normal calendar build publishes the generated
`artist-index.json`, `artist-index.csv`, and
`artist-article-associations.csv`. The Apps Script reads the JSON registry and
caches that download for six hours. It does not create a second identity
source.

Generation 3 separates three restartable stages:

1. `eeAnalyzeArchiveWorker()` reads up to 100 Blogger posts, performs no Apple
   calls, writes idempotent rows to `Apple Article Identity`, and advances
   `EE_APPLE_IDENTITY_INDEX`.
2. `eeDiscoverArtistsWorker()` resolves only `UNRESOLVED` rows in `Apple
   Artists`. Each artist has one persistent, gzip-capable catalogue row with a
   30-day `staleAfter` value. A transient Apple failure returns `RETRY_LATER`
   and pins `EE_APPLE_ARTIST_DISCOVERY_INDEX` to that artist.
3. `eeAssembleArticlePayloadsWorker()` combines resolved artist catalogues in
   batches of 100 and writes the existing article payload format. It makes no
   Apple calls and advances `EE_APPLE_ASSEMBLY_INDEX` independently.

`eeProcessNewestPosts()` and manual article refreshes use the same path. A
known artist is assembled entirely from the persistent artist catalogue. Only
a genuinely new or unresolved artist enters legacy external discovery. Reader
`doGet()` still calls only `eeGetPayload_()` and strips diagnostics; it never
loads the artist registry or performs Apple discovery.

Ambiguous/common names require an exact Blogger artist label plus relationship
or repeated-body corroboration, unless a reviewed article association already
exists. Title substring alone is insufficient. Relationships establish
identity only; they do not automatically qualify another person's catalogue
items as recommendations.

## Sheet schemas and compatibility

Existing `Apple Payloads` rows remain valid. The existing eight columns are
unchanged, schema-1 payloads continue to serve, and valid generation-2 READY
rows are not discarded.

Two sheets are created lazily by the new maintenance functions:

- `Apple Article Identity`: post ID, URL, analysis timestamp/version, artist
  keys/names, confidence, ambiguity, evidence, and article type.
- `Apple Artists`: artist key/name, registry and catalogue schema versions,
  Apple/MusicBrainz IDs, identity confidence/status, encoded catalogue,
  generation/staleness timestamps, representative post, and error.

`eeSeedArtistCataloguesFromGeneration2()` is an idempotent migration helper. It
seeds only nonempty generation-2 READY payloads with one registry-matched
artist and HIGH identity confidence. It ignores generation 1, malformed,
multi-artist, EMPTY, and ERROR rows, and never overwrites an existing artist
row.

## Observability

Run `eeArchitectureStatus()` manually to report analyzed posts, canonical and
unresolved/ambiguous artists, verified Apple IDs, READY/EMPTY/ERROR
classifications, Apple calls and cache hits, catalogue generations, all three
primary cursors, stale artist count/refresh cursor, cooldown, and the latest
transient failure. `eeRefreshStaleArtistsWorker()` refreshes at most one due
catalogue per invocation and pins its independent cursor on a transient error.
`eeBackfillStatus()`
remains available for the legacy article-payload table.

## Measured scaling

The hosted content manifest inspected during development contained 1,772
articles and 757 canonical artists. Treating each as one expensive work unit,
artist-level discovery is at most 757 jobs instead of 1,772 article jobs: 1,015
fewer repeated jobs, a 57.3% reduction. Actual Apple HTTP calls remain dependent
on each artist's eligible LISTEN/WATCH/READ searches, but they now scale with
unique unresolved artists. A known-artist new article performs zero Apple calls;
an unresolved artist performs one catalogue-generation job (with the retained
10-second global request interval and bounded retry policy). Fast identity and
assembly workers each handle up to 100 articles per invocation.

## Conservative production migration (instructions only)

No step below was performed by this repository task.

1. Publish the normal calendar/content build first and verify
   `proof/artist-index.json` is schema 1 and reachable.
2. Back up the Apps Script project and `Apple Payloads` sheet.
3. Install generated `Code.gs`, save it, but do not change the web-app
   deployment or existing trigger yet.
4. Run `eeSeedArtistCataloguesFromGeneration2()` once; inspect
   `eeArchitectureStatus()` and several seeded `Apple Artists` rows.
5. Run `eeAnalyzeArchiveWorker()` manually until identity analysis is complete;
   audit ambiguous/unresolved rows and add reviewed corrections to the source
   JSON followed by a normal index rebuild.
6. Run `eeDiscoverArtistsWorker()` in small manual batches. Stop on
   `RETRY_LATER`; do not advance/reset its cursor during cooldown.
7. Run `eeAssembleArticlePayloadsWorker()` and verify reviewed READY, EMPTY,
   multi-artist, obituary, and ambiguous-name examples. Existing READY rows
   remain available throughout.
8. Only after that validation, create a new Apps Script version and update the
   existing deployment while preserving its URL/access settings. No Blogger
   theme upload is needed for this backend-only generation change.
9. Replace the old brute-force schedule with separately reviewed worker
   schedules only after manual staging proves stable. Never run overlapping
   instances of the same worker. Add `eeRefreshStaleArtistsWorker()` only after
   its one-catalogue-per-run behavior has been observed manually.

Rollback is the prior Apps Script version. The added sheets and columns may
remain; generation-2 READY payloads remain readable. Do not delete rows or reset
cursors as part of routine rollback.
