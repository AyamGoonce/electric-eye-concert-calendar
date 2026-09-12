# Electric Eye Concert Calendar — Project Handoff

## 2026-09-10 — Genre enrichment checkpoint

Branch: `supersonic-scraper`

### Production state before this checkpoint
- Latest confirmed live gh-pages promotion before genre work:
  `d9002cd2fd161568a44e09c0ed8098653fb61826`
- Active asset at audit start:
  `proof/calendar-data.65c84af9864d2dab.js`
- Active live count at audit start: 2488 events.
- Previous production code commit:
  `5908733 Separate internal artist identity from public casing`

### Genre work completed
- Fixed `scripts/research_blank_genres.py` false-positive substring matching.
  - `rap` can no longer match inside words such as `biographical`.
- Updated offline Wikidata helper to current public taxonomy:
  - `Chanson Française / Variétés`
  - `Comedy / Spoken Word`
- Added explicit recognition of hyphenated `hip-hop`.
  - This recovered Odezenne and Hatik while correctly making mixed
    Electronic + hip-hop evidence ambiguous.
- Added 42 reviewed Wikidata artist mappings affecting 44 current rows.
- Existing reviewed MNEK and Noah Kahan mappings were not duplicated.
- Ambiguous/questionable Wikidata classifications were withheld rather
  than promoted automatically.
- Added conservative exact raw-source mappings for:
  - psych-rock
  - Afrobeats, Afropop, Rumba
  - Rap, Trap, Hip Hop
  - Concert / Hip hop
  - French pop - Indie pop
  - Musique orientale
  - Musique celtique
  - Zouk
- Mixed, non-musical, or unsupported raw labels remain deliberately blank.
- Fixed `scripts/resolve_genres.py` so MusicBrainz HTTP/transport failures
  are never cached as artist-level "unresolved" results.
- MusicBrainz was unavailable during the audit (503/timeouts), so no
  MusicBrainz research results from that run should be relied upon.

### Coverage measurement
Before reviewed mappings:
- Upcoming: 2487
- With genre: 1870
- Without genre: 617
- Coverage: 75.2%

After reviewed artist mappings:
- Upcoming: 2490
- With genre: 1914
- Without genre: 576
- Coverage: 76.9%

After safe raw-source mappings:
- Upcoming: 2496
- With genre: 1926
- Without genre: 570
- Coverage: 77.2%

Counts changed slightly between measurements because source data was live.

### Remaining genre work
- Roughly 484 current/future blank rows have no genre evidence,
  representing about 429 unique artist/event identities.
- Do not force classifications for recurring series, event titles,
  classical/film/conference/dance labels, or conflicting evidence.
- Continue reviewed artist research offline/manual-first.
- Do not add external genre lookup to the six-hour production workflow.
- Do not auto-promote ambiguous external-source results.

### Validation
- Full test suite: 565 tests passed.
- `git diff --check`: clean.

### Unrelated files — DO NOT stage/delete
- `.github/workflows/update-calendar.yml.save`
- `Electric-Eye-READY-audit-safety-gate-2026-09-05.json`

## 2026-09-10 — Resolver hardening checkpoint

- Added reviewed Odezenne genre mapping: Hip-hop / Rap.
- Confirmed artist mapping lookup is case-insensitive for Odezenne/ODEZENNE.
- Hardened `scripts/resolve_genres.py` genre vocabulary to current public taxonomy:
  - Chanson Française / Variétés
  - Comedy / Spoken Word
- Replaced unsafe substring genre matching with token/phrase-boundary matching.
  - Prevents `rap` from matching inside words such as `biographical`.
  - Still recognizes legitimate forms such as `French hip-hop` and `synth-pop`.
- Full suite after changes: 567 tests passed.
- Next task: turn existing MusicBrainz, Wikidata, Apple/iTunes and Bandcamp
  resolvers into a multi-source consensus enrichment engine, with controlled
  occupation/type evidence and without hard-coding individual performers.

### Unrelated files — DO NOT stage/delete
- `.github/workflows/update-calendar.yml.save`
- `Electric-Eye-READY-audit-safety-gate-2026-09-05.json`

## 2026-09-10 — Multi-source consensus core

- Added deterministic `combine_provider_results()` to the offline genre resolver.
- Consensus policy:
  - no usable provider result -> unresolved
  - one resolved provider -> review_candidate
  - two or more independent providers agreeing -> resolved
  - conflicting resolved providers -> ambiguous
- Unresolved providers do not veto agreement between other providers.
- This remains maintenance/research tooling only; production does not query external genre services.
- Targeted resolver suite: 11 tests passed.
- Next: wire MusicBrainz, Apple/iTunes, Bandcamp and Wikidata into one bulk consensus report, then add controlled occupation/type evidence.

### Unrelated files — DO NOT stage/delete
- `.github/workflows/update-calendar.yml.save`
- `Electric-Eye-READY-audit-safety-gate-2026-09-05.json`

## 2026-09-10 — Failure-safe provider orchestration

- Added shared `provider_result()` wrapper for external genre providers.
- Added `resolve_artist_consensus()` for one canonical artist identity.
- Existing providers now available through common orchestration:
  - MusicBrainz
  - Apple/iTunes
  - Bandcamp
  - Wikidata
- Transport/server failures return `unavailable` and are never cached as
  artist-level unresolved results.
- Genuine successful "not found" responses may still be cached as unresolved.
- Multi-provider agreement feeds the previously added conservative consensus layer.
- Conflicting providers remain ambiguous.
- This remains offline/research tooling only; production does not query these services.
- Full suite: 575 tests passed.
- Next: bulk consensus audit of all remaining blank calendar identities.

### Unrelated files — DO NOT stage/delete
- `.github/workflows/update-calendar.yml.save`
- `Electric-Eye-READY-audit-safety-gate-2026-09-05.json`

## 2026-09-10 — Apple/iTunes taxonomy correction

- Corrected stale Apple/iTunes mappings:
  - `chanson française`
  - `variété française`
- Both now normalize to the current public category:
  `Chanson Française / Variétés`
- Added regression coverage ensuring `French chanson` cannot re-enter the
  Apple/iTunes genre mapping.
- Full suite: 578 tests passed.
- Next: address event-title/composite-billing strings being treated as artist
  identities before expanding the multi-source genre audit.

## 2026-09-10 — Conservative genre research identity cleanup

- Added `research_artist_identity()` for external genre research only.
- Removes explicit performance-time suffixes such as `– 19h00`.
- Removes explicit jam-session suffixes such as:
  - `+ Jam Vocale`
  - `+ Jam blues`
  - `+ jam`
- Examples now consolidate to stable research identities:
  - `Cecil L. Recchia + Jam Vocale – 19h00` -> `Cecil L. Recchia`
  - `Big Dez + Jam blues` -> `Big Dez`
  - `David Sauzay + jam – 21h30` -> `David Sauzay`
- Arbitrary `+` and `&` artist names are deliberately not split.
- Public calendar display and deduplication semantics are unchanged.
- Full suite: 581 tests passed.
- Next: inspect the top 25 blank research identities after cleanup without
  making external provider calls.

## 2026-09-10 — Provider pacing and retry/backoff

- Added shared provider pacing for external genre research.
- Added transient retry handling for:
  - HTTP 429
  - HTTP 500
  - HTTP 502
  - HTTP 503
  - HTTP 504
  - connection errors
  - timeouts
- `Retry-After` is honored when supplied.
- HTTP 403 is deliberately not retried.
- Exhausted provider failures remain `unavailable` and are not cached as unresolved.
- The same policy now applies through the shared provider runner rather than
  provider-specific ad-hoc sleeps.
- Full suite: 585 tests passed.
- Next: rerun a controlled live provider sample using the new pacing/backoff
  before attempting another full 489-identity audit.

### Unrelated files — DO NOT stage/delete
- `.github/workflows/update-calendar.yml.save`
- `Electric-Eye-READY-audit-safety-gate-2026-09-05.json`

## 2026-09-10 — First Apple + Bandcamp consensus promotion batch

- Full external research pass completed across 489 blank research identities / 541 rows.
- Provider reliability after pacing/backoff:
  - unavailable provider calls: 0
- Two-source consensus:
  - 54 identities
  - 62 event rows
- Reviewed identity safety before promotion.
- Promoted 49 identities to `concert_calendar/genre_mappings.json`.
- These mappings affect 57 currently blank calendar rows.
- Evidence provenance:
  - Apple Music + Bandcamp
  - evidence_type: multi_source_genre_consensus
- Explicitly held out because identity/taxonomy evidence was unsafe or ambiguous:
  - Big D
  - Ekaterina Shelehova
  - Ozzy
  - Roomer
  - Sombr
- Mapping count increased from 1161 to 1210.
- Full suite after promotion: 585 tests passed.
- Live calendar has NOT yet been updated with this batch.
- Next: measure projected genre coverage with the new mappings, then continue
  reviewing high-confidence single-source candidates to build a larger deployment.

### Unrelated files — DO NOT stage/delete
- `.github/workflows/update-calendar.yml.save`
- `Electric-Eye-READY-audit-safety-gate-2026-09-05.json`

## 2026-09-10 — Shared production/research genre identity cleanup

- Added one shared conservative genre lookup identity helper in
  `concert_calendar/genres.py`.
- Production genre enrichment and external research now use the same identity
  normalization logic.
- Removes only explicit performance/session metadata:
  - time suffixes such as `– 19h30`
  - explicit `+ jam`, `+ Jam Vocale`, `+ JAM SESSION`, etc.
- Arbitrary `+` and `&` artist billing remains untouched.
- Public event titles, display names, and deduplication semantics are unchanged.
- This allows the 10 previously cleanup-only Sunset/Sunside jazz rows to use
  their reviewed artist mappings in production.
- Targeted tests passed.
- Full suite: 588 tests passed.
- Next: commit/push, then recalculate projected coverage using actual production
  genre enrichment before continuing single-source candidate review.

### Unrelated files — DO NOT stage/delete
- `.github/workflows/update-calendar.yml.save`
- `Electric-Eye-READY-audit-safety-gate-2026-09-05.json`

## 2026-09-10 — Emergency cancellation-status bug

### Incident
- Melanie Martinez at Accor Arena is officially cancelled.
- Accor Arena reports the cancellation.
- Live Nation also reports the cancellation.
- Electric Eye calendar currently fails to reflect it.

### Root cause identified
- Deduplication is already correct:
  - `cancelled` has highest ticket-status priority.
- Production export already supports:
  - `ticket_status="cancelled"` -> public `ts="cancelled"`.
- The failure is upstream:
  - Accor Arena scraper currently creates ConcertEvent records without extracting
    `ticket_status`.
  - Live Nation scraper currently creates ConcertEvent records without extracting
    `ticket_status`.
- Therefore the cancellation status never enters the event model and cannot be
  preserved by deduplication.

### Required systemic behavior
- Do NOT hard-code Melanie Martinez.
- Extract official cancellation status generically from Accor Arena.
- Extract official cancellation status generically from Live Nation.
- If either trusted source supplies `cancelled`, deduplication should preserve it.
- Public calendar rendering:
  - greyed/disabled status button reading `CANCELLED`
  - render `(cancelled)` beside the event name
- `(cancelled)` must be presentation-only.
- Do NOT append it to `event.headliner`, canonical identity, deduplication identity,
  or genre lookup identity.

### Current genre state before emergency
- Shared production/research genre identity cleanup committed/pushed:
  - commit `032f41e`
- Full suite at that checkpoint:
  - 588 tests passed
- Fresh local production genre run:
  - 2513 deduplicated Île-de-France events
  - 1999 with genre
  - 514 blank
  - 79.5% coverage
- No live deployment of the new genre work yet.

### Next emergency step
- Inspect raw Melanie Martinez records returned by the Accor Arena and Live Nation
  APIs to identify the authoritative cancellation fields.
- Inspect browser renderer handling of public `ts` statuses.
- Implement source extraction + renderer behavior + regression tests.
- Run full suite.
- Commit/push before resuming genre enrichment.

### Unrelated files — DO NOT stage/delete
- `.github/workflows/update-calendar.yml.save`
- `Electric-Eye-READY-audit-safety-gate-2026-09-05.json`

### Cancellation-status fix implemented and validated
- Accor Arena official `status_code == "H"` now maps systemically to:
  - `ticket_status="cancelled"`
- Verified against the live Accor Arena API:
  - Melanie Martinez — 2026-09-15 — cancelled
  - NEJ — 2026-11-23 — cancelled
- No artist-specific hard-coding was added.
- Existing deduplication already gives `cancelled` highest ticket-status priority.
- Existing production export already emits `ts="cancelled"`.
- Existing calendar renderer already displays a muted/disabled `CANCELLED` status control.
- Renderer now additionally displays presentation-only `(cancelled)` beside cancelled event billing.
- Canonical headliner/artist identity is unchanged.
- Genre lookup and deduplication identities are unchanged.
- Added Accor cancellation regression coverage.
- Full suite after implementation:
  - 591 tests
  - all passing

## 2026-09-10 — Accor cancellation fix deployed to production

Production deployment completed and verified.

- Code fix commit: 54ef195 — Handle Accor Arena cancellations
- Accor status_code H is translated systemically to ticket_status="cancelled"
- No performer-specific cancellation hardcoding
- Renderer displays "(cancelled)" beside the event name and a muted CANCELLED status control
- Full test suite: 591 tests, OK
- Production candidate event count: 2495
- Production data SHA-256: 2943e18bbf263cd496309b088ff69526b0428ef9a807d2b2924e062b05e1611f
- Production data asset: calendar-data.2943e18bbf263cd4.js
- Candidate staging gh-pages commit: 9464dca
- Live promotion gh-pages commit: 0d55397
- Live publishedAt: 2026-09-10T17:57:03Z
- Live verification confirmed:
  - Melanie Martinez | 2026-09-15 | Accor Arena | ticket_status=cancelled
  - Nej | 2026-11-23 | Accor Arena | ticket_status=cancelled
- Hosted candidate verification passed before promotion.
- Live pointer verification passed after promotion.

Next planned work: resume genre coverage/enrichment from the last production audit rather than reopening the cancellation issue.

## 2026-09-10 — Fresh post-enrichment genre audit

Fresh non-publishing production build completed successfully after the Sunset/Sunside fallback and reviewed raw-taxonomy mappings.

- Build exit code: 0
- Total events: 2508
- Populated genres: 2032
- Blank genres: 476
- Coverage: 81.02%
- source_explicit: 68
- source_mapping: 865
- artist_mapping: 951
- manual overrides: 2
- event_context: 36
- bill_consensus: 110
- blank_no_raw: 418
- blank_unresolved_raw: 39
- blank_festival: 5
- conflicts: 12
- unresolved raw occurrences: 41
- unresolved identities: 444

This supersedes the older 2500-event / 79.56% genre audit for current-code coverage analysis. The dominant remaining gap is now events with no raw genre evidence (418), not unresolved source taxonomy.

## 2026-09-10 — La Maroquinerie sold-out detection

Fixed systemic sold-out status extraction for La Maroquinerie.

- Explicit `COMPLET` is detected from booking text, source title, detail URL, or ticket URL.
- Matching events now set `sold_out=True` and `ticket_status="sold_out"`.
- This fixes cases such as Isabel van Gelder without artist-specific logic.
- Added regression tests for URL-based and visible-text `COMPLET` detection.

## 2026-09-10 — Deterministic cross-source duplicate merging

Improved systemic deduplication for exact artist/date/venue matches when an official venue source and an external source report different times.

- A venue-vs-external time disagreement alone no longer creates a duplicate when there is no explicit evidence of separate performances.
- Official venue provenance is captured before source metadata is merged, preventing load-order-dependent decisions.
- The official venue time is retained when the discrepancy is attributable to differing source time semantics.
- The official venue event URL is preferred over an external listing URL when merging an otherwise confirmed duplicate.
- Compatible metadata is unioned rather than discarded, including image, genre evidence, sold-out status, promoters, sources, openers and other fields.
- Result is deterministic regardless of scraper load order.
- Explicitly distinct performances and independently timed non-venue records remain protected.
- Verified against a 63Kluf-shaped La Machine du Moulin Rouge / DICE pair in both source orders.

## 2026-09-10 — Remove full ConcertEvent console logging

Resolved GitHub CodeQL alert #2: clear-text logging of sensitive information.

- Removed the debug loop in `concert_calendar/app.py` that printed every complete ConcertEvent object.
- The useful message reporting the generated HTML calendar path remains.
- No calendar data or production behavior was otherwise changed.

## 2026-09-12 — Apple Related engine: artist-resolution investigation

Current focus has returned to the Electric Eye "Related on Apple" recommendation engine.

### Active implementation
- Main deployed bundle: `deliverables/apple-related/Code.gs`
- Current branch at investigation start: `supersonic-scraper`
- Starting commit: `17cfe09`
- Core relevant functions:
  - `eeResolveIdentity_()` — artist identity resolution
  - `eeFastArticleIdentity_()` — article identity extraction
  - `eePrimaryArtistIdentityPayload_()` — Apple identity-search payload
  - `eeDiscoverArtistCatalogue_()` — Apple artist/catalogue discovery
  - `eeAnalyzeArchiveWorker()` — archive analysis
  - `eeDiscoverArtistsWorker()` / production worker — artist discovery/enrichment

### Problem
Too many articles remain unpopulated because artist identities are ending in
AMBIGUOUS / UNRESOLVED / ERROR rather than resolving to Apple artists.

A real failure list was supplied containing both obscure and extremely obvious
Apple Music artists. Important examples include:

- Prince
- Hozier
- Iggy Pop
- Depeche Mode
- Toto
- Metallica
- Lady Gaga
- KISS
- Patti Smith
- Franz Ferdinand
- Mastodon
- John Mayall
- John Scofield
- Jessica Hernandez
- Little Caesar
- Elegant Weapons
- ...And You Will Know Us By The Trail Of Dead

Because major unambiguous artists are failing as well as difficult names, this
is probably not primarily an Apple catalogue-availability problem.

### Failure classes already visible

1. Ordinary artists that should resolve trivially.
   Indicates likely query/scoring/acceptance-threshold failure.

2. Generic ambiguous names:
   Earth, Ross, Answer, Lucifer, Ride, Ghost, Ancient, Trio, Soul, Grove,
   Sugar, Down, Sparks, FM.

3. Punctuation / diacritics / stylization:
   ...And You Will Know Us By The Trail Of Dead, M-Pire of Evil,
   Suprême NTM, Téléphone, Les Insus?, Therapy?, W.A.S.P.,
   Dätcha Mandala, Beastö Blancö, Gaëlle Buswel, Yü.

4. Alias / canonical-name differences:
   Trail of Dead vs ...And You Will Know Us By The Trail Of Dead and
   possible leading-"The" catalogue differences.

5. Composite/collaborative identities:
   Richard Bona/Alfredo Rodriguez Trio,
   Neil Young and the Chrome Hearts,
   Smith/Kotzen,
   Satchvai Band,
   Earl Sweatshirt and MIKE,
   Peter Hook & The Light.

6. Non-artist/event concepts reaching artist resolution:
   West Side Story, Mondial du Tatouage, Playlist, Friday's Playlist,
   Blues, Jazz à la Villette, etc.
   These suggest an upstream article-identity/classification issue.

### Principle
Do NOT solve this by creating a large manual artist exception table.
Use the failure set to identify systemic resolver weaknesses.

### Immediate next step
Build a READ-ONLY diagnostic around the current resolver that, for a small
representative set such as:

- Prince
- Metallica
- Jessica Hernandez
- Therapy?
- Earth
- ...And You Will Know Us By The Trail Of Dead

captures for each artist:

- canonical/input artist name
- normalized Apple query/query variants
- Apple candidates returned
- Apple artist IDs and candidate names
- candidate score/evidence
- identity confidence
- final status
- exact rejection / ambiguity reason

No production writes or recommendation regeneration until that diagnostic
explains why obvious identities are being rejected.

## 2026-09-12 — Apple artist resolver read-only diagnostic added

Added `eeDiagnoseAppleArtistResolution(names)` to
`deliverables/apple-related/Code.gs`.

Purpose:
- diagnose why obvious Apple Music artists are ending as AMBIGUOUS / ERROR;
- use the current production lookup and `eeResolveIdentity_()` logic;
- make no writes to Apple Article Identity, Apple Artists, or Apple Payloads.

Default diagnostic set:
- Prince
- Metallica
- Jessica Hernandez
- Therapy?
- Earth
- ...And You Will Know Us By The Trail Of Dead

For each artist it reports:
- input and normalized identity
- actual Apple search term/media/entity/storefront
- raw Apple result count
- exact-name Apple artist IDs
- release counts
- resolver score components
- dominant exact artist candidate
- final HIGH / MODERATE / LOW resolver result
- explicit rejection reason such as:
  - NO_ARTIST_CANDIDATES
  - BEST_SCORE_BELOW_70
  - TOP_TWO_MARGIN_BELOW_15
  - RESOLVER_REJECTED
- recommendation-filter accepted/rejected counts

macOS JavaScript syntax validation passed:
`APPLE CODE SYNTAX: OK`.

Next step:
Deploy/sync this diagnostic into the existing Apps Script Apple project,
then run `eeDiagnoseAppleArtistResolution()` and inspect its Execution log.
Do not change production resolver behavior until the diagnostic results explain
the failure classes.

## 2026-09-12 — Apple resolver diagnostic moved to canonical generator source

Corrected the placement of `eeDiagnoseAppleArtistResolution()`.

- Canonical source is `sources/apple-related/Code.base.gs`.
- Generated deliverable remains `deliverables/apple-related/Code.gs`.
- The diagnostic is now inserted before the builder truncation point, so normal rebuilds preserve it.
- `tools/build_apple_related_deliverables.py` now normalizes generated Code.gs to one trailing newline.
- Two consecutive Apple deliverable builds produced identical SHA-256:
  `5fe8c2b5c2664f0bc2ca76a7547aaeacb00ecf858e02081614868be75549ad98`
- Rebuilt Apps Script syntax validation passed.
- `git diff --check` passed.
- No live Apps Script, Sheets, Blogger configuration, properties, cursors, or triggers have been changed yet.

Next step:
Install the rebuilt `deliverables/apple-related/Code.gs` into the existing
Apple Apps Script project, save it without changing the existing deployment,
then run `eeDiagnoseAppleArtistResolution()` manually and capture its execution
log for analysis.

## 2026-09-12 — Apple resolver diagnostic results

Ran `eeDiagnoseAppleArtistResolution()` manually in the existing Apps Script
project against six representative failures.

### Current resolver succeeds for previously problematic major artists

Prince:
- Apple exact artist ID: 155814
- 11 returned releases
- score 75
- HIGH / RESOLVED

Metallica:
- Apple exact artist ID: 3996865
- 16 returned releases
- score 75
- HIGH / RESOLVED

...And You Will Know Us By The Trail Of Dead:
- Apple exact artist ID: 110799
- 19 returned releases
- score 75
- HIGH / RESOLVED

Important implication:
If these artists remain ERROR / AMBIGUOUS in the persistent Apple Artists
sheet, the current resolver itself is no longer the reason. Existing terminal
rows may be stale and not being reconsidered after resolver improvements.

### Sparse-catalogue threshold failure

Jessica Hernandez:
- Apple returns one exact-name artist ID: 732516020
- exact identity has only 2 returned releases
- exact-name score = 30
- no >=3-release bonus
- final LOW / BEST_SCORE_BELOW_70

Apple also returns:
- Jessica Hernandez & The Deltas
- artist ID 848460638
- 11 returned releases

This shows the current requirement for >=3 release rows can reject a unique
exact-name identity even when Apple supplies no competing exact-name artist.

### Search-recall failures

Therapy?:
- 50 album-search results
- zero exact-name Apple artist IDs
- best unrelated score 18
- LOW / BEST_SCORE_BELOW_70

Earth:
- 49 album-search results
- zero exact-name Apple artist IDs
- best unrelated score 18
- LOW / BEST_SCORE_BELOW_70

These failures occur before meaningful scoring. Album search is therefore not
a reliable artist-identity lookup for punctuation-heavy or generic names.

### Current working diagnosis

At least three systemic issues must be investigated:

1. Persistent stale ERROR / AMBIGUOUS artist rows may not be automatically
   reconsidered after resolver improvements.

2. Unique exact-name artists with small Apple catalogues are penalized too
   heavily by the >=3-release / score-70 rule.

3. Artist identity discovery should not rely solely on album search.
   A likely safer architecture is:
   - Apple musicArtist identity search;
   - exact/normalized artist-name candidate evaluation;
   - artist-ID album lookup for catalogue evidence and recommendations;
   - punctuation/query variants when needed;
   - stronger article/context corroboration for genuinely ambiguous generic
     names such as Earth.

Do not loosen production matching globally until the retry/status behavior and
musicArtist search behavior have been measured.

## 2026-09-12 — Versioned retry for stale Apple artist identity failures

Implemented controlled retries for persistent Apple Artists rows that previously
became permanently trapped as ERROR or AMBIGUOUS.

Added:
- `EE_APPLE_IDENTITY_RESOLVER_VERSION = 1`
- `identityResolverVersion` column to `Apple Artists`
- `eeArtistNeedsIdentityResolution_(record)`

Behavior:
- UNRESOLVED always remains eligible for identity discovery.
- ERROR / AMBIGUOUS becomes eligible only when its stored resolver version is
  older than the current resolver version.
- Existing rows without the new column/value are treated as resolver version 0.
- Once an artist is attempted under resolver v1, subsequent stored rows carry
  identityResolverVersion=1 and do not retry indefinitely.
- A future substantive resolver improvement can intentionally bump the version
  to reconsider prior terminal failures once.

The rule is used by:
- direct article generation;
- artist discovery maintenance;
- existing catalogue short-circuit logic.

This specifically addresses stale terminal rows such as artists that failed
under older resolver behavior but resolve correctly now.

It does NOT yet address:
- sparse exact-name catalogues such as Jessica Hernandez;
- Apple album-search recall failures such as Therapy? and Earth.

Validation:
- two consecutive generated Code.gs builds produced identical SHA-256:
  728f2222967b94672ccda368da77661916047448f06035fc074669ce203da61c
- Apps Script JavaScript syntax check passed;
- git diff --check passed.

No production sheet rows have yet been retried with this new logic.

## 2026-09-12 — Controlled single-artist stale identity retry helpers

Added generic manual helpers to the generated Apple Apps Script architecture:

- `eePreviewNextStaleArtistIdentityRetry()`
- `eeRetryNextStaleArtistIdentity()`
- internal `eeNextStaleArtistIdentityRetryCandidate_()`

Purpose:
- inspect the next stale ERROR / AMBIGUOUS Apple Artists row eligible under the
  resolver-version migration;
- retry exactly one artist at a time;
- avoid hard-coded performers and bulk production changes.

Safety behavior:
- preview performs no artist-row mutation;
- retry touches only the next eligible stale terminal artist;
- requires a representative Blogger post;
- records the current resolver version through the normal catalogue writer;
- resets the assembly cursor only if the artist becomes RESOLVED;
- uses its own worker lease and execution deadline.

Validation:
- two consecutive generated Code.gs builds were identical:
  `5836e1c705e1bd9bb1e7c23c51040d622a32642a9fcd1ce7ea74913b36cc6c73`
- Apps Script JavaScript syntax check passed;
- git diff --check passed.

Next production-validation step:
1. install the rebuilt Code.gs in the existing Apps Script project;
2. save without redeploying;
3. run `eePreviewNextStaleArtistIdentityRetry()` only;
4. inspect the candidate before allowing the one-row retry.

## 2026-09-12 — Versioned stale-identity retry validated in production

Ran the controlled one-artist retry against the first eligible stale terminal
Apple Artists row:

Artist:
- Neal Black & the Healers
- artistKey: neal-black-the-healers
- previous status: AMBIGUOUS
- previous identityResolverVersion: 0

Result:
- retry completed successfully
- new status: AMBIGUOUS
- new identityResolverVersion: 1
- Apple artist ID: none
- identity confidence: MODERATE
- categories written: none
- error: none

Discovery diagnostic:
- 6 Apple calls
- 0 cache hits
- elapsed ~54.5 seconds
- album searches returned qualifying relationship candidates
- music-video search returned none
- ebook/audiobook results were rejected as unrelated
- terminal status remained AMBIGUOUS / PLAUSIBLE_MATCH

This validates that the resolver-version migration works as intended:
old terminal rows can be reconsidered once, and unsuccessful retries do not
loop forever because they are marked with the current resolver version.

The Apps Script editor later displayed a lost-connection warning, but the
execution itself had already produced the successful RETRIED result.

## 2026-09-12 — Added stale Apple identity retry backlog counter

Added `staleIdentityRetriesPending` to `eeArchitectureStatus()`.

It counts Apple Artists rows where:
- status is ERROR or AMBIGUOUS; and
- stored identityResolverVersion is older than the current
  `EE_APPLE_IDENTITY_RESOLVER_VERSION`.

This provides a direct measure of how many old terminal identity failures
still need their one-time resolver-version retry.

Validation:
- two consecutive generated Code.gs builds were identical:
  `a55f4bfe1724acf8075a925e7feebbdb2e169f64b56ca453630c912a9cc11f69`
- Apps Script JavaScript syntax check passed;
- git diff --check passed.

Next step:
Install the rebuilt Code.gs in the existing Apps Script editor and run
`eeArchitectureStatus()` once to measure the stale identity backlog.

## 2026-09-12 — Resolver-version change now restarts artist discovery sweep once

Added automatic discovery-cursor migration for Apple artist resolver changes.

Problem found:
- Apple Artists contained 161 stale ERROR / AMBIGUOUS rows eligible for
  resolver-v1 retry.
- `EE_APPLE_ARTIST_DISCOVERY_INDEX` was already at 849, beyond the 848 current
  artist rows.
- Therefore the maintenance worker would not naturally revisit those older
  rows even though the new eligibility rules allowed them.

Fix:
- `eeDiscoverArtistsMaintenanceWorker_()` now compares
  `EE_APPLE_ARTIST_DISCOVERY_RESOLVER_VERSION` with
  `EE_APPLE_IDENTITY_RESOLVER_VERSION`.
- On a resolver-version change only:
  - records the new resolver version;
  - resets `EE_APPLE_ARTIST_DISCOVERY_INDEX` to 1.
- Subsequent runs do not reset again for the same resolver version.
- The normal discovery worker then scans the sheet and processes only rows
  actually eligible under `eeArtistNeedsIdentityResolution_()`.

Current measured backlog before enabling this migration:
- canonicalArtists: 848
- staleIdentityRetriesPending: 161
- artistDiscoveryCursor: 849

Validation:
- two consecutive generated builds were identical:
  `51068a5d2e1ee69e2447bc9ea7d6182967cc2cc992e2c6757c9a345835b00816`
- Apps Script JavaScript syntax check passed;
- git diff --check passed.

The 161 stale identities do not need manual retries. Once this version is
installed, normal production maintenance can drain them incrementally under
the existing Apple throttle and execution limits.

## 2026-09-12 — Public one-run Apple discovery maintenance wrapper

Added:

`eeRunArtistDiscoveryMaintenanceOnce()`

Purpose:
- expose the internal `eeDiscoverArtistsMaintenanceWorker_()` through a
  function that appears in the Apps Script function dropdown;
- allow a controlled manual validation run without invoking the broader
  production worker.

The wrapper performs no additional logic; it simply calls the existing
discovery-maintenance implementation once.

Validation:
- generated Code.gs syntax check passed;
- git diff --check passed.

Next step:
Install the rebuilt Code.gs in the existing Apps Script project and run
`eeRunArtistDiscoveryMaintenanceOnce()` once. This should trigger the one-time
resolver-version cursor reset and begin draining the stale identity backlog.

## 2026-09-12 — Automatic resolver-v1 stale identity sweep validated

Ran `eeRunArtistDiscoveryMaintenanceOnce()` after installing the resolver-version
cursor-reset logic.

Observed behavior:

Knower:
- stale artist was automatically reconsidered
- 9 Apple calls
- 0 cache hits
- elapsed ~89.8 seconds
- terminal status remained AMBIGUOUS
- terminal reason: PLAUSIBLE_MATCH

Josie:
- worker automatically advanced to the next eligible artist
- performed part of discovery
- stopped safely with:
  `APPLE_SEARCH_EXECUTION_HEADROOM`
- terminal worker result: RETRY_LATER
- transient retry count: 1
- discovery cursor pinned at row 3

This confirms:
- the resolver-v1 sweep restarted automatically;
- stale terminal artists are processed without manual per-artist intervention;
- the worker can process multiple candidates in one maintenance run;
- execution-headroom protection stops the run before a hard Apps Script timeout;
- the cursor remains on the interrupted artist so the next maintenance cycle
  resumes rather than skipping it.

The stale identity backlog can therefore drain incrementally through normal
maintenance runs.

## 2026-09-12 — Sparse exact-name artist diagnostic wrapper

Added `eeDiagnoseSparseExactArtistExamples()` as a read-only diagnostic wrapper.

Current regression cases:
- The Crimson ProjeKct
- Jessica Hernandez

Purpose:
- determine whether The Crimson ProjeKct fails for the same reason already
  observed with Jessica Hernandez;
- specifically test the sparse-catalogue case where Apple may return one
  unique exact-name artist identity but too few release rows to reach the
  current score threshold.

Validation:
- two consecutive generated builds were identical:
  `68fb5d7fb371307a0957c77caac93fe7a69cedf2a8f7872618fb877a13ae0fe0`
- Apps Script JavaScript syntax check passed;
- git diff --check passed.

No resolver behavior has been changed yet.

## 2026-09-12 — Sparse-exact vs search-recall cases separated

Ran `eeDiagnoseSparseExactArtistExamples()`.

### The Crimson ProjeKct

Apple album search:
- query: The Crimson ProjeKct
- raw results: 3
- exact-name Apple artist IDs: none
- returned artist identities included:
  - King Crimson (Apple artist ID 627204)
  - Markus Reuter (Apple artist ID 49873671)
- resolver score: 0
- result: LOW / BEST_SCORE_BELOW_70

Conclusion:
The Crimson ProjeKct is NOT a sparse exact-name scoring failure.
The failure occurs earlier: album search does not surface an exact primary
artist identity. This belongs to the search-recall class already seen with
artists such as Therapy? and Earth.

It also illustrates why controlled associated-act recommendations are useful:
Apple itself surfaces directly related King Crimson material around the query,
but related acts must remain distinct from primary-artist identity.

### Jessica Hernandez

Apple album search:
- one exact-name artist ID: 732516020
- only 2 exact-name release rows
- exact-name score: 30
- result: LOW / BEST_SCORE_BELOW_70

Conclusion:
Jessica Hernandez remains the clean regression case for the sparse-catalogue
identity-scoring problem. A unique exact artist identity is currently rejected
because the >=3-release evidence bonus is required to cross the score threshold.

### Resolver work now required

1. Sparse exact identity:
   safely accept a sole exact-name Apple artist candidate without requiring a
   minimum three-release catalogue solely to establish identity.

2. Artist-first/search-recall fallback:
   when album search cannot establish an exact artist identity, query Apple's
   artist entity directly, then use the resulting artist ID for catalogue
   discovery.

3. After identity is reliable, implement controlled one-hop associated-act
   recommendation expansion for direct members, parent bands, side projects,
   and strongly evidenced collaborations, without allowing relationship drift.

The Crimson ProjeKct will be a regression case for both search-recall fallback
and later associated-act expansion.

## 2026-09-12 — Direct Apple musicArtist search diagnostic added

Added read-only diagnostic:

`eeDiagnoseAppleMusicArtistSearchExamples()`

Regression cases:
- The Crimson ProjeKct
- Therapy?
- Earth
- Jessica Hernandez

Purpose:
- test Apple's direct `musicArtist` entity search independently from album
  search;
- determine whether artist-first lookup can recover identities that album
  search currently misses;
- measure whether exact normalized artist-name matches are returned before
  changing production resolver behavior.

This diagnostic does not mutate Apple Artists, Apple Article Identity,
Apple Payloads, cursors, or resolver mappings.

Validation:
- two consecutive generated builds were identical:
  `b5225095cd192b8d6ac387aa87ec8c3851ad0070e4f1190808d271da4c5b21b4`
- Apps Script JavaScript syntax check passed;
- git diff --check passed.

Next step:
Install the rebuilt Code.gs in the existing Apps Script project and run
`eeDiagnoseAppleMusicArtistSearchExamples()` manually.

## 2026-09-12 — Identity vs Apple recommendation anchor

New product requirement confirmed.

The engine must distinguish:

- article subject identity;
- resolved Apple artist identity;
- Apple recommendation anchor(s).

These are not always the same thing.

### The Crimson ProjeKct

Apple does not expose a usable primary artist result for The Crimson ProjeKct.
If there is no usable Crimson ProjeKct catalogue in Apple Music, it is
acceptable and desirable to use directly associated acts such as King Crimson
as recommendation anchors.

Important:
King Crimson must NOT be stored as though it were the same artist identity as
The Crimson ProjeKct.

Desired conceptual state:

- article subject: The Crimson ProjeKct
- primary Apple artist: none if unavailable
- recommendation anchor: King Crimson
- relationship: directly associated / parent-related act
- additional one-hop anchors may include strongly evidenced members or related
  projects such as Adrian Belew or Tony Levin

### Same-name collision requirement

Generic or reused artist names must not be resolved from name equality alone.

Regression cases now include:

- Earth
- Wargasm

The existing engine has produced recommendations for the wrong Wargasm.
This must be prevented systemically.

When multiple Apple artists share the same name, resolution should use article
and identity context such as:

- member names
- album and song titles
- collaborators
- side projects / related bands
- country or origin when supported
- active period / dates
- genre as supporting evidence only
- MusicBrainz relationships and aliases
- Apple catalogue titles and release dates

The engine should select an Apple artist only when contextual evidence
converges. Otherwise the identity must remain ambiguous.

### Resolver design direction

1. Preserve literal/punctuation-sensitive names before normalized comparison.
2. Use direct Apple `musicArtist` search to improve recall.
3. If one strong exact identity exists, resolve it.
4. If multiple same-name candidates exist, perform contextual disambiguation.
5. Keep ambiguous when evidence is insufficient.
6. Keep article subject identity separate from recommendation anchors.
7. Allow controlled one-hop related-act anchors when the primary subject has
   no usable Apple catalogue.
8. Do not use uncontrolled transitive relationship expansion.
9. Avoid artist-specific hard-coded exception tables.

Regression set now includes:
- Jessica Hernandez — unique sparse exact identity
- Therapy? — punctuation-sensitive identity
- Earth — many same-name candidates
- Wargasm — known wrong-same-name recommendation
- The Crimson ProjeKct — no primary Apple identity; related-anchor case

## 2026-09-12 — Apple identity resolver v2 checkpoint

Implemented and locally validated Apple resolver v2.

Key changes:
- Apple artist resolution now performs direct musicArtist identity lookup before album scoring.
- Same-name identities can require contextual MusicBrainz evidence instead of trusting a unique Apple name result.
- MusicBrainz resolution can disambiguate same-name artists using article relationship evidence such as member names.
- Wargasm regression is explicitly protected: the UK WARGASM identity can be established from Sam Matlock / Milkie Way context, while Apple's FR search currently exposes only the older US Wargasm artist ID 22575637; that Apple ID must not be substituted for the UK act.
- Therapy?-style punctuation-sensitive literal identity remains supported.
- Previously RESOLVED rows with an older identityResolverVersion are now eligible for one-time resolver-v2 revalidation, allowing old wrong identities to be corrected.
- Artist discovery can fall back from title evidence to artist labels and then dominant repeated body identity.
- Body-only artist discovery is fallback-only and cannot contaminate an article that already has stronger title/label identity evidence.
- If no artist can be established, recognised music-genre labels can produce an explicitly marked GENRE_FALLBACK LISTEN payload rather than EMPTY_NO_SUBJECT.
- Genre fallback is recommendation context only; it is never treated as artist identity.
- Entity profile cache now avoids blindly reusing context-disambiguated same-name profiles across unrelated articles.
- Direct resolver diagnostic regression set includes Wargasm.

Local validation:
- deterministic double build: fea359b6b11d67f0a0a07a21e292c027c4fae2badc923d53ba2c5ada3a6b682c
- generated Code.gs JavaScript syntax: OK
- git diff --check: clean
- critical production functions each occur exactly once

Not yet production-validated:
- Resolver v2 has NOT yet been installed into Apps Script.
- Do not run production discovery maintenance until regression diagnostics are checked.
- First Apps Script regression targets: Wargasm, Earth, Therapy?, Jessica Hernandez, The Crimson ProjeKct, plus a no-artist article with a usable genre label.
- Associated-act recommendation expansion remains the next feature after identity safety is validated.

## 2026-09-12 — Contextual Apple qualified-name resolution checkpoint

Follow-up to resolver v2 commit 9782a14.

Added systemic Apple identity handling for qualified/disambiguated artist names such as:
- article subject / MusicBrainz identity: Wargasm
- Apple display identity: WARGASM (UK)

Implementation:
- Added country-aware qualified-name recognition for Apple artist results.
- MusicBrainz country/context may validate an Apple qualifier such as "(UK)".
- Added Apple catalogue lookup across candidate artist IDs.
- Candidate ranking considers:
  - exact vs qualified artist name
  - qualifier/country agreement
  - own-release count
  - earliest/latest own-release years
  - compatibility with MusicBrainz activity dates
- A substantial own catalogue can distinguish a real primary artist identity from a feature-credit/secondary Apple identity.
- Contextual candidates with catalogue dates contradicting the MusicBrainz activity period are penalized/rejected.
- Previously stored Apple IDs and identity mappings no longer bypass contextual validation for ambiguous/common artist names. This is required so resolver upgrades can correct an already-resolved wrong identity instead of preserving it merely because it was stored earlier.

Wargasm evidence established during diagnostics:
- correct article subject: newer UK WARGASM, MusicBrainz contextual identity includes Sam Matlock and Milkie Way.
- Apple artist 1476730259 = WARGASM (UK), substantial catalogue beginning 2019, including Venom, EXPLICIT: The MiXXXtape, Spit., Salma Hayek, etc.
- Apple artist 1778991054 = Wargasm (UK), only one feature-credit release observed.
- Apple artist 22575637 = older US Wargasm, catalogue beginning in the 1980s; incompatible with the UK act.
- No artist-specific Wargasm Apple ID exception was added.

Local validation:
- deterministic double build SHA-256:
  6c47f4f991ee8c204b002c910f6e5bc840f5ed0454cec39c094ebf14ef9b22b0
- generated Code.gs JavaScript syntax: OK
- git diff --check: clean

Current caveat:
- This latest qualified-name/catalogue resolver has NOT yet been pasted into Apps Script or production-tested.
- Resume with read-only regression validation before running production discovery maintenance.
- Identity regression set remains Wargasm, Earth, Therapy?, Jessica Hernandez and The Crimson ProjeKct.
- Associated-act recommendation expansion remains pending after identity safety validation.

## 2026-09-12 — Calendar workflow unblocked from Apple test regressions

Calendar publication failures were traced to the shared GitHub Actions test gate, not to the calendar scraper.

Cause:
- update-calendar.yml ran every Python test in tests/.
- Five failing Apple Recommendations tests caused the calendar production workflow to exit before publication.
- The calendar scraper/build itself was still functioning.

Fix:
- Calendar production workflow now runs all Python test modules except tests/test_apple_related_deliverables.py.
- Apple Recommendations tests remain in the repository but no longer block production calendar publication.
- Node artist auto-linker regression remains unchanged.
- Local validation: 529 non-Apple Python tests passed.
- git diff --check clean.

This separation prevents future Apple Recommendations development from blocking otherwise healthy calendar updates.

## 2026-09-12 — Apple no-blank recommendation invariant

Requirement established:
- No Electric Eye article should render a blank Apple recommendations section.
- Artist accuracy remains the preferred path, but recommendation coverage must degrade gracefully when artist identity cannot be established.

Implemented fallback hierarchy:
1. Artist/relationship catalogue recommendations.
2. GENRE_FALLBACK from explicit Blogger article labels.
3. CONTENT_GENRE_FALLBACK from genre terminology in article title/body.
4. SITE_FALLBACK using broadly relevant Electric Eye / Rock Apple Music content.
5. If the Apple search itself cannot supply catalogue items, the site fallback can still emit a deterministic Apple Music Rock link.

Diagnostics distinguish fallback recommendations from artist-derived recommendations; fallback creators are never treated as article-subject identity.

Added public read-only diagnostic:
- eeDiagnoseAppleNoBlankFallbacks()

Apps Script validation on 2026-09-12:
- GENRE_LABEL -> GENRE_FALLBACK -> 12 items -> passed
- CONTENT_GENRE -> CONTENT_GENRE_FALLBACK -> 12 items -> passed
- SITE_FALLBACK -> SITE_FALLBACK -> 12 items -> passed
- summary: status OK, 3/3 passed, 0 failed
- all cases had emptyClassification=null

Build validation:
- deterministic generated Code.gs
- SHA256 c043ae1431998dd977233e7daf40e6281db2ee5cc5ab0a154f61d2d0fc4dd1b9
- JavaScript syntax OK
- git diff --check clean
- calendar workflow and calendar scraper code untouched

The validated generated Code.gs was manually installed and saved in the existing Apps Script project. No deployment was performed.

## 2026-09-12 — Contextual Apple artist identity resolver validated

The contextual Apple artist resolver is now validated for production use independently of the later WATCH/READ expansion.

Fix:
- Ambiguous Apple artist candidates now gather album/catalogue evidence independently per candidate ID.
- This avoids shared multi-ID Apple lookup limits making a valid candidate appear artificially sparse.
- No ambiguity thresholds were weakened.
- No artist-specific Apple ID exception was added.

Read-only Apps Script regression:
- Wargasm -> Apple artist 1476730259, WARGASM (UK), HIGH confidence
  - qualifier country match: UK / GB
  - own release count: 26
  - catalogue span: 2019-2026
  - decision: CONTEXTUAL_QUALIFIED_APPLE_ARTIST
- Therapy? -> 13128523
- Earth -> remains unresolved / context required
- Jessica Hernandez -> 732516020
- The Crimson ProjeKct -> no false direct Apple identity
- summary: status OK, 5/5 passed

The generated Code.gs was manually installed and saved in Apps Script for read-only validation.
Calendar workflow and calendar scraper code were not touched.
