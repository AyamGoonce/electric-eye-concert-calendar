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
