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

### Deterministic mechanism: a per-account guest-merge receipt

Edge: migrate succeeds → clear fails → user reverts the authed state (e.g.
unfollows an artist) → reboot → a naive "migrate whatever guest data is present"
reconcile would **resurrect** the reverted item. Window-narrowing alone
(early boot, session guard, prompt drain) is probabilistic and does not close
this edge.

The deterministic fix: **a successful migration writes a persistent per-account
receipt; the receipt, not the presence of guest data, decides whether to
migrate.**

- On first authenticated boot for an account, if there is **no receipt**, the
  store migrates the guest queue (idempotent), then writes the receipt
  (`liverty:guestMerged:<userId>`), then clears the guest queue.
- On any later boot where the **receipt already exists**, residual guest data is
  treated as stale and is **cleared without re-migrating** — so reverted state
  is never resurrected, regardless of an earlier clear failure.

The receipt makes migration exactly-once per account at the queue level; backend
idempotency covers the create-then-write window. Guest follows additionally use
per-item drain (remove each artist from the queue as its `Follow` succeeds), so
even a single migration pass only ever retries genuinely failed items.

### Sign-out also evicts user-specific caches

`clearAll()` on the old `GuestService` path is replaced by per-store
`SignedOut` handling. To avoid a privacy regression on a shared browser, **any
store that caches user-specific data (e.g. `FollowStore`'s followed-artist
projections) MUST evict it on `SignedOut`.** The cache-only `ConcertStore` /
`ArtistStore` hold only non-user-specific public resources (e.g. ListTop) and so
need not participate in migration, but still evict on `SignedOut` if they ever
hold anything user-scoped.

### Returning user with a pre-existing account (`ALREADY_EXISTS`)

When `UserService.Create` returns `ALREADY_EXISTS`, the guest's onboarding
home/language are **not** applied — a returning user's saved account preferences
win (overwriting them with throwaway guest-session choices would be wrong). Only
**follows** merge into the existing account (they are additive). This is a
deliberate decision, not a silent drop.

### NULL `preferred_language` on an existing account

Independent of guest data: an authenticated user whose backend
`preferred_language` is NULL (historical rows) has nothing in any guest queue,
so reconcile does not fire for them. `UserStore` SHALL handle this by surfacing
`I18N.getLocale()` and backfilling via `UpdatePreferredLanguage`, preserving the
current `user-hydration-task` behavior.

### Modal blocks on creation only, not on follow migration

The SignUp modal awaits **user creation** (the awaited Create call) and then
navigates. Follow migration runs in the background (best-effort, via
`UserCreated`); the modal does not await it, and there is no completion barrier.
Failed follows are healed by boot reconciliation.

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
   language + UserService) → **fixes the guest locale-selector bug**. Keep
   `GuestDataMergeService.merge()` working by adapting it to `UserStore.create()`
   so signups during phase 1 still migrate follows (its removal is deferred).
2. **FollowStore** + `UserCreated` / `SignedOut` events + receipt-based
   boot-reconcile (absorb GuestService.follows + FollowServiceClient; supersede
   GuestDataMergeService).
3. **ConcertStore / ArtistStore** cache renames.
4. Consumer migration (11 sites) + removal of locale mirrors + delete
   `GuestService` and `GuestDataMergeService`.

## Decisions captured

| Decision | Resolution |
|---|---|
| Layer name | **store** (not repository) |
| Granularity | per-entity/aggregate (UserStore owns home+lang+identity), not per-field |
| Scope | one change incl. cache-only Concert/Artist stores; phased PRs |
| Boundary coordination | EA self-handling (`UserCreated`/`SignedOut`) + boot reconcile; **no orchestrator, no barrier** |
| home/lang transition | Create-time inputs (no event) |
| follows transition | post-`UserCreated`, idempotent, per-item drain, self-clear |
| Failure handling | app-boot reconcile keyed on a **per-account guest-merge receipt** (deterministic; no resurrection) |
| `ALREADY_EXISTS` | existing account preferences win — guest home/lang NOT applied; only follows merge |
| NULL server `preferred_language` | surface `I18N.getLocale()` + backfill via `UpdatePreferredLanguage` |
| Sign-out | each store self-clears AND evicts user-specific caches |
| SignUp modal | blocks on user creation only; follow migration is background |

## Out of scope

- Backend / proto / DB changes (none).
- The `fix-settings-layout` scroll fix (already shipped).
