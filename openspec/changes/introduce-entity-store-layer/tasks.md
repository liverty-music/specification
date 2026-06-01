# Tasks

One change, delivered in phased PRs. Each phase ships independently to prod.

## 1. Store-layer scaffold + UserStore (PR 1 — also fixes the guest locale bug)

- [x] 1.1 Define the store-layer convention (observable state owner + source
      selection + cache) and a minimal guest storage adapter pattern, following
      the `OnboardingService` precedent.
- [x] 1.2 Introduce `UserStore` **composing** `IUserService` (authed `current`)
      and an observable guest source (guest home + anonymous-period language on
      `GuestService`). Expose a single resolved observable for home and for
      preferred language (guest = localStorage-backed; authed = `User` entity).
      De-risk: `UserServiceClient`'s auth logic is NOT rewritten here; full
      absorption is deferred (see 1.3 / Phase 2).
- [x] 1.3 Handle a NULL server `preferred_language` by surfacing the (observable,
      i18n-event-mirrored) active locale and backfilling once via
      `UpdatePreferredLanguage` (session-guarded, shared with the hydration task).
- [x] 1.3b (DONE in Phase 5b) Absorb `UserService` into `UserStore.create()`
      (persist Create-time home/language inputs, publish `GuestMigrationRequested`, clear own
      guest localStorage; `ALREADY_EXISTS` → existing account wins, guest
      home/language not applied). Until then `UserService.create()` /
      `GuestDataMergeService.merge()` remain the create+migrate path.
- [x] 1.3a `GuestDataMergeService.merge()` remains functional in Phase 1
      (untouched — it still owns the Create + follow migration). Its REMOVAL is
      deferred to phase 4; no signup between deploys strands guest follows.
- [x] 1.4 Migrate `SettingsRoute` to read home/language from `UserStore`; remove
      the `currentLocale` / `currentHome` auth-branching getters and the
      render-time `I18N.getLocale()` read. Remove `welcome-route`'s
      `currentLocale` mirror.
- [x] 1.5 Verify the guest language-selector highlight is reactive (change en→ja
      as a guest, reopen selector → reflects ja). Unit + component tests.
- [ ] 1.6 `make check` green. Open PR 1, CI green, merge, release, ship to prod.

## 2. FollowStore + boundary events + boot reconcile (PR 2)

- [x] 2.1 Introduce `FollowStore`: absorb `GuestService.follows`/hype and
      `FollowServiceClient`; cache followed artists; expose observable follow set.
- [x] 2.2 Subscribe `GuestMigrationRequested` → migrate follows + hype (idempotent),
      removing each artist from `guest.followedArtists` as its `Follow` succeeds
      (per-item drain; only failures remain). Write the per-account guest-merge
      receipt on success.
- [x] 2.3 Publish/subscribe `SignedOut` → each store self-clears (idempotent,
      order-independent) AND evicts user-specific caches (e.g. followed-artist
      projections), preserving the privacy guarantee of the old
      `GuestService.clearAll()` sign-out path.
- [x] 2.4 Implement boot reconciliation keyed on the **guest-merge receipt**:
      no receipt + leftover queue → migrate, write receipt, clear; receipt
      already present + residual queue → clear WITHOUT re-migrating (no
      resurrection). Run early, session-guarded.
- [x] 2.5 Tests: migration on `GuestMigrationRequested`, self-clear, sign-out clear,
      boot-reconcile (incl. the no-resurrect guard). `make check` green.
- [ ] 2.6 Open PR 2, CI green, merge, release, ship to prod.

## 3. Cache-only stores (PR 3)

- [x] 3.1 Rename `ConcertService` → `ConcertStore` and the artist query service →
      `ArtistStore`; keep their resource caches (e.g. ListTop 50). No guest/authed
      ownership; no boundary-event participation.
- [x] 3.2 Update consumers of the renamed stores. `make check` green.
- [ ] 3.3 Open PR 3, CI green, merge, release, ship to prod.

## 4. Consumer migration + GuestService removal (PR 4)

- [x] 4.1 Migrate the remaining `IGuestService` consumers (dashboard,
      my-artists, discovery, concert-service, user-home-selector,
      auth-callback, main.ts) to the stores; remove all
      `auth.isAuthenticated` source-selection branching at call sites.
- [x] 4.2 Delete `GuestService` and `GuestDataMergeService` once no references
      remain.
- [ ] 4.3 Tests + `make check` green. Open PR 4, CI green, merge, release, ship
      to prod.

## 5. Absorption completion + dead-code (PR 5a / 5b)

- [x] 5a.1 Absorb `FollowServiceClient` into `FollowStore`: migrate the 4 routes
      that inject `IFollowServiceClient` directly (dashboard, discovery,
      my-artists, import-ticket-email) to `IFollowStore`; remove the separate
      `IFollowServiceClient` DI registration. ConcertStore keeps its direct
      storage-adapter reads (cycle defense).
- [x] 5a.2 Remove `welcome-route`'s `@observable currentLocale` mirror +
      `currentLocaleChanged`; bind the language radio through `UserStore`
      (the deferred task 1.4 item).
- [x] 5a.3 Tests + `make check`; PR 5a, CI green, merge.
- [x] 5b.1 (was 1.3b) Absorb `UserService`/`UserServiceClient` into `UserStore`:
      move `ensureLoaded`/`create`/`updateHome`/`updatePreferredLanguage`/`clear`/
      `resendEmailVerification` + the `@observable current` into `UserStore`;
      migrate the 11 `IUserService` consumers to `IUserStore`; delete
      `UserServiceClient`; relocate `ProvisionResult`. Preserve the auth bootstrap
      (cache->Get->Create->PermissionDenied recovery, write-through) exactly.
- [x] 5b.2 Tests + `make check`; PR 5b, CI green, merge.

## 6. Close-out

- [ ] 5.1 Confirm all phases live in prod; verify the guest language selector and
      home flows in the running app.
- [ ] 5.2 Archive this OpenSpec change.
