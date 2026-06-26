## 1. My Artists route — non-blocking load

- [x] 1.1 Extract the fetch body of `loading()` into `loadArtists(): Promise<void>` (mapping followed → `MyArtist[]`, `prevHypes` seed, logging, `isLoading` finally), mirroring `dashboard-route.ts`'s `loadData()` shape. The method OWNS the `AbortController`: abort-first then `this.abortController = new AbortController()`, then fetch with `this.abortController.signal`.
- [x] 1.2 Confirm abort-first + `AbortError` swallow inside `loadArtists` (the single controller owner — do NOT also create the controller in `loading()`).
- [x] 1.3 In `loading()`, keep ONLY the non-controller synchronous prelude (`isLoading = true`, signup-banner flag) and call `void this.loadArtists()` instead of awaiting. Do not create the `AbortController` here, or the routine's abort-first would abort the just-created controller and the first fetch would `AbortError`.
- [x] 1.4 Confirm `detaching()` still aborts the in-flight request.

## 2. Dashboard route — non-blocking load + observation-gated side effects

- [x] 2.1 Change the region-set branch at `loading()` from `await this.loadData()` to `void this.loadData()`; leave the `needsRegion` branch and `onHomeSelected()`'s awaited `loadData()` as-is.
- [x] 2.2 Re-anchor `onTimetableReady()` (celebration + completion latch) to observed data arrival via `@watch` (or an `@observable` readiness flag) instead of the `attached()` call, guarded by `!needsRegion && !isLoading && data-present` and one-shot latches.
- [x] 2.3 Remove/adjust the `attached()` `!needsRegion → onTimetableReady()` call so the celebration no longer depends on `loading()` having awaited the fetch; ensure both arrival paths (load-driven and `onHomeSelected`-driven) route through the same gated handler exactly once.
- [x] 2.4 Verify `maybeCelebrate()`/`maybeFinishOnboarding()` guards still hold (post-signup vs guest tiers, `followedCount` engagement) under the new timing.

## 3. Discovery route — non-blocking load

- [x] 3.1 Extract `await this.bubbles.loadInitialArtists(...)` into `loadInitialBubbles(): Promise<void>` (keep the try/catch → Snack on failure).
- [x] 3.2 Keep the onboarding hydrate prelude before the fetch; call `void this.loadInitialBubbles()` from `loading()`.
- [x] 3.3 Confirm order-independence: canvas `artistsChanged` (`!this.ctx` guard) + `attached()` seed render bubbles whether data arrives before or after attach; keep the concurrent `searchConcertsForArtist` fan-out.

## 4. Tests — deterministic async

- [x] 4.1 `test/routes/my-artists-route.spec.ts`: update the `loading` suite and `beforeEach(await sut.loading())` suites to `await sut.loadArtists()` (or `tasksSettled()`) before asserting populated state.
- [x] 4.2 `test/routes/discovery-route.spec.ts`: drain via awaiting `loadInitialBubbles()` / `tasksSettled()` rather than relying on open-ended fake-timer draining as the primary mechanism.
- [x] 4.3 `test/routes/dashboard-route.spec.ts`: add coverage that the celebration/latch fires on observed data arrival (not over a spinner) and not before data when the load is non-blocking; keep synchronous `needsRegion`/banner assertions. (Also updated the colocated `src/routes/dashboard/dashboard-route.spec.ts`, which drives the same side effects.)
- [x] 4.4 Add/adjust a test asserting navigation is non-blocking: `loading()` resolves before the fetch settles (e.g. fetch mock pending) and `isLoading` is true at attach.

## 5. Verify locally

- [x] 5.1 `make test` (vitest) — the three route specs pass. (Full suite: 1303 passed, 2 skipped.)
- [x] 5.2 `make lint` (Biome + stylelint + typecheck) clean. (Exit 0; only pre-existing warnings unrelated to changed files.)
- [x] 5.3 Manual: `npm start`, rapid menu-tab tapping — new frame + spinner/empty state appears immediately, data fills in afterward, no frozen outgoing screen; Dashboard celebration appears over a real timetable.

## 6. Ship to prod

- [x] 6.1 Open the frontend PR (Refs #469), pass CI, address review, merge to `main`. (PR #472 merged 2026-06-26; all CI green incl. E2E/Visual/Security Audit; no review comments.)
- [x] 6.2 Cut the frontend GitHub Release (`vX.Y.Z`) → retag to prod AR; confirm the automated `repository_dispatch` pin-bump pushes to `cloud-provisioning:main` and ArgoCD auto-syncs. (Release v1.20.0; release workflow `dispatch-prod-pin` success → CP commits pin web-app + admin-app prod overlays to v1.20.0; ArgoCD synced after a hard-refresh nudge past a stale repo-server cache.)
- [x] 6.3 Verify in prod: tap menu tabs on `liverty-music.app` — view swaps immediately with spinner, data streams in; no regression in Dashboard celebration / onboarding completion. (Playwright on prod v1.20.0: menu-tab swaps 17–73ms across all tabs; Discovery rendered 45 live artists; Dashboard home-selector renders immediately; 0 console errors; celebration correctly deferred while `needsRegion` — not displayed over a non-ready timetable.)
