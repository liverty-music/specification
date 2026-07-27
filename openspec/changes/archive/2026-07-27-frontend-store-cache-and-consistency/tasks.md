## 1. Spike: confirm the problem

- [x] 1.1 Measure current route-entry latency per data-bearing page (Dashboard, Discovery, Tickets): does painting block on RPC, and by how long? Record which pages actually benefit from SWR before wiring anything.
- [x] 1.2 Confirm the audited resource tiers still hold against current code (TIER1 cache set, TIER3 network-first, dropped per-artist reads); adjust scope if drifted.

## 2. Shared revalidating-cache primitive

- [x] 2.1 Add the `RevalidatingCache<T>` utility (e.g. `src/services/cache/`): `get(key, fetcher, { staleTime })`, `invalidate(key)`, in-flight coalescing, timestamp/staleness bookkeeping. No component-facing API — used only inside stores.
- [x] 2.2 Unit tests: fresh-hit (no fetch), stale (serve + background revalidate), miss (fetch + store), in-flight coalescing (one RPC for concurrent callers), invalidate (next read refetches), complete-key behavior.

## 3. Generalize the concert cache onto the primitive

- [x] 3.1 Refactor `concert-store.ts` so `listByFollower` caching comes from the primitive (behavior-preserving: 24h `staleTime`, existing `invalidateFollowerCache()` semantics on follow/unfollow).
- [x] 3.2 Add background revalidation on Dashboard route entry (paint cache first) and route follow/unfollow **and `setHype`** invalidation of `listByFollower` through the primitive (invalidate only after the RPC succeeds).

## 4. Extend caching to the audited read resources

- [x] 4.1 Cache `Concert.listWithProximity` (the guest concert path, re-fetched on Dashboard/Welcome re-entry) via the primitive, keyed by `sorted(artistIds) + countryCode + level1`; add a small LRU cap only if the guest artist-set varies enough to grow the key space. No write-side invalidation needed (the key changes with the follow set).
- [x] 4.2 Cache `Artist.listTop` via the primitive, keyed by `country + tag + limit` (limit MUST be in the key). Verify Discovery re-entry reuses the cached pool without a refetch.
- [x] 4.3 Cache `Ticket.listTickets` via the primitive (long `staleTime`); invalidate it on a new ticket mint.
- [x] 4.4 Confirm `Concert.listConcerts` and `Artist.listSimilar` remain uncached pass-throughs; confirm `User.get` keeps its own idempotent recovery (NOT migrated onto the primitive); confirm TIER3 (`Entry.getMerklePath`, `Push.*`, `Artist.search`) stays network-first.

## 5. Ticket-journey single source of truth

- [x] 5.1 Add `TicketJourneyStore` singleton owning `@observable journeyMap: Map<eventId, JourneyStatus>`; `listByUser` populates it (network-first, no stale window); `setStatus`/`delete` are write-through (RPC then map update; no map update on failure).
- [x] 5.2 Migrate `dashboard-route.ts` to read journey status from the store instead of a local `journeyMap` copy.
- [x] 5.3 Migrate `event-detail-sheet.ts` to write via the store (remove the local `event.journeyStatus` mutation as the source of truth).
- [x] 5.4 Clear `journeyMap` on sign-out (wire to the existing auth-boundary event).

## 6. App-level resume revalidation

- [x] 6.1 Add a single `visibilitychange`/resume hook that triggers background revalidation of the cached resources owned by the **currently active route's stores** (not all mounted stores; no `reconnect` trigger this iteration). Ensure it does not double-fire with route-entry revalidation.

## 7. Tests

- [x] 7.1 Journey write-through consistency test: a status change in the detail sheet reflects on the Dashboard without a re-fetch or route re-entry.
- [x] 7.2 Revalidation-on-resume test: a stale cached resource is revalidated on PWA foreground; the swap is in place (no reload / scroll reset).
- [x] 7.3 Sign-out clears the journey store.

## 8. Verify locally

- [x] 8.1 Run `make check` (Biome + stylelint + typecheck + unit tests) and confirm green.
- [x] 8.2 Manually verify fast tab re-entry (cache paints immediately) and that Dashboard/Tickets/Discovery show fresh data after PWA resume.

## 9. Ship to production

- [x] 9.1 Open the frontend PR, get CI green, and merge.
- [x] 9.2 Cut a frontend GitHub Release (SemVer tag) → automated pin-bump → ArgoCD auto-sync to prod; confirm pods roll to the new tag.
- [x] 9.3 Verify in prod: tab re-entry is fast, journey status is consistent across Dashboard and detail sheet, and data refreshes on PWA resume.
- [x] 9.4 Archive the OpenSpec change once verified in prod.
