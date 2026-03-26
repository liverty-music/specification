## Context

The frontend PWA uses Workbox in `src/sw.ts` to manage caching strategies. PR #92 added two API caching routes:

1. **Concert API** (`NetworkFirst`, no method filter) - intended for offline read access to concert lists
2. **Artist API** (`NetworkFirst` + `BackgroundSyncPlugin`, `'POST'` filter) - intended for offline queuing of follow/unfollow operations

Both routes target Connect-RPC endpoints which exclusively use POST. The Cache API only supports GET, creating a fundamental incompatibility.

## Goals / Non-Goals

**Goals:**
- Eliminate the `TypeError: Failed to execute 'put' on 'Cache'` error on Artist API calls
- Remove dead code that never functioned (Concert API route, periodicSync, REFRESH_CONCERT_CACHE handler)
- Preserve BackgroundSync functionality for Artist API offline queuing

**Non-Goals:**
- Implementing Concert API offline caching (requires `useHttpGet` transport change - separate change)
- Changing Connect-RPC transport configuration
- Modifying backend or proto definitions

## Decisions

### 1. Artist API: NetworkOnly instead of NetworkFirst

**Decision**: Replace `NetworkFirst` with `NetworkOnly` on the Artist API route.

**Rationale**: The Artist API route's purpose is BackgroundSync (queue failed mutations for replay), not response caching. `NetworkOnly` passes requests directly to the network without attempting cache operations. `BackgroundSyncPlugin` works with any strategy — it hooks into `fetchDidFail`, not `cacheDidUpdate`.

**Alternative considered**: Custom plugin with `handlerDidRespond` to store in IndexedDB instead of Cache API. Rejected because the route's purpose is write operations (follow/unfollow), not read caching.

### 2. Concert API: Remove entirely rather than fix

**Decision**: Delete the Concert API route, `CONCERT_CACHE` constant, periodicSync handler (`sw.ts`), periodicSync registration and REFRESH_CONCERT_CACHE handler (`main.ts`).

**Rationale**: This code has never functioned since it was merged. The route lacked `'POST'` in its method filter, so no requests ever matched and the cache was always empty. The periodicSync handler (including the dd9f231 fix) iterated over an empty cache. Fixing it by adding `'POST'` would just reproduce the same `cache.put` error that the Artist API route has. Properly solving Concert API offline caching requires `useHttpGet` transport changes — a cross-repo effort that belongs in a separate change.

## Risks / Trade-offs

- **[Loss of intent]** Removing Concert API caching code loses the expressed intent from PR #92. Mitigated by documenting the future `useHttpGet` path in the proposal and creating a follow-up issue.
- **[BackgroundSync behavior unchanged]** `NetworkOnly` still triggers `BackgroundSyncPlugin` on network failure — verified by Workbox source: the plugin's `fetchDidFail` callback fires regardless of strategy.
