## Context

The dashboard route (`dashboard-route.ts`) currently loads all concerts for followed artists and renders them unconditionally via `<concert-highway>`. There is no mechanism to scope the view to a subset of artists.

Push notifications are delivered through the Service Worker (`sw.ts`), which reads `notification.data.url` and navigates to it directly — no frontend integration is needed to support deep-link URLs. The existing `IHistory` adapter (used by `EventDetailSheet`) provides a clean pattern for URL state synchronisation without triggering Aurelia router transitions.

The `DateGroup` entity (`entities/concert.ts`) contains `Concert[]` per lane, and each `Concert` carries an `artistId: string`. Client-side filtering over this structure is straightforward and avoids any backend changes for the frontend scope.

## Goals / Non-Goals

**Goals:**
- Parse `?artists=id1,id2` from the dashboard URL on load and apply as an in-memory filter
- Expose a filter chip UI in the page header that reflects active filters and allows individual dismissal
- Provide an artist-selection bottom sheet for users to actively choose which artists to filter by
- Keep filter state in the URL (via `replaceState`) so it survives reload and is shareable
- Support navigation from push notifications with a pre-set artist filter

**Non-Goals:**
- Backend changes to the concert fetch API (filtering remains client-side)
- Persisting filter state in `localStorage` (URL is the single source of truth)
- Multi-artist selection via the notification payload (notifications target one artist at a time)
- Changes to the onboarding flow or lane intro behaviour

## Decisions

### Decision 1: Client-side filtering over `filteredDateGroups` computed getter

**Chosen:** Filter `dateGroups` in the ViewModel via a computed getter `filteredDateGroups`. When `filteredArtistIds` is empty, return `dateGroups` unchanged. When non-empty, map each group keeping only concerts whose `artistId` is in the set, then drop groups where all three lanes are empty.

**Alternatives considered:**
- *Pass artist IDs to the backend API* — Would require a protobuf schema change, backend work, and a spec-driven release cycle. The frontend already fetches all followed-artist concerts; filtering a few dozen items client-side is negligible.
- *Filter inside `ConcertService.toDateGroups()`* — Would bleed UI concern into a shared service. The dashboard is the only consumer that needs filtered groups.

### Decision 2: URL encoding — comma-separated `?artists=id1,id2`

**Chosen:** Single `artists` key with comma-separated UUIDs.

**Rationale:** UUIDs contain no commas so splitting on `,` is unambiguous. The URL stays short (important for notification payloads). Reading is one call: `next.queryParams.get('artists')?.split(',') ?? []`.

**Alternative:** `?artists=id1&artists=id2` (repeated key, `URLSearchParams.getAll()`). More idiomatic for multi-value params but produces longer URLs. Not worth the extra length for this use case.

### Decision 3: URL sync via `IHistory.replaceState`, not Aurelia router navigation

**Chosen:** Mutate the URL silently with `IHistory.replaceState(null, '', '/dashboard?artists=...')` when the user changes filters.

**Rationale:** Mirrors the pattern already established by `EventDetailSheet`. A full Aurelia router navigation would re-run `loading()`, triggering a new API call and resetting all local state — unnecessary when only the filter changes. `replaceState` keeps the back-button stack clean (no extra history entry) and avoids reload.

### Decision 4: Filter UI — header-integrated chips + bottom sheet trigger

**Chosen:** When `filteredArtistIds` is non-empty, render dismissible artist-name chips in the page header (right side). A small trigger button (`≡`) is always present to open the artist-selection bottom sheet. The bottom sheet lists all followed artists with checkboxes.

**Rationale:**
- **No filter active:** header is unchanged — zero wasted space.
- **Filter active:** chips communicate state at a glance; individual `×` on each chip allows quick dismissal without opening the sheet.
- Re-uses the existing `bottom-sheet` primitive (already used by `UserHomeSelector` on the same route).

**Alternative A: Horizontal chip bar below the header** — always visible, wastes vertical space on mobile when no filter is active.

**Alternative B: Filter state only in the bottom sheet** — requires two taps to see the active filter; state is less discoverable.

### Decision 5: `artist-filter-bar` component with two bindables only

`artist-filter-bar` exposes:
- `@bindable followedArtists: Artist[]` — the list to render in the sheet
- `@bindable({ mode: 'two-way' }) selectedIds: string[]` — the active filter; parent mutates this directly via Aurelia two-way binding

No custom events. The parent (`DashboardRoute`) reacts to `selectedIdsChanged()` via Aurelia `@observable`-style change handler on the bound property, then calls `updateFilterUrl()`.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| `filteredDateGroups` re-runs on every render cycle if implemented as a plain getter | Use `@computed` or memoise behind `@observable filteredArtistIds` so it only recalculates when the filter or `dateGroups` changes |
| Stale URL when user navigates away and back (Aurelia re-runs `loading()`) | `loading()` always re-reads `next.queryParams`, so the URL remains the source of truth |
| Bottom sheet and `UserHomeSelector` sheet opening simultaneously during onboarding | Disable the filter trigger button while `isOnboarding` is true (filter is irrelevant during lane intro) |
| Very long artist name overflows header chip | Cap chip width with `max-width` + `text-overflow: ellipsis`; full name visible in the bottom sheet |

## Migration Plan

1. Deploy frontend change — feature is additive; URLs without `?artists` behave identically to today.
2. Backend team updates push notification payloads to include `/dashboard?artists=<artistId>` — can happen independently after frontend ships.
3. No rollback concern: removing `?artists` from any URL restores the unfiltered view.

## Open Questions

- Should the filter trigger button be visible during onboarding, or hidden entirely until onboarding is complete? (Current proposal: hidden/disabled during onboarding to avoid distraction.)
