# IDF Concert Calendar project rules

- The calendar covers concerts in Île-de-France. Scrapers may emit nationwide
  records when the central geography filter can classify them reliably.
- Each scraper exposes `SOURCE_NAME` and `load_events()`, uses bounded network
  requests, returns `ConcertEvent` records, and deduplicates its own output.
- `ConcertEvent.promoters` contains actual promoters only. Never use it for
  scraper or aggregator attribution, and never label DICE as a promoter.
- Preserve explicit billing. Do not invent openers or infer hierarchy from
  separators unless the source provides that hierarchy.
- Prefer official promoter and venue records over aggregators. DICE remains a
  low-priority gap-filling source and must load after official sources.
- Deduplicate conservatively with explicit aliases or tightly constrained
  normalization. Do not add fuzzy matching by default.
- Keep reviewed artist aliases, descriptive-title equivalences, and relocated
  event venue rules centralized in the deduplication layer. A terminal generic
  `+ Guest(s)` marker is comparison-only and requires an event-specific ticket,
  shared promoter, or official-source plus DICE corroboration.
- Canonicalize verified venue aliases before event identity. Venue names and
  municipalities remain separate; reviewed venue geography may correct stale
  source city data.
- Preserve genuine multiple performances through explicit early/late, set, or
  time-labeled billing. A shared product URL is diagnostic evidence, not by
  itself permission to merge performances on different dates.
- In visible output, show the venue alone for Paris and `Venue (Town)` outside
  Paris. Keep city and department structured internally.
- Do not accidentally commit generated calendars, scrape snapshots, logs,
  downloaded assets, caches, `unknown_venues.txt`, or secrets.
- Keep one logical source or product change per commit where practical. Run the
  focused tests and a full live pipeline before major commits.
- Preserve Git history. Do not reset, rebase, squash, or rewrite existing work.
- Production refreshes run in GitHub Actions, never through a scheduler on the
  user's Mac. The workflow runs every six hours and also supports a manual
  `workflow_dispatch` refresh.
- A failed scrape, test, production validation, regression guard, or hosted
  integrity check must fail the workflow without replacing the last-known-good
  Pages data.
- GitHub Pages hosts the static calendar assets; Blogger remains the website.
  Routine data refreshes require no Blogger edits.
- Treat `calendar-renderer.js` and `calendar.css` as stable assets. Routine
  publication updates the content-addressed data file and
  `calendar-current.js`, changing stable assets only when their source changes.
- Retain the current and two prior hashed data assets on Pages for rollback.
- Festival-day records retain complete authoritative lineups internally. The
  renderer may initially show five non-headliners, but search and expansion
  must use the complete lineup.
- Preserve `first_seen` in `proof/calendar-state.json`; derive NEW only within
  72 hours. Never publish candidate state after failed validation.
- Calendar dates and freshness use `Europe/Paris`. Quick weeks are Monday to
  Sunday; weekend means Friday through Sunday of the current/upcoming weekend.
- Preserve human-readable URL state for search, venue, genre, month, quick
  date, Newly added, and sorting.
- Sold out requires explicit structured source evidence. Missing tickets or
  source disappearance never imply sold out, cancellation, or postponement.
- Public genre is presentation-only and must be one of the 12 labels in
  `genres.PUBLIC_GENRES` or blank. Preserve source evidence, use reviewed exact
  mappings, report conflicts, and prefer a correct blank to an inference.
- Genre research is a controlled, human-reviewed maintenance task, never a
  six-hour build dependency. Prefer existing authoritative event evidence,
  official artist biographies, MusicBrainz/Wikidata structured data, then
  corroborated reputable editorial sources. Reject identity collisions,
  multi-bucket evidence, and unsupported tag clouds.
- Keep reviewed artist genres in `genre_mappings.json` with evidence. Artist
  matching is canonical and exact, never fuzzy; festival days do not inherit a
  headliner's genre.
- Every reviewed mapping records evidence source/type, review date, source URL
  where available, and notes. Event-specific evidence beats editorial override,
  which beats artist fallback. Conflicting research remains in the review queue
  and must never silently replace an existing mapping.
- Stable public event IDs derive only from canonical date, headliner, and venue.
  Metadata improvements must not break direct links or reset event state.
- Ticket states are only `tickets`, `sold_out`, `free`, `not_on_sale`, or blank,
  and require source evidence. Calendar files are all-day unless a reliable
  source time exists.
- Multi-genre selection is OR within Genre and AND against other filters. URL
  state overrides local preferences; corrupt browser storage must fail safely.
- Change reporting is diagnostic. Disappearance does not mean cancellation;
  support additions may later power NEW SUPPORT but must stay distinct from NEW.
- Do not query Blogger per event. Any Electric Eye archive link must come from
  a build-time canonical index and remain blank when identity is ambiguous.
- Event imagery requires explicit source provenance, stable reuse rights, lazy
  loading, and a no-image fallback. Compact mode must issue zero image requests.
- The Mac manual-update helper only dispatches the existing GitHub workflow;
  it never scrapes locally and contains no credentials.
- Before Blogger go-live, configure an AdSense exact-URL exclusion for the
  calendar Page. Never hide served Auto Ads with CSS.
- Never commit GitHub credentials, personal access tokens, or other secrets.
