## Context

See proposal.md — Why. Current state, verified in code:

- `ListByFollowerRequest` is an empty message; `listConcertsByFollowerQuery` has no date predicate, so past concerts are returned and rendered at the top of the chronological highway.
- `ListByLocation` already models a date window with `from`/`to` of `entity.v1.LocalDate` (wrapping `google.type.Date`), and the frontend already sends client-supplied `CalendarDate`s for the "All Nearby" mode. This is the precedent to follow.
- The dashboard filter bottom sheet already hosts artist and journey facets that narrow the **already-loaded** set purely client-side, with URL sync via `history.replaceState` (`artists`, `journey` params).
- `ConcertStore.listByFollower` caches under a single key with 24h stale-while-revalidate.

## Goals / Non-Goals

**Goals:**
- Default the timetable to today-onward with a client-anchored "today".
- Let the user widen the range into the past from a chosen date via a collapsible date facet, with URL persistence.
- Reuse existing proto/UI conventions (LocalDate VO, bottom-sheet facet, URL sync).

**Non-Goals:**
- No `to`/upper-bound for the timetable — the date facet is open-ended (`>= from`); only a lower bound is added.
- No change to "All Nearby" mode (already has its own from/to range).
- No change to the artist/journey facets' semantics beyond the fact that their chip counts now compute over a possibly past-inclusive loaded set.
- No DB migration (query predicate only).

## Decisions

### D1: Add `from` to `ListByFollowerRequest` rather than a new RPC
Add `entity.v1.LocalDate from = 1;` (optional). Mirrors `ListByLocationRequest.from` and the "Proto Value Object Consistency" requirement. Additive field = wire-compatible; the behavioral default (future-only) is the only breaking aspect and it is the desired behavior.
- *Alternative rejected*: a separate `ListPastByFollower` RPC — duplicates grouping/proximity logic and the caching path for no benefit.

### D2: Client owns "today"; backend defaults to `CURRENT_DATE` when `from` is unset
The frontend always sends `from = client local today` for the default view. Backend query becomes `AND e.local_event_date >= COALESCE($2, CURRENT_DATE)`. This keeps the date boundary correct across timezones (server is UTC; a user just after local midnight would otherwise see yesterday's shows drop or persist a day early). The `COALESCE` default protects any non-dashboard caller that omits `from`.
- *Alternative rejected*: backend always uses `CURRENT_DATE` and ignores client date — simpler but reintroduces the UTC boundary skew the client-anchored approach avoids.

### D3: Date facet triggers an RPC round-trip, not a client-side narrow
Unlike artist/journey facets, changing `from` changes what the server returns, so it re-fetches `ListByFollower(from)`. The store cache key MUST incorporate `from` so switching between today-onward and a past date does not serve a stale set. Expanding into the past is the only case that fetches more data; the common default path is unchanged in cost.
- *Consequence*: the artist/journey chip counts (spec'd as "over the loaded set") naturally recompute over the past-inclusive set once past concerts are loaded — this is acceptable and documented in the `dashboard-date-filter` spec.

### D4: URL param + collapsible facet UI
Add a single date query param (e.g. `from=YYYY-MM-DD`) synced via `replaceState`, matching `artists`/`journey`. In the sheet, the date facet is collapsed behind "過去のコンサートも表示" and expands to one date field ("この日付以降を表示"), committed by the shared confirm button. Clearing it back to today removes the param.

## Risks / Trade-offs

- **[Behavioral break for any consumer expecting past concerts from `ListByFollower`]** → The only current consumer is the dashboard, which is updated in the same coordinated release. The `COALESCE` default is explicit and documented; `from` remains optional on the wire.
- **[Unbounded payload when a very old `from` is chosen]** → Acceptable: past widening is user-initiated and rare; the default path stays future-only and bounded. If it becomes a problem later, add pagination or a floor date — out of scope here.
- **[Cache key regression]** → If `from` is omitted from the cache key, users would see a stale today-onward set after choosing a past date (or vice versa). Explicit task + test to key the cache on `from`.
- **[Timezone correctness depends on client sending the right local date]** → Reuse the same client date source already used by "All Nearby" (frontend-plain-date-lib) to avoid a second date-source discrepancy.

## Migration Plan

Standard cross-repo proto coordination (see global protocol):
1. specification: add `from` to `ListByFollowerRequest`, open PR (CI/lint/breaking).
2. In parallel, prepare backend (query predicate + handler/use-case threading) and frontend (store/client `from` arg, cache key, date facet, URL sync) against the planned shape with TODO markers for generated types.
3. Merge spec PR → publish Release tag → monitor `buf-release.yml` BSR gen.
4. Upgrade generated packages (backend `go get`, frontend `npm install`), swap TODO placeholders for generated types, run `make check`.
5. Open backend/frontend PRs once green locally; ship to prod.

Rollback: revert the backend query predicate (returns to all-concerts) and/or frontend to not send `from`; the additive proto field can remain unused. No data migration to reverse.
