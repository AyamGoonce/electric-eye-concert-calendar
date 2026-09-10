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
