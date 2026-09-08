# Official outer-IDF parser fixtures

Captured 2026-09-07 from the venues' public official ticket offices/agendas:

- https://lempreinte.mapado.com/
- https://billetterie.leplan.com/
- https://leforum.cergypontoise.fr/agenda

`official_extracts.json` retains selected listing cards and the corresponding
event-page Next.js entities / JSON-LD. It is a parser fixture, not a programme
snapshot for publication. The two Mapado listing collections are reduced to the
selected examples, with `hydra:totalItems` adjusted to that fixture subset.
Detail occurrence collections retain their source counts and timestamps.

Examples cover a flat full bill, Le Plan's Club/Grande Salle and inverted raw
city/postcode, a non-concert conference, a sold-out Forum concert, and the two
off-site Forum listings (including explicitly enumerated October 8/9 evenings).
Tests always inject a fixed reference date; they do not require network access.

Full temporary captures and replay output are deliberately outside the repository.
