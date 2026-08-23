# Reviewed artist genre research — 2026-08-23

## Audit scope and method

The published 1,709-event baseline contained 1,266 blank genre rows. Five were
festival days and 1,261 non-festival rows represented 1,203 exact normalized
headliner identities. The inventory is unusually long-tailed: 1,172 identities
occur once, 25 occur twice, three occur three times, and one each occurs five,
six, and nineteen times. Several repeated identities are show, convention, or
series titles rather than artists.

The controlled audit queried 976 simple exact labels against Wikidata P136. It
never runs during production. Exact-label collisions, non-musical entities,
unknown styles, and evidence spanning multiple public buckets were rejected.
High-impact misses were then checked against official artist/promoter/venue
biographies and reputable editorial references. Existing authoritative event
genres remained higher priority throughout.

The dictionary grew from 36 to 142 records:

- 36 prior editorial reviews, migrated to structured provenance;
- 104 reviewed Wikidata structured-genre records;
- one official artist biography (Ysé);
- one reputable editorial biography (Alice on the Roof).

No researched record is fetched or refreshed by the six-hour workflow. The
complete raw inventory, mappings, provenance, unresolved identities, and build
coverage are included in `automation-report.json`, uploaded with every Actions
run.

## Conflict handling

No accepted research record conflicted with an existing artist mapping. Six
apparently unambiguous automated candidates were rejected during identity or
semantic review (`Tommy Barlow`, `LOST`, `Haunt Me`, `The Buoys`, `Catch Your
Breath`, and `Mark Lettieri`). The existing Hollywood Vampires event-source
conflict remains blank. A duplicate canonical mapping is a validation error;
new contradictory evidence must be recorded and reviewed rather than replacing
the old record by load order.

## Concise manual-review queue

These are the remaining highest-impact or clearest ambiguous identities. The
machine artifact contains the complete queue.

| Identity | Rows | Candidate buckets | Why unresolved |
|---|---:|---|---|
| Roméo & Juliette | 19 | — | Musical/show title; raw value is generic `Other`, not a stable artist identity. |
| Gildaa | 6 | French chanson; World / Latin; Jazz / Blues; R&B / Soul / Funk | Official venue biography explicitly spans chanson, baile funk, jazz and R&B. |
| Mardi Jazz! | 5 | Jazz / Blues | Recurring series title; not enough event-specific evidence to label every edition. |
| MaMA Music & Convention 2 | 3 | — | Convention/event product rather than one artist. |
| Alma Rechtman | 3 | Folk / Country; Jazz / Blues; R&B / Soul / Funk; World / Latin | Official promoter biography explicitly cites soul, jazz and folk; no dominant bucket. |
| Dov'è Liana | 2 | Pop; Rock / Indie / Punk; Electronic | No sufficiently authoritative single-bucket evidence located. |
| Saint Levant | 2 | Hip-hop / Rap; R&B / Soul / Funk; Pop | Wikidata and event metadata consistently span several buckets. |
| FFF | 2 | Rock / Indie / Punk; R&B / Soul / Funk | Event evidence is explicitly funk and rock. |
| Asaf Avidan | 2 | Folk / Country; Rock / Indie / Punk | Structured evidence includes both folk and indie rock. |
| Camille | 2 | Pop; French chanson | Source metadata supplies both pop and French variété. |
| Ben Harper | 2 | Folk / Country; Rock / Indie / Punk; Jazz / Blues | Career evidence spans folk, rock and blues without a safe event-specific default. |

Correct blank values remain preferable to assigning a commercially convenient
or first-listed category.
