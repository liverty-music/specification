## Context

Today's `events` table stores every individual concert as a flat row, with `title` and `source_url` repeated per stop of a multi-day tour or festival and a single `artist_id` per event. The proto layer exposes `Concert` (RPC-facing DTO with the same flat shape) and `Event` (defined but currently unused in any RPC). The natural key `UNIQUE(artist_id, local_event_date)` enforces an "one artist cannot play two venues on the same day" invariant that is incidentally true today but does not survive M:N performer modeling.

The Liverty Music product roadmap calls for tour-scoped notifications ("follow this tour"), tour-overview pages, tour-level ticket-purchase URLs, festival lineup support, and richer auto-discovery output where Gemini returns a tour title alongside individual stops. All of these require a first-class parent entity above `Event` and a way to attach multiple performers to a single event.

Industry surveys (Schema.org `Event`/`subEvent`, Songkick `Event`/`Performance`, Eventbrite recurring `Series`/`Occurrence`, Ticketmaster `Event`/`Attraction`) converge on a parent-child shape; the divergence is mainly in naming. Production has not been released yet, so the migration can be aggressive (`TRUNCATE`).

## Goals / Non-Goals

**Goals:**

- Introduce a parent entity that owns tour/series-level metadata shared across multiple events.
- Support multiple performing artists per event (festival lineups, co-headliners).
- Keep the existing `Concert` DTO usable from downstream consumers (frontend), populated via JOIN in handlers.
- Preserve the existing `EventId` and downstream FK shape (`tickets.event_id`, etc.) — no churn in ticket/journey/email/merkle/nullifier tables.
- Single, atomic Atlas migration with no data-rescue step (acceptable because prod is empty).

**Non-Goals:**

- Designing tour-scoped notifications, follow flows, or UI screens — those are downstream changes that depend on this data model.
- Changing the Gemini auto-discovery prompt or `SearchNewConcerts` behaviour — tracked separately (likely a `auto-discovery-series-grouping` change). The handler shipped here will create one `Series` per `Event` (1:1 fallback) so existing discovery code keeps working.
- Tour-level ticket purchase URL, cached `start_date`/`end_date`, or any other `Series` field beyond what the product needs today (YAGNI).
- Restructuring `ConcertService` RPC signatures — the proto field changes are deliberately confined to the `Concert` message body.
- Cleaning up the `concerts` table beyond removing the now-redundant `artist_id` column. The table is retained as a placeholder for future music-specific extensions per the existing `event-management` "Event-Type Extensibility" requirement.

## Decisions

### Decision 1: Parent table named `series` (not `event_series` or `tour`)

- **Choice**: Top-level table `series` with FK `events.series_id`; proto `Series` / `SeriesId` / `SeriesType`.
- **Alternatives considered**:
  - `tour` — rejected: too narrow, does not naturally cover festivals, residencies, or 2-day single-venue runs.
  - `event_series` — rejected: forces either stuttering FK (`event.event_series_id`) or FK/table-name mismatch. The schema's existing convention is that top-level entities with their own identity get simple plural names (`users`, `artists`, `venues`, `events`, `tickets`); compound names (`artist_official_site`, `followed_artists`, `ticket_emails`) are reserved for relationship or attribute tables.
  - `EventSummary` (user's original draft) — rejected: "summary" reads as a presentation/DTO concept, not a domain entity.
- **Rationale**: `series_id` → `series` matches the established FK convention. Domain context (music + events) eliminates the genericity concern; if a future "data series" or "time series" concept ever appears, it can take a qualified name.

### Decision 2: `series_type` enum (PG ENUM + proto enum) with three values

- **Choice**: PG `CREATE TYPE series_type AS ENUM ('TOUR', 'SINGLE', 'FESTIVAL')`. Proto `SeriesType` with `SERIES_TYPE_TOUR=1`, `SERIES_TYPE_SINGLE=2`, `SERIES_TYPE_FESTIVAL=3`.
- **Alternatives considered**:
  - `TEXT` column — rejected: weaker constraint, no compile-time check downstream.
  - `SMALLINT` (as used by `ticket_emails.email_type`) — rejected: the existing SMALLINT pattern predates the team's preference for explicit ENUM types and loses self-documentation.
  - `TOUR` + `SINGLE` only (MVP minimum, user's initial proposal) — rejected: festivals are a stated use case (M:N performers were added specifically for them) and need different UI/notification treatment than tours; adding the enum value here costs nothing.
  - Add `RESIDENCY` / `STREAMING` — deferred: no current product requirement. Enum values are additive (non-breaking), so can be added later.
- **Naming `type` vs `kind`**: the codebase already uses `_type` suffix elsewhere (`email_type`, see `ticket_emails`). `type` wins on consistency.

### Decision 3: `events` keeps its identity (`events.id` unchanged); `Event` proto slimmed to match

- **Choice**: `events` is the child table; its primary key and row identity are preserved. The `Event` proto is rewritten to reflect the slimmed schema (`id`, `series_id`, `venue`, `local_date`, `start_time`, `open_time`, `merkle_root`).
- **Alternatives considered**:
  - Rename `events` → `event_occurrences` (or similar) and create a brand-new `events` parent table — rejected: would force renaming `tickets.event_id`, `ticket_journeys.event_id`, `merkle_tree.event_id`, `nullifiers.event_id`, `ticket_emails.event_id` and updating every Go/TS consumer of those columns. The `event_id`-keyed downstream tables already mean "the per-day concert this ticket grants entry to," which is precisely what the child entity represents.
  - Leave the `Event` proto unchanged because it is unused — rejected: keeping a stale `Event` definition that contradicts the DB shape is worse than rewriting it. Doing so here keeps proto/schema parity even though no current RPC reads it.

### Decision 4: `Concert` proto stays as the user-facing DTO; embed `Series` and `repeated Artist performers`

- **Choice**: `Concert` keeps its position as the RPC-facing message. Fields that moved to `Series` (`title`, `source_url`) are removed from `Concert`. `artist_id` is replaced by `repeated Artist performers`. A `Series series` field is embedded (not just `SeriesId`).
- **Alternatives considered**:
  - Strip `Concert` down to `{ EventId id }` only — rejected: `Event` proto is unused in current RPC, so `Concert` is the only practical surface for downstream consumers; emptying it breaks the entire ConcertService surface.
  - Reference `SeriesId series_id` only and let the client fetch `Series` separately — rejected: forces N+1 fetches for typical "list concerts" responses where each row needs `series.title` for display.
  - Add `repeated Performer` with `billing` (headline/support) — rejected: no current product requirement for billing differentiation. Extending `Artist` later is non-breaking.

### Decision 5: M:N performers via `event_performers` (no role/billing column)

- **Choice**: `event_performers (event_id, artist_id)` composite PK only.
- **Rationale**: Smallest table that satisfies festival lineups and co-headliners. Adding `role TEXT` or `billing` later is a non-breaking column add. `Concert.performers` exposes the artists as an ordered repeated field; ordering semantics, if needed, can be added by introducing an `ordinal SMALLINT` column without breaking the table contract.

### Decision 6: Replace the `(artist_id, local_event_date)` natural key with `(series_id, local_event_date, venue_id)`

- **Choice**: New unique constraint: `UNIQUE(series_id, local_event_date, venue_id)`.
- **Rationale**: With M:N performers the old "one artist per day" key is structurally impossible to enforce on `events` (artist now lives on a junction table). The new key models "the same series cannot have two events at the same venue on the same date" which is the realistic dedupe surface for both manual entry and Gemini-driven discovery.
- **Known limitation**: Same series, same venue, same date, with morning/evening showings (昼夜2部) violates this key. No instances exist today; if they appear, the fix is to add `start_at` to the key (with a partial-key strategy because `start_at` is nullable in many records). Tracked as a follow-up, not blocking this change.

### Decision 7: `series` has no derived/cached fields (`start_date`, `end_date`) or future-use fields (`ticket_purchase_url`)

- **Choice**: `series` ships with only `id`, `title`, `type`, `source_url`.
- **Rationale**: YAGNI. Period summaries are computable on demand via `MIN/MAX(events.local_event_date) WHERE series_id = ?` and the query cost is trivial relative to maintaining cache invalidation. Ticket-purchase URL was earmarked for "Phase 3" with no concrete consumer; deferring it keeps the schema small and avoids prematurely committing to a single-URL model (consumers may eventually need multiple URLs per region/sale phase).

### Decision 8: Migrate by truncation, not by backfill

- **Choice**: `TRUNCATE events CASCADE`, then apply the DDL.
- **Rationale**: Production is not released; dev/staging data is disposable. A 1-row-to-1-row backfill would only add code and migration time for no business value. The cascade also clears `tickets`, `ticket_journeys`, `ticket_emails`, `merkle_tree`, `nullifiers` — all of which reference orphan dev-only test data.

### Decision 9: Modify the `event-management` capability rather than creating a new one

- **Choice**: All requirement updates land in `openspec/specs/event-management/spec.md` as MODIFIED requirements.
- **Rationale**: The existing capability already owns the "generic Event" + "Concert as Event subtype" framing. Series is the natural parent in that framing; promoting it to its own capability would split a single coherent domain concept across two specs.

## Risks / Trade-offs

- **Risk**: Embedding the full `Series` message in every `Concert` inflates RPC payloads when listing many concerts (e.g., dashboard). → Mitigation: typical list responses are paginated to ~50 items; `Series` carries only 4 small fields. If payload size becomes a measured problem, switch to `SeriesId` reference with a sibling map response — non-breaking on the wire if done before clients depend on the embed.
- **Risk**: 1-`Event`-per-`Series` fallback during auto-discovery scatters real tours across many single-row series. → Mitigation: explicitly deferred to a follow-up change (`auto-discovery-series-grouping`). The data model is ready; the discovery prompt change is independent.
- **Risk**: Removing `events.title` removes a free-text searchable field. → Mitigation: the equivalent text moves to `series.title`; any existing search by title needs to JOIN `series`. Documented in spec.
- **Risk**: `concerts` table now has only `event_id` (a placeholder). Future maintainers may delete it as "useless." → Mitigation: keep the existing `event-management` "Event-Type Extensibility" requirement in spec to document why the table is retained.
- **Trade-off**: New `event_performers` table doubles writes for the common case (1 artist per event). Acceptable: writes are dwarfed by reads, and the table eliminates schema duplication.
- **Trade-off**: `series_type` is a PG ENUM, which makes adding values DDL-only (no `ALTER` migration is needed in PG ≥ 12 for `ADD VALUE`, but removals/renames are awkward). Acceptable: enum churn is rare for this concept.

## Migration Plan

This is a single Atlas migration. Production is empty so no data backfill is required.

1. `TRUNCATE events CASCADE` (clears `events`, `tickets`, `ticket_journeys`, `ticket_emails`, `merkle_tree`, `nullifiers`).
2. `CREATE TYPE series_type AS ENUM ('TOUR', 'SINGLE', 'FESTIVAL')`.
3. `CREATE TABLE series (...)` per the schema.
4. `CREATE TABLE event_performers (...)` per the schema.
5. `ALTER TABLE events` — drop `artist_id`, `title`, `source_url`, the old `uq_events_natural_key`; add `series_id UUID NOT NULL REFERENCES series(id)`, the new `uq_events_natural_key`; add `idx_events_series_id`.
6. `ALTER TABLE concerts DROP COLUMN artist_id`; drop the old `idx_concerts_artist_id`.
7. Atlas registers the migration file in `k8s/atlas/base/kustomization.yaml`.

**Rollback strategy**: The migration is destructive (truncates data). Rollback is `DOWN` migration that recreates the old columns and the old natural key, but the truncated data cannot be recovered. Since production has no data, this is acceptable; the practical rollback path is "fix forward."

## Open Questions

- The auto-discovery follow-up (`auto-discovery-series-grouping`) needs a Gemini prompt spike to confirm whether the model returns consistent tour titles for the same tour across separate stop pages. The data model in this change supports both grouped and 1:1 fallbacks, so the spike does not block this change.
- The `Concert` DTO's embedded `Series` decision should be re-validated once concrete dashboard/list payload sizes are measurable.
