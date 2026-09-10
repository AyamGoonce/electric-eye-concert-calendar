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
