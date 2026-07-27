## Context

The frontend is an Aurelia 2 PWA whose client state is owned by DI singleton stores (per the `entity-store-layer` capability: each store owns its entity's observable state and MAY cache read-only resources). Today only `ConcertServiceClient.listByFollower()` is cached — a bespoke in-store 24h TTL with in-flight coalescing and manual `invalidateFollowerCache()` (see `dashboard-concert-cache`). Every other read re-fetches on each route entry, and nothing revalidates when the installed PWA is resumed from the background.

Two concrete problems motivated an audit of every frontend data resource:

1. **Slow tab re-entry / staleness.** Route entry awaits RPCs before painting; a long-lived PWA tab can show stale data with no refresh trigger (the only `visibilitychange` listener today pauses the Discovery canvas animation, not data).
2. **Journey inconsistency.** `ITicketJourneyService` is a stateless RPC pass-through. The Dashboard fetches a `journeyMap` once into non-observable local state; the detail sheet writes via `SetStatus` and mutates only its own `event` reference. The Dashboard does not reflect the change until the route is re-entered — the two hold **separate copies**.

The audit (recorded here so the change is self-contained) classified all resources into three tiers:

```
TIER 1 — cache (value comes from cross-route re-entry, not intra-session repeats)
   listByFollower (already), listWithProximity, listTop (key: country+tag+limit),
   listTickets, User.get (idempotent)
TIER 2 — client-owned localStorage state (NOT server cache): onboarding, consent,
   pwa-install, help-seen flags, guest follows/home  → untouched
TIER 3 — network-first, never cache: TicketJourney.listByUser (freshness),
   Entry.getMerklePath (single-use crypto), Push.*, Artist.search
DROPPED — listConcerts / listSimilar: per-artistId, each queried at most once per
   session (guards prevent re-tap; bubbles evicted) → ~zero cache hits, so uncached
```

## Goals / Non-Goals

**Goals:**
- Fast tab re-entry: paint cached state instantly, revalidate in the background.
- Never stale on resume: revalidate on route entry and on PWA foreground (`visibilitychange`/resume).
- One reusable mechanism: a shared stale-while-revalidate primitive that stores compose internally, replacing the one bespoke cache.
- Journey consistency: a single observable source of truth so a sheet write reflects on the Dashboard with no re-fetch.
- Single source of truth everywhere: exactly one copy of each resource, owned by its store; components read only the store.

**Non-Goals:**
- No Service-Worker/HTTP-layer caching of RPC responses (see Decisions — Connect-RPC is POST).
- No caching of the Discovery bubble component instance (fights the Aurelia router lifecycle; dropped earlier).
- No caching of TIER 2 client-owned state or TIER 3 network-first resources.
- No cold-start persistence (IndexedDB warm cache) — a possible future layer, out of scope.
- No `reconnect` (online/offline) revalidation trigger this iteration.
- No change to journey display mapping (`journey-status-presentation`) or backend `ticket-journey` semantics.

## Decisions

- **A shared in-app SWR primitive, composed inside stores (not a parallel state layer).** Introduce a small `RevalidatingCache<T>` (working name) utility. It holds one copy of a resource keyed by a cache key, records `staleTime` + timestamp, coalesces concurrent fetches (one in-flight promise per key), and exposes `get(key, fetcher, opts)`, `invalidate(key)`, and revalidation hooks. Stores use it **internally**; the store's `@observable` remains the sole public read surface. Components never import or read the cache.
  - *Why:* generalizes the proven `concert-store` pattern into one place; avoids duplicating TTL/dedup/invalidation across stores.
  - *Alternative — per-store ad-hoc caching:* rejected. The target state has 4–5 stores needing the same TTL + revalidation + invalidation; duplicating it invites divergence and invalidation bugs.
  - *Alternative — a query library (TanStack-style):* rejected for now. Adds a dependency and a second state model; the singleton-store pattern already exists and a thin utility fits it. Revisit only if the primitive grows beyond a small utility.
  - **No double management:** the data lives in exactly one place (inside the store, via the primitive). The primitive is bookkeeping + orchestration, not a second source components read from. This directly answers the "won't this duplicate store state?" concern.

- **`staleTime` is the single knob; it unifies speed and consistency.** A long `staleTime` yields SWR (serve cache, rarely refetch) → speed. `staleTime = 0` yields always-revalidate — and when paired with a write-through observable store, gives consistency. Same abstraction, different setting.
  ```
  staleTime = long  → SWR: listByFollower / listWithProximity / listTop / listTickets
  staleTime = 0     → single source of truth: TicketJourney (write-through, observable)
  ```

- **Revalidation triggers: route entry + PWA resume only.** On route entry the consuming store revalidates in the background (cache paints first). A single app-level `visibilitychange`/resume hook triggers revalidation of the active/foreground stores. No `reconnect` trigger this iteration.
  - *Why:* route entry is the core "fast tab" win; resume covers the one real staleness gap (installed PWA reopened after long background). Long `staleTime` is safe precisely because resume re-checks.

- **Cache keys must be complete.** `listTop` is keyed by `country + tag + limit` (the audit found `limit` varies — `MAX_BUBBLES` vs `MAX_BUBBLES/seedCount` — so a `country+tag`-only key would serve the wrong result size). `listWithProximity` is keyed by `sorted(artistIds) + countryCode + level1`. `listByFollower` stays user/region scoped.

- **Bounded memory.** Remaining caches are few-key (`listTop`: a handful of country/tag/limit tuples; `listByFollower`/`listTickets`: user-scoped). Only `listWithProximity` (keyed by the guest artist-id set) can grow if that set varies — apply a small LRU cap (~20–30) if observed; the dropped per-artist reads removed the main unbounded-key risk. (`User.get` is out of scope — it keeps its own single-entry idempotent recovery and is not on the primitive.)

- **Journey becomes a write-through observable store (single source of truth).** Add a `TicketJourneyStore` singleton owning `@observable journeyMap: Map<eventId, JourneyStatus>`. `setStatus`/`delete` call the RPC then mutate the map. Dashboard and detail sheet both read the store; the observable mutation triggers re-render. `listByUser` populates it on load (`staleTime = 0` — always fresh). The store clears `journeyMap` on sign-out.
  - *Why:* the inconsistency is caused by two copies; one observable owner removes it without any TTL cache or extra re-fetch.
  - *Alternative — return updated state from `setStatus` and re-assign `dateGroups`:* rejected — still two copies; brittle re-render trigger.

- **No Service-Worker caching for this data.** The real blocker is that Connect-RPC unary is a **POST** request, which the Cache API cannot key/cache; SW-caching would also store raw bytes, still requiring an in-app deserialized observable store — i.e. a second copy. (Today the SW only routes `ArtistService` and `FollowService` explicitly as `NetworkOnly` for BackgroundSync; `Concert`/`TicketJourney`/`User`/`Ticket` RPCs are simply not intercepted and go to network by default — either way nothing SW-caches RPC responses.) The SW remains responsible for what it is uniquely good at (static assets, ZK `.wasm`/`.zkey`, offline POST queueing) and is unchanged. (Artist image GETs, if any, are a separate SW-runtime-cache candidate — noted, not in this change.)

## Risks / Trade-offs

- **[Wrong cache key serves wrong data]** → key `listTop` on `country+tag+limit` and `listWithProximity` on `sorted(artistIds)+country+level1`; cover keying in unit tests.
- **[Stale-flash / layout jump on revalidation swap]** → swap fresh data into the store non-destructively (in place), preserve scroll position; never full-reload.
- **[Unbounded memory from per-key caches]** → remaining keys are few; add a small LRU only to `listWithProximity` if filter-combo growth is observed.
- **[Journey store leaks across accounts]** → clear `journeyMap` on sign-out (covered by a requirement + test).
- **[Over-caching hides real freshness needs]** → TIER 3 stays strictly network-first; the primitive is applied only to the audited TIER 1 set.
- **[Premature optimization]** → first task is a route-entry latency spike; only wire SWR where entry actually blocks on RPC.

## Migration Plan

1. Add the `RevalidatingCache<T>` utility with unit tests (staleTime, in-flight coalescing, invalidate).
2. Refactor `concert-store.ts` to obtain `listByFollower` caching from the primitive (behavior-preserving: same 24h) and add route-entry + resume revalidation.
3. Extend the primitive to `listWithProximity`, `listTop` (complete key), `listTickets`.
4. Add `TicketJourneyStore` (write-through observable) and migrate `dashboard-route.ts` + `event-detail-sheet.ts` to read/write it; clear on sign-out.
5. Wire the app-level `visibilitychange`/resume revalidation hook.
6. `make check`; ship via the frontend PR → release path.

Rollback: the primitive and journey store are additive; revert the change (no data/schema/API impact).

## Open Questions

- Exact `staleTime` values per resource (proposed: `listTop`/`listSimilar-n.a.`/`listTickets`/`listByFollower` long ≈ 24h; `listWithProximity` medium–long). Confirm during apply; they are safe to set long because resume revalidates.
- Whether `listWithProximity` needs the LRU now or only after observing filter-combo growth (default: add only if observed).
- Whether to fold the artist-image SW-runtime-cache candidate into a separate follow-up (default: separate change).
