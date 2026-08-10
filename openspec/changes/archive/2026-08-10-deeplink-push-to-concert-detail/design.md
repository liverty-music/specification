## Context

A new-concert push notification is produced by `NotifyNewConcerts` in the backend for one artist and a batch of newly created concerts. Followers carry a hype level (`watch` / `home` / `nearby` / `away`≡`anywhere`) that gates delivery. Today the per-follower gate is a boolean (`f.Hype.ShouldNotify(home, venueAreas, concerts)`), the body count is `len(concerts)` over the whole batch, and the payload `data.url` is a hardcoded `"/dashboard"`.

On the frontend, `concerts/:id` already routes to `DashboardRoute`, and the detail sheet already owns the `/concerts/:id` URL: `open()` does `history.pushState(..., '/concerts/:id')` and `close()` does `history.replaceState(..., '/dashboard')`. `DashboardRoute.loading()` currently ignores the `:id` route param and only reads `?artists=` / `?journey=` query params. The dashboard's `listByFollower` result groups concerts into `home` / `nearby` / `away` lanes, and the `away` lane captures far / unknown-location concerts — so any followed-artist concert is present in the list regardless of geography.

This change wires the notification to the concert that actually triggered each recipient's hype match, and makes the deep-link land on that concert's detail sheet.

## Goals / Non-Goals

**Goals:**
- Tapping a new-concert notification opens the earliest hype-matched concert's detail sheet, dashboard filtered to that artist.
- The deep-link target and the body count are computed from the per-recipient hype-matched subset (case A), fixing the pre-existing `home`-hype over-count.
- Reuse existing surfaces: the `/concerts/:id` URL, the `listByFollower` fetch, the detail sheet's open/close. No new URL form, no new RPC.

**Non-Goals:**
- No new `GetConcert(id)` single-resource RPC (the `away` lane guarantees list presence; hype-match range ⊆ dashboard range).
- No change to the detail sheet component's own open/close/URL behavior.
- No `nearby` productization beyond its current phase-1 semantics.
- No proto/schema change (the payload already carries `data.url`; count is a formatting concern).

## Decisions

### Decision 1: Deep-link URL is `/concerts/<concertId>`, artist filter derived (not `?artists=`)

Reuse the URL the detail sheet already writes, so a push-tap and a manual card-tap converge on identical URL + state. The artist is redundant with the concert, so it is derived on open (`filteredArtistIds = [concert.artistId]`) rather than duplicated in a query param.

- **Alternative — `/dashboard?artists=<id>&concert=<id>`**: introduces a second representation of "concert open" (the sheet still writes `/concerts/:id`), forcing either two URL forms or a larger refactor of the sheet. Rejected for maintainability.
- **Alternative — keep the shipped `/dashboard?artists=<id>`**: only filters; never opens the concert. Fails the intended experience.

Rationale over "REST purity": the decisive factor is that `/concerts/:id` already exists end-to-end. This is a consistency/least-surface choice, not a claim that path-over-query is universally correct for overlays.

### Decision 2: Case A — per-recipient hype-matched subset drives both count and deep-link

Refactor the per-follower boolean `ShouldNotify(...) bool` into a subset selector (e.g. `MatchingConcerts(home, concerts) []Concert`). The delivery gate becomes `len(subset) > 0`; the body count becomes `len(subset)`; the deep-link concert is the earliest of `subset` (local date asc, tie-break start time asc).

- **Alternative — case B (global earliest)**: keep the boolean gate and deep-link everyone to the batch's globally earliest concert. Simpler backend, but a `home`-hype recipient could be deep-linked to an out-of-area concert that never matched their hype — reintroducing the "notification says X, tapping shows Y" mismatch this change exists to remove. Rejected.

Case A also fixes the pre-existing over-count for free (the `home`-hype user's count reflects only their in-area matches).

### Decision 3: Frontend resolves the pending open against the authoritative fetch, not the cache paint

`loading()` records `pendingConcertId` from the `:id` param. `loadData()` already fetches `listByFollower` (fast-path paints from cache first, then background-refreshes; cold boot awaits the full fetch). The auto-open resolves the concert **when the authoritative fetch promise settles**, then calls `detailSheet.open(concert)` and derives the filter. No optimistic cache-open, no timer, no reconciliation pass.

- **Alternative — open from cache paint then reconcile**: adds machinery for a warm-focus edge case; the cold-boot case (the common notification-tap path) has no cache anyway. Rejected as unnecessary complexity.

### Decision 4: Absent-concert path degrades to filter-only

If the resolved list has no matching concert (unfollow-after-send, zero-date, or unresolved-performer anomaly), apply the artist filter if still derivable and leave the sheet closed — no error surfaced. Because geography never drops a concert (away lane) and the notification implies a followed artist, this path is rare.

## Risks / Trade-offs

- **Behavioral change to `home`-hype counts** → intended and spec'd; call it out in the release notes since the visible count shrinks for those users.
- **Warm-focus timing (existing window focused, stale cache)** → mitigated by resolving the open on the authoritative fetch promise rather than the cache paint; the concert appears once the refresh lands.
- **Concert genuinely missing (rare edge)** → mitigated by the filter-only graceful degrade; no error, dashboard still narrows to the artist.
- **Two URL writers on the dashboard (sheet open/close vs the `syncFilterUrl` `@watch`)** → the deep-link path sets `filteredArtistIds` which would trigger `syncFilterUrl`; sequence the sheet `pushState('/concerts/:id')` so it wins while the sheet is open, and let the filter URL apply after close. Verify no double-write drops a state during apply.

## Migration Plan

1. specification: land the delta specs (no proto change expected). If review concludes a proto/schema touch is needed, follow the cross-repo BSR release flow; otherwise skip BSR.
2. backend: refactor hype to subset selection + earliest-concert deep-link + subset-aligned count; unit-test the `home`/`away` subset and earliest tie-break; `make check`.
3. frontend: wire `loading()` `:id` → pending open resolved on the authoritative fetch + derived filter + graceful degrade; unit/e2e for open, filter-derive, close-no-reload, and absent-concert; `make check`.
4. Release backend, then frontend; bump prod pins; verify a real notification tap in prod opens the correct concert's sheet filtered to its artist.
5. Rollback: revert the backend `data.url`/count change and the frontend `loading()` wiring independently; the deep-link URL reverting to `/dashboard` is the prior (buggy but safe) behavior.

## Open Questions

- Does the current hype entity expose a clean seam to return the matched subset, or does `MatchingConcerts` need a small new method alongside `ShouldNotify` (kept for any other caller)? Confirm during backend implementation.
- Confirm no other caller depends on the body count meaning "all new concerts" before narrowing it to the subset.
