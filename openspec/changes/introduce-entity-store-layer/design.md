# Design

## Goal

Organize client state by **entity/aggregate**, not by auth-state. Each
entity/aggregate is owned by an observable **store** that internally resolves
its source (guest localStorage / authed backend) and caches its resources, so
callers never branch on `auth.isAuthenticated`.

## Naming: "store", not "repository"

The layer holds observable in-memory state, caches resources, AND selects a
persistence source. That is a **store** (Pinia/Svelte sense), not a classic
stateless DDD repository. The existing classes are `*Service`; renaming to
`*Store` signals "observable state owner + cache + source selection" more
honestly than either `Service` or `Repository`.

## Store inventory

| Store | guest/authed dual ownership | Responsibilities | Boundary participation |
|---|---|---|---|
| **UserStore** | yes (`home`, `preferredLanguage`) | User entity state; guest = synthesized "current user" view (Null Object) from localStorage; identity when authed | create (home/lang at Create-time), self-clear |
| **FollowStore** | yes (`follows` + `hype`) | follow set state + followed-artist cache | migrate on `UserCreated`, self-clear |
| **ConcertStore** | no | cache read-only resources (e.g. ListTop 50) | none (cache-only) |
| **ArtistStore** | no | artist query cache | none (cache-only) |

`GuestService` dissolves: `home` → UserStore, `follows`/`hype` → FollowStore.
`UserService` → UserStore. `FollowServiceClient` → FollowStore.
`ConcertService` → ConcertStore.

## Auth-boundary transitions — event-driven, per-store, no orchestrator

The earlier proposal posited a saga/orchestrator for atomicity + ordering.
That requirement **dissolves** once state is per-store, because there is no
cross-store dependency that needs a global barrier:

- **home / language are Create-time inputs, not post-event migrations.**
  `auth-callback` reads the guest view and calls
  `userStore.create(email, locale, home)`. They are baked into the Create RPC
  atomically; nothing migrates them afterward. `UserStore.create()` clears its
  own guest localStorage on success.
- **follows are the only post-create migration**, and only `FollowStore` cares.
  The single ordering edge is "create before follow-migrate" (follows need a
  `user_id`). Expressed as: `UserStore.create()` publishes `UserCreated` →
  `FollowStore` subscribes, migrates (idempotent), clears its own localStorage.
- **No completion barrier** is needed: each store clears its own data when its
  own migration completes; stores are mutually independent.

```
sign-up
  auth-callback
    └─ userStore.create(email, locale, home)        # home/lang = Create inputs
         ├─ persist + current = authed user
         ├─ clear own guest localStorage (home/lang)
         └─ publish UserCreated ─────────────► FollowStore (subscribe)
                                                  ├─ migrate follows+hype (idempotent)
                                                  └─ clear own guest localStorage

sign-out
  publish SignedOut ─────────► UserStore.clear / FollowStore.clear   # each self-clears

app boot (safety net)
  each store.init: if authed && leftover guest data → idempotent reconcile (re-migrate + clear)
```

EA fits here precisely because the barrier requirement is gone: the boundary
signals (`UserCreated`, `SignedOut`) are decoupled, and each store self-handles
its own slice. This matches the codebase's existing EA usage
(`i18n:locale:changed`, `ConsentChanged`, `Snack`).

## Failure handling: app-boot reconciliation (not in-flight retry)

Partial-migration failures (crash mid-migrate, network loss) are healed by an
idempotent boot-time reconcile rather than a saga retry: on init, if the user is
authenticated and guest data remains in localStorage, re-run the migration
(backend follow/setHype are idempotent) and clear. This reuses the established
pattern of `user-hydration-task` (boot backfill + session flag) and the settings
push self-heal.

### Design risk to resolve: reconcile must not resurrect reverted state

Edge: migrate succeeds → clear fails → user changes the authed state (e.g.
unfollows an artist) → reboot → naive reconcile re-migrates the stale guest item
and **resurrects** it.

Mitigations (to specify):
- Run reconcile in the **earliest boot phase, before the UI is interactive**,
  guarded by a per-session flag (as `user-hydration-task` does).
- Treat guest localStorage as a **pending-migration queue** that is drained
  (cleared) promptly and atomically with a successful migrate, so the
  migrated-but-not-cleared window is minimal.
- Reconcile only fires when a leftover queue is actually present.

This edge does not invalidate the approach; it is the one detail the
reconciliation requirement must nail.

## Reactivity cleanup

Each store exposes a single resolved `@observable`. Remove:
- `SettingsRoute.currentLocale` / `currentHome` getters' auth branching → read
  `userStore` directly.
- `welcome-route`'s `@observable currentLocale` mirror + `currentLocaleChanged`.
- The render-time `I18N.getLocale()` read that froze the guest selector.

The guest language-selector highlight becomes reactive because `UserStore`
exposes the active language as observable state for both guest and authed paths.

## Caching (ConcertStore / ArtistStore)

Read-only resources (ListTop 50, followed-artist projections) are cached in
their store. These stores have no guest/authed ownership duality (a guest may
hit a different RPC variant, but the data is fetched, not owned), so they do not
subscribe to `UserCreated` / `SignedOut` and are excluded from reconcile. They
are included in this change only for layer-naming consistency
(`*Service` → `*Store`).

## Phasing (one change, multiple PRs)

1. Store-layer scaffold + **UserStore** (absorb GuestService.home + guest
   language + UserService) → **fixes the guest locale-selector bug**.
2. **FollowStore** + `UserCreated` / `SignedOut` events + boot-reconcile
   (absorb GuestService.follows + FollowServiceClient + GuestDataMergeService).
3. **ConcertStore / ArtistStore** cache renames.
4. Consumer migration (11 sites) + removal of locale mirrors + delete
   `GuestService`.

## Decisions captured

| Decision | Resolution |
|---|---|
| Layer name | **store** (not repository) |
| Granularity | per-entity/aggregate (UserStore owns home+lang+identity), not per-field |
| Scope | one change incl. cache-only Concert/Artist stores; phased PRs |
| Boundary coordination | EA self-handling (`UserCreated`/`SignedOut`) + boot reconcile; **no orchestrator, no barrier** |
| home/lang transition | Create-time inputs (no event) |
| follows transition | post-`UserCreated`, idempotent, self-clear |
| Failure handling | idempotent app-boot reconcile (not in-flight retry) |

## Out of scope

- Backend / proto / DB changes (none).
- The `fix-settings-layout` scroll fix (already shipped).
