## Context

The guest onboarding UX has three observable regressions after onboarding completes:

1. **Header clutter**: `artist-filter-bar` renders artist name chips in the page header when a filter is active. The header has limited horizontal space, and chip text duplicates information already visible in the concert highway.

2. **Silent laser beam failure**: `FollowServiceClient.listFollowed()` for unauthenticated users hardcodes `hype: 'watch'` for every artist. `isHypeMatched('watch', lane)` always returns `false` (HYPE_ORDER=0 < all LANE_ORDERs ≥1), so `ConcertHighway.buildBeamIndexMap()` produces an empty map and no beams render — even though the guest may have set hype levels in My Artists.

   Root cause: `GuestFollow` entity lacks a `hype` field. Hype is stored separately in `GuestService.hypes: Record<string, string>` (key `liverty:guest:hypes`), but `listFollowed()` never reads it.

3. **Banner copy mismatch**: Japanese banner text is two sentences and wraps to 3 lines on mobile. English text (`"🔔 To enable notifications"`) is far shorter and communicates less value.

Current entity shape:
```
GuestFollow   { artist: Artist, home: string | null }  ← home always null
FollowedArtist { artist: Artist, hype: Hype }
```
The two types are structurally incompatible despite representing the same concept (a user's relationship with an artist). `GuestFollow.home` is set to `null` everywhere and is never read — the guest's home area is stored separately in `GuestService.home`.

## Goals / Non-Goals

**Goals:**
- Remove artist name chips from filter bar header; preserve filter icon active state
- Unify guest and authenticated follow representation under `FollowedArtist`
- Make guest laser beams render correctly by reading persisted hype values
- Shorten Japanese signup banner copy to ≤2 lines; align English copy in meaning

**Non-Goals:**
- Changing hype persistence storage key (`liverty:guest:hypes` key eliminated, follows now unified under `guest.followedArtists`)
- Changing backend RPC contracts or proto schema
- Adding new onboarding steps or flow changes
- Fixing beam rendering for authenticated users (already works correctly)

## Decisions

### Decision 1: Eliminate `GuestFollow`, unify on `FollowedArtist`

**Chosen**: Remove `GuestFollow`. `GuestService.follows` becomes `FollowedArtist[]`. Hype is stored inline in each follow entry. The separate `hypes: Record<string, string>` sidecar and `liverty:guest:hypes` storage key are eliminated.

**Alternatives considered**:
- *Keep `GuestFollow`, read `getHypes()` in `listFollowed()`*: Fixes the beam bug with minimal change, but leaves the structural lie (`GuestFollow` with dead `home` field) and the dual-storage awkwardness intact.
- *Add `hype` field to `GuestFollow`*: Halfway solution — two types still diverge with no benefit.

**Rationale**: `GuestFollow.home` has never been used (always `null`). The type exists solely as a historical artifact. Merging into `FollowedArtist` removes a conceptual mismatch, collapses dual storage into one key, and makes `listFollowed()` trivially correct.

### Decision 2: `DEFAULT_HYPE` constant in entity layer

**Chosen**: Define `export const DEFAULT_HYPE: Hype = 'watch'` in `entities/follow.ts`. All fallback assignments (`entry?.hype ?? 'watch'` in `concert-service.ts`, etc.) reference this constant.

**Rationale**: The default hype value is a business rule ("new follows start at watch-only"). It belongs in the entity layer, not scattered as string literals across service and adapter files.

### Decision 3: Remove chips from filter bar, retain icon active state

**Chosen**: Delete the `<ul class="chips-list">` block from `artist-filter-bar.html`. The filter trigger button already has `data-active.bind="selectedIds.length > 0"` which CSS uses to change its color. Users re-open the bottom sheet to change or clear the filter.

**Alternatives considered**:
- *Keep chips but move them below the header*: Adds complexity, consumes vertical space above the concert grid.
- *Replace chips with a count badge on the icon*: Valid, but adds a new UI element not currently designed.

**Rationale**: The filter icon's active state is sufficient affordance for a secondary feature. Removing chips simplifies the header significantly.

### Decision 4: localStorage migration for unified follow format

**Chosen**: `loadFollows()` migrates on read. If a stored entry lacks a `hype` field (legacy `GuestFollow` format), the validator accepts it and falls back to `DEFAULT_HYPE`. No separate migration script needed.

The separate `liverty:guest:hypes` key is no longer written. On data merge at signup, `GuestService.getHypes()` is replaced by reading hype from each `FollowedArtist` entry. The `clearHypes()` call in `clearAll()` is removed (key simply becomes orphaned and is ignored).

## Risks / Trade-offs

- **Legacy localStorage key `liverty:guest:hypes` becomes orphaned** → Acceptable. The key is not written after this change. Existing data in it is ignored. It does not affect correctness because hype is now read from the unified `guest.followedArtists` storage. A future cleanup task can remove it, but it causes no harm.

- **Data merge on signup no longer calls `SetHype` separately** → The `guest-data-merge` flow currently reads from `GuestService.getHypes()`. After this change, hype values are embedded in `FollowedArtist[]` entries. The merge code must be updated to iterate `guest.follows` and call `SetHype` for entries where `hype !== DEFAULT_HYPE`. This is a correctness requirement captured in tasks.

- **Filter dismiss UX change** → Users who relied on the `×` chip to dismiss individual filters lose that affordance. They must re-open the bottom sheet. This is a deliberate simplification; the bottom sheet already supports partial deselection.

## Migration Plan

1. Deploy frontend change only (no backend, no BSR release).
2. Existing users with `liverty:guest:hypes` data: hype values are now embedded in `guest.followedArtists`. If both keys exist simultaneously (user had old data), the new `loadFollows()` returns entries with `hype: DEFAULT_HYPE` (from missing field fallback). Their previously-set hype values in the orphaned key are effectively lost. This is acceptable given that: (a) the affected population is small (guest users mid-session during deploy), and (b) hype can be re-set in My Artists at no cost.
3. No server-side rollout coordination required.

## Open Questions

None — all decisions above are resolved based on codebase exploration.
