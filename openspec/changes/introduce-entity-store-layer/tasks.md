# Tasks

One change, delivered in phased PRs. Each phase ships independently to prod.

## 1. Store-layer scaffold + UserStore (PR 1 — also fixes the guest locale bug)

- [ ] 1.1 Define the store-layer convention (observable state owner + source
      selection + cache) and a minimal guest storage adapter pattern, following
      the `OnboardingService` precedent.
- [ ] 1.2 Introduce `UserStore`: absorb `UserService` (authed `current`) and the
      guest home + anonymous-period language storage from `GuestService`. Expose
      a single resolved observable for home and for preferred language
      (guest = localStorage-backed synthesized view; authed = `User` entity).
- [ ] 1.3 `UserStore.create(email, locale, home)`: persist Create-time inputs,
      switch `current` to the authed entity, clear own guest localStorage,
      publish `UserCreated`.
- [ ] 1.4 Migrate `SettingsRoute` to read home/language from `UserStore`; remove
      the `currentLocale` / `currentHome` auth-branching getters and the
      render-time `I18N.getLocale()` read. Remove `welcome-route`'s
      `currentLocale` mirror.
- [ ] 1.5 Verify the guest language-selector highlight is reactive (change en→ja
      as a guest, reopen selector → reflects ja). Unit + component tests.
- [ ] 1.6 `make check` green. Open PR 1, CI green, merge, release, ship to prod.

## 2. FollowStore + boundary events + boot reconcile (PR 2)

- [ ] 2.1 Introduce `FollowStore`: absorb `GuestService.follows`/hype and
      `FollowServiceClient`; cache followed artists; expose observable follow set.
- [ ] 2.2 Subscribe `UserCreated` → migrate follows + hype (idempotent), then
      self-clear guest follow localStorage (best-effort). Replaces
      `GuestDataMergeService.merge()`.
- [ ] 2.3 Publish/subscribe `SignedOut` → each store self-clears (idempotent,
      order-independent). Replace `GuestService.clearAll()` call sites.
- [ ] 2.4 Implement boot reconciliation: on init, if authenticated and leftover
      guest data remains, re-run idempotent migration + clear; run in the
      earliest boot phase, session-guarded, treating guest localStorage as a
      promptly-drained pending queue (no resurrection of reverted state).
- [ ] 2.5 Tests: migration on `UserCreated`, self-clear, sign-out clear,
      boot-reconcile (incl. the no-resurrect guard). `make check` green.
- [ ] 2.6 Open PR 2, CI green, merge, release, ship to prod.

## 3. Cache-only stores (PR 3)

- [ ] 3.1 Rename `ConcertService` → `ConcertStore` and the artist query service →
      `ArtistStore`; keep their resource caches (e.g. ListTop 50). No guest/authed
      ownership; no boundary-event participation.
- [ ] 3.2 Update consumers of the renamed stores. `make check` green.
- [ ] 3.3 Open PR 3, CI green, merge, release, ship to prod.

## 4. Consumer migration + GuestService removal (PR 4)

- [ ] 4.1 Migrate the remaining `IGuestService` consumers (dashboard,
      my-artists, discovery, concert-service, user-home-selector,
      auth-callback, main.ts) to the stores; remove all
      `auth.isAuthenticated` source-selection branching at call sites.
- [ ] 4.2 Delete `GuestService` and `GuestDataMergeService` once no references
      remain.
- [ ] 4.3 Tests + `make check` green. Open PR 4, CI green, merge, release, ship
      to prod.

## 5. Close-out

- [ ] 5.1 Confirm all phases live in prod; verify the guest language selector and
      home flows in the running app.
- [ ] 5.2 Archive this OpenSpec change.
