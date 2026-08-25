## Context

See proposal.md - Why. Step ① shipped organizer identity, org-per-tenant
Zitadel tenancy, the `organizer.html` console, and the org-scoped
`rpc.organizer.v1.OrganizerService` (`Get` + `ListArtists`). The concert
model (`Series`/`Event`/`Venue`/`event_performers`) exists, and
`CONCERT.created` already drives follower push (the `notify-concert`
consumer → `NotifyNewConcerts`).

**Depends on `fix-series-fragmentation` (spec#869).** That change makes
discovery **series-grouped**: the payload is
`DiscoveredSeries{ Title, Type, SourceURL, Events[] }`, a series row is
created **once** when its `series_id` is resolved (via a shared
`(artist, dates)`-adopt-else-mint helper reused by discovery and approval),
`staged_concerts.series_id` is a **real FK** (no materialize/adopt
branching), events converge on the natural key
`uq_events_natural_key(venue_id, local_event_date, start_at)`, and
**publish emits one `CONCERT.created` per series** (carrying all its event
ids). ② is authored against **this** model, reuses its shared
series-resolution helper, and sequences after its backend implementation
lands. Competitor field research informs the field set; see
`docs/organizer-platform-design.md`.

## Goals / Non-Goals

**Goals:** the smallest data model that lets an organizer publish an
informational concert page, reusing the fix-series-fragmentation
series-grouped persistence + the existing notify pipeline; add only the
writer, ownership, visibility, lifecycle, and image hosting.

**Non-Goals:** ticketing (④); rich authoring
(`organizer-event-authoring-extensions`).

## Decisions

**D1 — Times live at the `Event` (performance) level. [confirmed]**
tiget puts 開場/開演 at the *ticket-type* level because it has no separate
performance or discovery entity and its sellable unit collapses
(showtime × price × capacity) — a small-seller simplification at the cost of
normalization. Liverty is the opposite: **`Event` = a concert performance is
load-bearing across the shipped product** (discovery, followers, proximity,
`CONCERT.created`→notify), and the industry model (eplus 公演/席種, ぴあ,
Ticketmaster) separates performance from price. So times stay on `Event`; ④
attaches ticket types/lottery per `Event`; a 2部制 day is multiple `Event`s
under one `Series` (the natural key already distinguishes same-day
showtimes). The "one page, multiple showtimes" UX is the `Series` page
listing its `Event`s.

**D2 — Minimal fields on `Series`; origin derived from `organizer_id`.**
Add to `Series`: `description`, `cover_image`, `visibility`
(`PUBLIC`/`UNLISTED`), `publish_state` (`DRAFT`/`PUBLISHED`/`CANCELLED`),
`organizer_id` (owner). A non-null `organizer_id` marks first-party. `Event`,
`Venue`, `event_performers` reused unchanged. **A first-party concert is a
`Series` authored via the fix-series-fragmentation series-resolution path**,
so an organizer-authored tour is one `Series` with its `Event`s — grouping is
structural, same as discovery.

**D3 — Dedicated `rpc.organizer.v1.ConcertService`, bare verbs, VO fields.**
Concert authoring is its own org-scoped service (mirroring admin
`ConcertService` + AIP one-service-per-entity), NOT bolted onto the
identity `OrganizerService` (which stays `Get`/`ListArtists`). Bare-verb
methods: `Create` (Series+Event(s)+performers → DRAFT), `Update` (draft or
published correction), `Cancel`, `Publish`, `UploadCoverImage`,
`RegenerateToken`, `List` (own). Org-scoped auth reuses ①'s role claim;
artist ownership checked against the represented-artists set. **Fields are
wrapper VOs** per repo convention: `cover_image` is the existing `Url` VO,
`description` a `Description` VO with protovalidate length bounds; the
unlisted token is backend-only (not on the read DTO). **Enum final shapes
are declared now** so extensions is purely additive: `Visibility` =
`UNSPECIFIED(0)` / `PUBLIC` / `UNLISTED` (reserve `PASSWORD` for
extensions); `PublishState` = `UNSPECIFIED(0)` / `DRAFT` / `PUBLISHED` /
`CANCELLED` (reserve `SCHEDULED` for extensions).

**D4 — Publish, notification gating, supersede — aligned to #869.**
- Publish a `PUBLIC` series emits **one `CONCERT.created` per series**
  (carrying the newly-published event ids), matching
  fix-series-fragmentation's publish-once-per-series. `DRAFT`/`UNLISTED`
  emit nothing. Publishing an additional `Event` later under an
  already-published series emits `CONCERT.created` for that series with only
  the new event id(s) (so followers hear about a genuinely new date, once).
- **Supersede via the shared series-resolution + natural-key upsert, NOT the
  old AdoptStaged path** (which fix-series-fragmentation removes). An
  organizer's events insert under the organizer's own `series_id`; the event
  natural-key upsert converges on any existing row at
  `(venue, date, start)`. If that row belongs to a **discovered** series, the
  first-party publish claims it: re-point the event to the organizer's series
  and mark it organizer-owned, without re-emitting `CONCERT.created` if it
  was already announced. A matching `staged_concert` is dropped. A matching
  **suppressed** slot is NOT silently resurrected — publishing into a
  suppressed slot requires an explicit organizer action (see Risks).
- **Cross-organizer collision** (a slot already owned by a *different*
  organizer's first-party series) is NOT an automatic takeover: it is a
  conflict routed to admin reconciliation, never a silent `organizer_id`
  overwrite.

**D5 — Scraping exclusion filters the discovery cron, keyed on association.**
The discovery job loops `FollowRepo.ListAll` → `SearchNewConcerts(artist)`.
Exclusion SHALL filter that artist list **before** calling
`SearchNewConcerts` (i.e. skip the Gemini call entirely for artists
associated with an active organizer) — not merely drop results at the
downstream ingest/suppression stage. Associating an artist starts the
exclusion; disassociating or deactivating the organizer resumes scraping.
Reuses the associate/disassociate/deactivate lifecycle from
`organizer-accounts`; matches the roadmap "represented ⇒ excluded".
*Trade-off:* an artist associated but not yet authored has no scraped
concerts during that window; accepted (vetted partners commit to author;
reversible).

**D6 — Unlisted = signed tokenized URL, regenerable.** `UNLISTED` concerts
carry an HMAC-signed token in their share URL; the public read path verifies
it (constant-time) and is excluded from all list/discovery/notify queries.
The owning organizer can regenerate the token (invalidating the old URL). No
referrer control.

**D7 — Cover image hosting (the one new infra).** Organizer upload →
type/size validation → GCS → served via a stable URL persisted on the
Series. MVP: one image. Bucket provisioned in cloud-provisioning.

## Relationship to fix-series-fragmentation (#869) and to ③

- ② **reuses** fix-series-fragmentation's shared series-resolution helper and
  its publish-once-per-series emit; it does not re-implement grouping or
  reference the removed AdoptStaged/materialize path. ② should land after
  that change's backend persistence is in place.
- Because `CONCERT.created` (now one per series) drives the existing
  follower push, a `PUBLIC` publish **gets follower notification for free**.
  This makes roadmap step ③ largely redundant — ③ collapses to at most a thin
  change (organizer-specific copy / deeplink) and may be dropped; re-scope ③
  after ② ships (update the roadmap accordingly rather than deciding it
  silently here).

## Risks / Trade-offs

- **Double-notify on supersede** → claiming an already-announced discovered
  event does NOT re-emit `CONCERT.created`; new PUBLIC events emit once, per
  series.
- **Suppressed-slot resurrection** → a first-party publish into a suppressed
  `(venue,date,start)` must be an explicit, logged organizer action, not a
  silent bypass of the suppression gate.
- **Cross-organizer takeover** → routed to admin reconciliation, never an
  automatic `organizer_id` overwrite.
- **Draft/unlisted/cancelled leakage** → a shared guard excludes them from
  every public/follower/notify query; test explicitly.
- **Exclusion coverage gap** (D5) → accepted; reversible via disassociate.
- **Image abuse** → server-side type/size validation; moderation deferred.

## Migration Plan

1. spec: additive `Series` fields + authoring RPCs → Release → BSR gen.
2. cloud-provisioning: GCS bucket + access.
3. backend: migration; authoring usecase reusing the fix-series-fragmentation
   series-resolution helper; publish (per-series gated emit + natural-key
   supersede + suppression/cross-org handling); association-keyed discovery
   exclusion in the cron; token sign/verify/regenerate; image upload;
   edit/cancel; `organizer.concert.published` analytics.
4. frontend: console authoring screens; unlisted route token validation.
- Rollback: additive; drafts/unlisted/cancelled inert; new columns nullable.

## Open Questions

- Per-`Event` (date-specific) description — deferred to extensions.
- RPC naming/placement + field VO-wrapping — resolve per the code review
  before the proto lands.
