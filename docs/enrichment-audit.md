# Final enrichment and prototype audit

Audit date: 2026-08-23. Baseline: 1,708 published events at Pages commit
`6a0105966d57f0757aaea76813e4b3e2bc27f202`.

## Genre method

Public genre has a closed 12-label vocabulary. Each deduplicated event retains
all non-empty raw/source evidence. Enrichment applies event-specific reviewed
evidence, detects cross-source conflicts, then uses an exact normalized artist
mapping. It never guesses from name, venue, promoter, ticket price, billmates,
or festival headliner. The build report contains completeness counts, the full
raw-value frequency/source inventory, unresolved values, and conflicts.

The baseline had 355 populated and 1,353 blank genres (20.78%). Reproduction
from the immutable published payload and final reviewed rules classified those
blanks as: A no raw evidence 1,188; B generic/unapproved raw evidence 43; C
multi-category ambiguous raw evidence 104; D safe raw-mapping gaps 11; E exact
reviewed artist enrichment 7. The categories are exclusive and sum to 1,353.
The production build report records the complete raw frequency/source inventory
and unresolved values so this audit can be repeated rather than curated by hand.

## Image feasibility

The model and all 25 production adapters were audited. Zero adapters currently
extract an image URL, dimensions, provenance, licence/reuse signal, or expiry
information, so production coverage is 0/1,708 (0%). Several source payloads or
pages visibly contain promotional artwork, but their contracts differ: some
are remote CMS/CDN derivatives, some ticketing artwork, and some page-level
Open Graph images that may be venue logos or generic campaigns. The existing
pipeline cannot yet prove that a URL is event-specific, durable, reusable, or
an appropriately sized thumbnail across all sources.

Direct hotlinks avoid repository growth but transfer reliability, privacy,
expiry, and hotlink-policy risk to 25 third parties. Caching improves delivery
control but copies third-party promotional material, adds rights/terms review,
workflow download time, storage/retention cleanup, and possible stale artwork.
Mass caching is therefore not justified. Arbitrary image search, generated
images, inferred artist photos, and generic placeholders are prohibited.

Recommendation: keep Compact as the only production/default mode for this
release. It makes zero image requests and retains the current density. A later
source-by-source Images experiment should begin only with an official API that
provides event-specific stable thumbnails and a reviewed reuse policy; it must
remain opt-in, lazy-load near-viewport images with dimensions, and collapse
cleanly to the existing text row on any failure. Festival rows must use
festival/day artwork, never an implied headliner portrait.

## Electric Eye archive architecture

Do not query Blogger from the browser or once per event. A future independent
archive export should create one compact build-time map from canonical artist
identity to public Electric Eye post URLs. Calendar export can then attach at
most one exact reviewed URL per event. Collisions, group/solo ambiguity, tribute
acts, and festivals remain blank. Public presentation should be a restrained
`ELECTRIC EYE ARCHIVE` action after the core calendar actions. No archive link
is shipped in this pass because no authoritative archive index was supplied.

## Date navigator evaluation

`prototypes/date-navigator.html` implements the requested accessible,
horizontally scrolling near-term strip without document overflow. It makes
“what is on Thursday?” direct, but duplicates Tonight/This Week/This Weekend
and Month, adds 18 controls above an already capable filter bar, and is weakest
for the calendar's long horizon. Recommendation: do not ship it by default.
Retain the prototype for a later reader test; if adopted, it should set the
existing date filter rather than introduce new state semantics.
