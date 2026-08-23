# Production automation

## Architecture

The production refresh runs entirely on a GitHub-hosted Ubuntu runner:

1. GitHub Actions checks out the source branch and installs Python dependencies.
2. The complete test suite runs before any live scraping.
3. Every scraper runs with bounded central retries for raised network failures.
4. Events pass through the existing geography, scope, venue, promoter, and
   deduplication pipeline.
5. The generated renderer contract, dates, required fields, genres, ticket
   URLs, hashes, source counts, and event counts are validated.
6. Canonical event state is reconciled and validated against the durable
   `proof/calendar-state.json` file from the current Pages branch.
7. Only validated assets and candidate state are staged and committed to the
   `gh-pages` branch.
8. The hosted pointer, hashed data, state, renderer, and CSS are verified over HTTPS.

GitHub Pages hosts the static assets. Blogger remains the public website and
loads those assets; ordinary updates do not require Blogger edits. The user's
Mac does not participate in scheduled or manual GitHub runs.

## Schedule and concurrency

`Update Electric Eye Concert Calendar` runs at `17 */6 * * *`: 00:17, 06:17,
12:17, and 18:17 UTC every day. These are 01:17/07:17/13:17/19:17 in Paris
during CET and 02:17/08:17/14:17/20:17 during CEST.

All runs share one concurrency group. `cancel-in-progress` is false, so an
active publication is allowed to finish and a later run waits rather than
racing it or leaving an interrupted publication.

## Persistent event state

`proof/calendar-state.json` is the durable, versioned event-state store. It is
checked out from `gh-pages` on every independent runner. A canonical SHA-256
identity uses the existing normalized date, headliner, and canonical venue;
ticket, genre, opener, promoter, casing, and source-order improvements therefore
do not reset `first_seen`.

The first state-enabled run bootstraps every successfully validated candidate
event at 72 hours plus one second before the build time. This deliberately
prevents the existing inventory from appearing NEW. Later unseen identities
receive the current successful build timestamp. NEW is derived at render time
and lasts exactly 72 hours.

State is validated before candidate export. Missing state bootstraps safely
without NEW markers; malformed state fails the workflow. Candidate state is
copied before the pointer and committed atomically with the data. A scrape,
test, or validation failure cannot advance published state or Last updated.
The pointer contains the state hash, and hosted verification checks it.

State records retain `first_seen`, `last_seen`, and event date. Past identities
are retained for 180 days, allowing temporarily missing events to return without
immediately losing identity while bounding growth. The state schema can later
add explicit source-supported cancelled, postponed, date/venue change, opener,
and ticket-status history. Disappearance alone must never set those statuses.

## Manual update

1. Open the repository's **Actions** tab.
2. Select **Update Electric Eye Concert Calendar**.
3. Select **Run workflow**, leave both safety options disabled, and confirm.

`allow_large_count_change` is only for a deliberately reviewed inventory change
outside the normal safety range. `validation_failure_test` deliberately fails
after building and validating the candidate data and never publishes it.

## Last-known-good protection

Publication is skipped if tests fail, a scraper exhausts its retries, a core
source returns zero, required counts are zero, fewer than 100 final events are
produced, the public renderer contract is malformed, dates or ticket URLs are
invalid, public genres are unknown, duplicate renderer records remain, or an
asset hash/pointer is inconsistent.

The new final count must normally remain between 60% and 250% of the currently
published manifest count. The lower bound catches a severe source collapse but
allows ordinary inventory expiry and seasonality. The generous upper bound
catches obvious duplication or runaway pagination. A reviewed manual run can
explicitly override this count-only guard; it cannot override any other
validation.

The workflow commits to `gh-pages` only after all local validation succeeds.
The hashed data file and pointer change in the same Git commit, so Pages never
receives a commit whose pointer references a missing file. A failed job leaves
the existing Pages commit and calendar online.

## Data retention and rollback

Each successful publication retains the current hashed data asset and the two
most recent prior assets. Older hashes are removed in the same atomic Pages
commit. Stable renderer and CSS files are copied only when their content
changes.

To roll back, restore `proof/calendar-current.js` from the desired known-good
`gh-pages` commit together with its `calendar-state.json` and referenced data
hash, commit that change to
`gh-pages`, and verify both URLs. Reverting the most recent Pages publication
commit is the simplest option when its predecessor is known good.

## Operations and diagnosis

GitHub's **Actions** tab shows scheduled and manual runs and provides normal
GitHub failure notifications according to the account's notification settings.
No external monitoring credentials are required.

For a failed run:

1. Open the failed **Update Electric Eye Concert Calendar** run.
2. Inspect the failing step and scraper count output.
3. Download the `calendar-production-report-<run-id>` artifact when present.
4. Fix the underlying source or validation issue on the source branch.
5. Trigger a normal manual run; do not bypass non-count validation.

The run summary records raw, IDF, and final counts, genre completeness and
conflicts, new/disappeared events, support additions, genre enrichments,
ticket-status changes, the published SHA-256, runner platform, and whether
Pages changed. Disappearance is informational only and never implies
cancellation. A future NEW SUPPORT badge can use support additions without
changing the existing NEW identity semantics.

The public proof is:

`https://ayamgoonce.github.io/electric-eye-concert-calendar/proof/`

## Calendar product behavior

Festival days retain complete authoritative lineups. The public row initially
shows five other artists and an accessible `+ N more artists` button; expansion
is visual only, and hidden names remain searchable.

Quick dates use `Europe/Paris`: Tonight is the Paris-local current date; This
Week is Monday through Sunday; This Weekend is Friday through Sunday of the
current weekend on Friday–Sunday, otherwise the upcoming weekend. Selecting a
quick date clears Month, selecting Month clears the quick date, and All Dates
clears both date restrictions.

URL parameters are `q`, `venue`, repeatable `genre`, `month`, `when`, `new`, and `sort`.
State restores on reload and popstate. Examples:

- `?q=Afghan%20Whigs`
- `?venue=Bataclan`
- `?genre=Metal%20%2F%20Hard%20Rock`
- `?when=weekend&new=1&sort=artist-asc`

Artist text populates Search; venue text activates the canonical Venue filter.
Explicit structured sold-out evidence produces SOLD OUT and suppresses the
Tickets action. The same evidence-only rule applies to FREE and NOT ON SALE
YET; a missing URL never implies any status. Stable event anchors are derived
from canonical date, headliner, and venue, so metadata improvements preserve
Copy link/Share URLs. Add to calendar emits an all-day ICS unless a reliable
source time exists; festival rows remain one calendar event with their full
authoritative lineup. Last updated comes from
the successfully published pointer timestamp and renders in Paris local time.

The Genre control permits several broad categories. Genre selections use OR;
search, venue, date, month, and Newly added remain AND constraints. URL state
has precedence over the locally remembered sort preference. Storage failures
or malformed values are ignored safely.

## Genre provenance and reviewed mappings

The closed public vocabulary lives in `concert_calendar/genres.py`. Source raw
values and source names remain build-side as evidence. Exact safe raw mappings
are applied before the reviewed canonical artist dictionary in
`concert_calendar/genre_mappings.json`; narrow reviewed overrides have highest
priority. Conflicting mapped source evidence produces a diagnostic and a blank
public genre. Festival-day rows never inherit a headliner genre. Production
fails on vocabulary leakage and on a catastrophic drop below 10% coverage,
while ordinary coverage drift is allowed.

External genre research is deliberately absent from the production workflow.
It is performed as a controlled maintenance audit, in descending blank-row
impact, using authoritative event sources first, official artist biographies,
then reviewed MusicBrainz/Wikidata structured metadata and corroborated
editorial sources. `scripts/research_blank_genres.py` is an optional one-time
audit helper, not an imported production component. Its output is reviewed
before records are copied into the persistent dictionary.

Each dictionary record requires a canonical artist, approved public genre,
evidence source and type, review date, evidence URL when available, and notes.
Exact normalized casing/punctuation matches are allowed; fuzzy artist matching
is not. Reliable event-specific genre always beats an artist default. A narrow
editorial override may resolve conflicting evidence only when explicitly
reviewed; otherwise conflicts and genuinely multi-bucket artists remain blank.
The build diagnostic includes every raw value and source, mapped target,
mapping provenance, conflict, and unresolved canonical artist ordered by
affected rows. See `docs/genre-research.md` for the current manual-review queue.

## Archive and image policy

Electric Eye archive links must eventually be generated from one build-time
index of canonical artist identities to public Blogger URLs. Production must
not query Blogger per row, and ambiguous identities must not link. The small
archive action should appear only where an exact match exists.

No public imagery is currently shipped. Future image data must be explicitly
associated with the event by an official or otherwise reviewed source, retain
provenance, and never use image search, generated imagery, or unrelated stock.
Compact remains the default and must make zero image requests. Any Images mode
must lazy-load dimensioned thumbnails near the viewport, preserve the text-only
fallback, prefer festival artwork for festival rows, and resolve reuse and
caching rights before copying third-party assets to Pages.

## One-click Mac update

`scripts/Update Concert Calendar.js` is portable JXA app source and
`scripts/update-concert-calendar.sh` is its terminal equivalent. Compile the
app with the command in the README and place it wherever convenient (normally
the Desktop). Clicking it authenticates through the existing `gh` keychain
session, dispatches `Update Electric Eye Concert Calendar` on
`supersonic-scraper`, then says only that the update *started on GitHub*.
“Open Update Status” opens the Actions page. Authentication, network, and
workflow errors produce an error dialog; no token or machine path is embedded.

Filters are sticky above 680px with the scoped
`--ee-calendar-sticky-top` custom property available for the eventual Blogger
shell offset. Mobile controls are intentionally non-sticky. Day separators
appear only in chronological sorts.

Before Blogger go-live, add an AdSense exact URL exclusion for
`https://www.electriceyerock.com/p/paris-area-concert-calendar.html`. Do not
hide served Auto Ads with CSS.
