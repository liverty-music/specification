## Why

Client state today is partitioned by **auth-state** rather than by **domain
concept**. Guest (unauthenticated) state lives in `GuestService`
(localStorage), authenticated state in `UserService.current` (the backend
`User` entity), and read-only resources in ad-hoc service caches
(`ConcertService`, etc.). Because the split is by auth-state, every call site
that needs a value branches on `auth.isAuthenticated`:

```
currentHome():   auth.isAuthenticated ? user.home : guest.home
currentLocale(): user.preferredLanguage ?? <guest locale read from i18n>
follows:         authed ? followService.list() : guest.follows
```

This produces two concrete problems:

1. **Caller-side branching, repeated across 11 `IGuestService` consumers** —
   each new derived value re-implements the guest/authed fork.
2. **Low cohesion → latent inconsistency.** `GuestService` groups `home`,
   `follows`, `hype` (and, by omission, language) under one roof solely because
   they share "guest-ness". The asymmetry this produced is the guest
   **language-selector reactivity bug**: guest `home` is a first-class
   `@observable` (`GuestService.home`), but guest *language* has no observable
   owner — it is only read back through the unobservable `I18N.getLocale()`, so
   the language selector highlight freezes after a guest changes the language
   while the home row stays reactive.

The fix is to organize client state by **entity/aggregate**, each owned by an
observable **store** that internally resolves its guest(localStorage) /
authed(backend) source and caches its resources. Callers read the store and
never branch on auth. `GuestService` and the entity `*Service` classes dissolve
into this store layer.

> Supersedes the earlier `dissolve-guest-service` proposal; that narrower framing
> is generalized here into the store-layer introduction (GuestService dissolution
> becomes one outcome). Properly fixes the guest language-selector reactivity
> defect left out of `fix-settings-layout`.

## What Changes

- **Introduce a client-side store layer.** One observable store per
  entity/aggregate. A store owns: observable state, source selection
  (guest localStorage / authed backend), and resource caching. Callers stop
  branching on `auth.isAuthenticated`.
  - **`UserStore`** — owns the User entity: `home`, `preferredLanguage`,
    identity. For a guest it exposes a synthesized "current user" view sourced
    from localStorage (Null Object); for an authenticated user it owns the
    backend entity. Absorbs `GuestService.home`, the guest language storage, and
    `UserService`. Settings' `currentHome` / `currentLocale` branching collapses
    into this store.
  - **`FollowStore`** — owns the follow set + hype; caches followed artists.
    Absorbs `GuestService.follows` and `FollowServiceClient`.
  - **`ConcertStore` / `ArtistStore`** — cache-only stores for read-only
    resources (e.g. ListTop 50). No guest/authed state ownership; they do not
    participate in the auth-boundary operations. Rename of the existing
    `ConcertService` / artist query services for layer consistency.
- **Dissolve `GuestService`** — its state moves into `UserStore` (home/language)
  and `FollowStore` (follows/hype). No single auth-state-partitioned service
  remains.
- **Auth-boundary transitions become event-driven, per-store self-handling — no
  orchestrator, no completion barrier:**
  - **home / language**: captured at signup as **Create-time inputs**.
    `auth-callback` calls `userStore.create(email, locale, home)` (home/language
    read from the guest view). `UserStore.create()` persists them, switches
    `current` to the authed entity, and clears its own guest localStorage. No
    event needed for these fields.
  - **follows**: `auth-callback` publishes `GuestMigrationRequested` on every
    successful authentication (sign-up AND returning sign-in); `FollowStore`
    subscribes and migrates follows/hype (idempotent backend calls, now that a
    `user_id` exists), then clears its own guest localStorage. Best-effort.
  - **sign-out**: a `SignedOut` event is published; each store self-clears its
    own guest/authed state (idempotent, order-independent).
  - **failure / partial state**: an **app-boot reconciliation** — each store, on
    init, if authenticated and leftover guest data remains in localStorage,
    re-runs its idempotent migration and clears. Reuses the established
    boot-reconcile pattern (`user-hydration-task` backfill, settings push
    self-heal).
- **Reactivity cleanup.** Each store exposes a single resolved `@observable`;
  Settings' `currentLocale` / `currentHome` getters and `welcome-route`'s
  `currentLocale` mirror are removed. The guest language-selector highlight
  becomes reactive (the deferred Bug 2 fix).

## Capabilities

### New Capabilities

- `entity-store-layer` — defines the store-layer pattern: one observable store
  per entity/aggregate owning state + source selection (guest localStorage /
  authed backend) + resource caching; the event-driven, per-store self-handling
  auth-boundary transitions (`GuestMigrationRequested` / `SignedOut`); and the app-boot
  reconciliation safety net. (Name TBD in design.)

### Modified Capabilities

- `guest-data-merge` — the signup transition is per-store self-handling
  (home/language at Create-time, follows via `GuestMigrationRequested`), with boot
  reconciliation replacing in-flight retry coordination; clarifies merge scope
  and the idempotency contract.
- `user-home` — home preference resolution (guest storage vs `User.home`) moves
  behind `UserStore`; callers stop branching.
- `user-language-preference` — guest language gains a first-class observable
  source in `UserStore`, unified with the authed `User.preferredLanguage`;
  Settings' selector highlight becomes reactive.
- `settings` — the Language row + selector derive from `UserStore` (no auth
  branching, no render-time `I18N.getLocale()` read).

## Impact

- **Frontend only**, cross-cutting. `IGuestService` consumers to migrate (11):
  `main.ts`, `user-home-selector`, `guest-data-merge-service`,
  `follow-service-client`, `concert-service`, `dashboard-route`,
  `my-artists-route`, `auth-callback-route`, `settings-route`,
  `discovery-route`, `welcome-route`. Plus the `*Service` → `*Store` renames.
- **Removes** guest/authed caller branching and the ad-hoc locale mirrors
  (settings + welcome).
- **Phased delivery.** One change, multiple PRs: (1) store-layer scaffold +
  `UserStore` (fixes the locale bug), (2) `FollowStore` + boundary events +
  boot-reconcile, (3) `ConcertStore` / `ArtistStore` cache renames, (4) consumer
  migration + mirror removal.
- **Design risk to resolve in design.md:** boot-reconcile must not resurrect
  state the user reverted after signup (run early, session-guarded; treat guest
  localStorage as a promptly-drained pending queue).
- **No backend, proto, or DB changes.**
- **Ships to prod** via the normal frontend release per phase.
