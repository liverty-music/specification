## Why

Tab-to-tab navigation re-issues RPCs and paints only after they resolve, so revisiting a page (Dashboard, Discovery, Tickets) feels slow even when the underlying data barely changed. Today only `ConcertServiceClient.listByFollower()` has an in-memory cache (a bespoke 24h TTL); every other read re-fetches on each route entry, there is no revalidation when the installed PWA is resumed from the background (so a long-lived tab can show stale data), and there is no shared caching mechanism — the one cache is hand-rolled and cannot be reused. Separately, ticket-journey status is held as **separate copies** in the Dashboard and the detail sheet, so setting a status in the sheet does not update the Dashboard until the route is re-entered.

The fix is a single, standard **stale-while-revalidate (SWR)** discipline expressed through the existing Aurelia singleton stores: serve cached state instantly for fast navigation, revalidate in the background (on route entry and on PWA resume) so it never goes stale, and make each cacheable resource a **single source of truth** owned by one observable store — which also removes the journey inconsistency.

## What Changes

- Introduce a shared, in-app **revalidating-cache primitive** (stale-while-revalidate) that singleton stores compose internally. It owns one copy of each resource, tracks per-resource `staleTime`, coalesces in-flight requests, exposes explicit invalidation, and revalidates on **route entry** and on **`visibilitychange`/resume (PWA foreground)**. It is an internal store collaborator — components keep reading only the store's observable state (no second state layer, no double management).
- Generalize the existing bespoke 24h concert cache to use the shared primitive, and add PWA-resume/route-entry revalidation so the Dashboard concert list refreshes when the installed app is reopened.
- Extend caching to a small, verified set of read resources whose value comes from **cross-route re-entry** (not intra-session repeats): `Concert.listWithProximity` (the guest concert path, re-fetched on Dashboard/Welcome re-entry — note the authenticated Dashboard uses `listByFollower` and filters client-side, so this is a guest-path win, not a filter-toggle one), `Artist.listTop` (Discovery re-entry — cache key MUST include `country + tag + limit`), and `Ticket.listTickets` (near-immutable). `User.get` is **unchanged and out of scope**: it keeps its existing idempotent get-or-create recovery (in-memory + localStorage) and is not migrated onto the shared primitive.
- Make ticket-journey status a **single source of truth**: a singleton store owns an observable journey map; `SetStatus`/`Delete` are write-through (update the store, not a local copy); Dashboard and detail sheet both read the store, so a status change reflects everywhere without a re-fetch. The store clears its journey state on sign-out.
- **Explicitly NOT changed / out of scope**: per-artist one-shot reads `Concert.listConcerts` and `Artist.listSimilar` stay uncached (each artistId is requested at most once per session — an audit found ~zero cache hits); network-first resources stay network-first (`TicketJourney.listByUser` freshness, `Entry.getMerklePath`, `Push.*`, `Artist.search`); client-owned localStorage state (onboarding, consent, PWA-install, help flags, guest follows/home) is not server-cache and is untouched; Service-Worker/HTTP-layer caching of RPC responses is out (Connect-RPC uses POST — not cacheable by the Cache API — and would create a second copy); and caching the Discovery bubble component instance is dropped (fights the Aurelia router lifecycle).

## Capabilities

### New Capabilities
- `frontend-store-cache`: A shared stale-while-revalidate primitive that Aurelia singleton stores use to cache read-only RPC resources — per-resource `staleTime`, in-flight coalescing, explicit invalidation, and revalidation on route entry and PWA resume — while keeping the store the single source of truth (no parallel state).

### Modified Capabilities
- `dashboard-concert-cache`: The `listByFollower` cache is re-expressed via the shared primitive and gains revalidation on route entry and PWA resume (previously it only had a passive 24h TTL with no refresh trigger).
- `entity-store-layer`: Add a journey single-source-of-truth requirement (a store owns the observable journey status; writes are write-through; readers share it; cleared on sign-out) and clarify that cache-only stores obtain caching via the shared `frontend-store-cache` primitive rather than bespoke per-store logic.

## Impact

- Frontend only. No proto/BSR, backend, or API changes; no new runtime dependency (the primitive is a small in-repo utility).
- Affected code: a new revalidating-cache utility (e.g. `src/services/cache/`); `concert-store.ts` (generalize existing TTL + add revalidation triggers); the artist/top and proximity read paths; a new journey store plus its consumers (`dashboard-route.ts`, `event-detail-sheet.ts`); route-entry and `visibilitychange` wiring.
- Risk: incorrect cache keys serving wrong data (mitigated by keying `listTop` on `country+tag+limit`); stale-flash on revalidation (mitigated by non-destructive in-place swap preserving scroll); memory growth (bounded — remaining caches are few-key; a small LRU only if `listWithProximity` filter combos grow).
- Testing: unit tests for the primitive (staleTime, in-flight coalescing, invalidation), a journey write-through consistency test (sheet write reflects on dashboard without re-entry), and a revalidation-on-resume test.
- Recommended first task: a quick spike measuring current route-entry latency to confirm which pages actually block on RPC before wiring SWR.
