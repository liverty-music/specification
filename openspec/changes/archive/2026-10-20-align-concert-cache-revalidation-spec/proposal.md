## Why

The dashboard spec requires the cached `ConcertService.ListFollowed` result to be revalidated in the background on every Dashboard route entry, but the shipped frontend does not do this and should not: concert data changes only through the daily `concert-discovery` job (18:00 JST), the daily `sales-phase-discovery` job (21:00 JST) and organizer console publishing (in trial). A refetch on every tab switch costs an RPC per navigation for data that changes a few times a day. The spec, not the code, is wrong, and code comments repeat the wrong claim.

## What Changes

- The `ListFollowed` cache requirement drops the "revalidate on Dashboard route entry" obligation. Freshness comes from three triggers only: the 24-hour `staleTime`, the forced revalidation when the installed PWA returns to the foreground, and invalidation on a successful follow, unfollow or hype change (unchanged).
- The requirement text no longer contradicts itself ("served without issuing an RPC" within `staleTime` vs "revalidate on route entry").
- The scenario "Cache hit on Dashboard re-entry" states that re-entry within 24 hours issues no RPC, instead of requiring a background revalidation.
- Frontend: no behavior change. Code comments that claim route-entry revalidation (`concert-store.ts`, `artist-store.ts`, `cache/revalidating-cache.ts`, `cache/cached-resource.ts`, `resume-revalidator.ts`) are corrected, and the dashboard re-entry test is named for what it checks.
- No manual reload control is added to the PWA. Pull-to-refresh stays disabled; a fan who hits a broken state restarts the app, which clears the in-memory cache.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/dashboard`: requirement "ListFollowed results are cached in memory for the session" no longer revalidates on Dashboard route entry; the re-entry scenario changes accordingly.

## Impact

- Frontend (`liverty-music/frontend`): comments and one test name only. No runtime change, no RPC count change (the current code already behaves as the new spec says).
- Backend, proto, cloud-provisioning: none.
- Discovery: the `listTop` cache follows the same policy in code; the discovery spec does not claim route-entry revalidation, so it is not modified. Only the `artist-store.ts` comment changes.
