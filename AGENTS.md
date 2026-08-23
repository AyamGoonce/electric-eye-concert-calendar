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
- In visible output, show the venue alone for Paris and `Venue (Town)` outside
  Paris. Keep city and department structured internally.
- Do not accidentally commit generated calendars, scrape snapshots, logs,
  downloaded assets, caches, `unknown_venues.txt`, or secrets.
- Keep one logical source or product change per commit where practical. Run the
  focused tests and a full live pipeline before major commits.
- Preserve Git history. Do not reset, rebase, squash, or rewrite existing work.
