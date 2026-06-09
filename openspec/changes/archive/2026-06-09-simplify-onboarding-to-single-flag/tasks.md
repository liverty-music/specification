## 1. Collapse OnboardingService to a single flag

- [x] 1.1 Rewrite `services/onboarding-service.ts` to hold one `@observable` latched boolean (`onboardingComplete`) with `get isOnboarding()` (= `!onboardingComplete`), `get isCompleted()` (= `!isOnboarding`), and a single one-way `finish()` mutator. The backing field MUST be `@observable` so the getters notify dependent bindings/watchers (`pwa-install-service` `@watch(isCompleted)`, `app-shell.html` `if.bind`). Remove `step`, `setStep`, `reset`, `complete`, `currentStep`, `getRouteForCurrentStep`, `readyForDashboard`, `setDiscoveryCounts`, `followedCount`, `artistsWithConcertsCount`, and the spotlight properties/methods.
- [x] 1.2 Reduce `entities/onboarding.ts` to the minimum: delete `OnboardingStep`, `STEP_ORDER`, `stepIndex`, `STEP_MIGRATION`, `normalizeStep`, `isOnboarding`/`isCompleted` step predicates. Remove `STEP_ROUTE_MAP` from `onboarding-service.ts`.
- [x] 1.3 Update `adapter/storage/onboarding-storage.ts`: persist `onboardingComplete` (boolean) under a single key; add a one-time construction-time migration that sets `onboardingComplete = completedSet.has(legacy onboardingStep)` where `completedSet = {'completed', '7'}` (legacy numeric `'7'` mapped to `COMPLETED`), then deletes the legacy `onboardingStep` key. Any other legacy value (`'discovery'`, `'my-artists'`, `'detail'`, absent) maps to `false`.
- [x] 1.4 Move `DASHBOARD_FOLLOW_TARGET` / `DASHBOARD_CONCERT_TARGET` out of `onboarding-service.ts` into a `constants` module.
- [x] 1.5 Update `entities/index.ts` and any barrel exports to drop the removed onboarding symbols.

## 2. Extract the coach mark into CoachMarkService

- [x] 2.1 Create `services/coach-mark-service.ts` owning spotlight state (`target`, `message`, `radius`, `active`, `onTap`) and `activate()` / `deactivate()`; register it in `main.ts`.
- [x] 2.2 Repoint `app-shell.html` coach-mark bindings from `onboarding.*` to the new `CoachMarkService`.
- [x] 2.3 Update `DiscoveryRoute` to compute the coach-mark trigger from live counts: `isOnboarding && (followedCount >= DASHBOARD_FOLLOW_TARGET || artistsWithConcertsCount >= DASHBOARD_CONCERT_TARGET) && !shown`; call `coachMark.activate(...)`. Remove the `setDiscoveryCounts` mirror writes and the `@watch` handlers that fed it.
- [x] 2.4 Ensure the coach-mark `onTap` performs navigation only (no step advance); deactivate on route `detaching()`.
- [x] 2.5 Make the coach mark non-blocking: remove the four `.mask-*` click-blocker divs and the `<au-viewport>` scroll lock from the coach-mark component (the spotlight stays a `pointer-events: none` visual cutout). Remove the multi-step "continuous spotlight persistence" logic (anchor-name reassignment across steps, Step-6 teardown) and the empty-selector guard / retry-timer cancellation move into `CoachMarkService`.

## 3. Fix #444 — decouple hype editing from onboarding

- [x] 3.1 In `routes/my-artists/my-artists-route.ts` `onHypeInput`, remove the `isOnboardingStepMyArtists` branch (`setStep(CONSENT)`) and the `if (this.isOnboarding) { artist.hype = prev; return }` revert guard so every hype change applies and persists.
- [x] 3.2 Remove now-unused `isOnboardingStepMyArtists` / `OnboardingStep` references from the My Artists route; confirm the guest path persists via `followStore.setHype` only.

## 4. Soft-gate the route guard

- [x] 4.1 In `hooks/auth-hook.ts`, remove the onboarding ordinal branches (`tutorialStep`/`onboardingStep` comparison, `readyForDashboard`, step-route redirects, blocked-nav snackbars, the LP-limbo Priority 5 path). Keep: authenticated bypass, `data.auth === false` public allow, guest free roam.
- [x] 4.2 Remove `data.onboardingStep` and `data.earlyUnlock` route metadata from `app-shell.ts` route definitions that only existed for ordinal gating.
- [x] 4.3 Add a dashboard empty-state CTA (to discovery) shown when an unauthenticated user has zero follows, per `frontend-route-guard` "Guest with no follows lands on the dashboard".

## 5. Wire the completion latch (B1 ∧ B2)

- [x] 5.1 In `routes/dashboard/dashboard-route.ts`, replace the `DASHBOARD → MY_ARTISTS` `setStep` with a `finish()` call gated on a *meaningful* first arrival: timetable real (region set + data loaded) AND `followedCount >= 1`. Evaluate it after the `maybeCelebrate()` decision (so it observed `isOnboarding === true`) honoring the `needsRegion` deferral, but drive it from the data-ready+engaged condition — NOT from the celebration actually rendering (a guest with `celebrationShown === '1'` must still latch). Do NOT latch on a zero-follow arrival.
- [x] 5.2 In `routes/auth-callback/auth-callback-route.ts`, replace `onboarding.complete()` with `finish()` (idempotent backstop).
- [x] 5.3 In `routes/welcome/welcome-route.ts`, drop `onboarding.reset()` / `setStep(DISCOVERY)`; "Get Started" simply navigates to discovery.

## 6. Update dependent consumers and docs

- [x] 6.1 Confirm `notification-prompt`, `pwa-install-service`, and the dashboard signup banner still read `isCompleted` (now `!isOnboarding`) and behave correctly; adjust any `@watch` targets if needed.
- [x] 6.2 Confirm `onboarding-popover-guide` and `onboarding-page-help` still gate on `isOnboarding`; no behavior change expected.
- [ ] 6.3 Refresh the `state-transition-diagram` capability doc: replace the onboarding state-machine section/Mermaid with the two-state (`onboarding` → `completed`) model and the single `finish()` latch trigger (documentation sync, applied during archive per the OpenSpec sync workflow).

## 7. Tests

- [x] 7.1 My Artists: regression test for #444 — second and subsequent hype taps apply and persist (guest, during onboarding) and never revert.
- [x] 7.2 OnboardingService: legacy-key migration (`'completed'` → `false`, any other value / absent → `true`) and `finish()` one-way latch.
- [x] 7.3 AuthHook: guest free roam (dashboard reachable with zero follows → empty-state, no redirect); authenticated bypass; public-route allow.
- [x] 7.4 Coach mark: trigger fires from live follow/concert counts gated on `isOnboarding`, shows once per session, `onTap` navigates without step mutation.
- [x] 7.5 Latch timing: a region-less guest still sees the light celebration before `finish()` latches; and `finish()` still fires when the celebration is suppressed (`celebrationShown === '1'`) on a meaningful arrival.
- [x] 7.6 Latch engagement gate: a zero-follow guest landing on the dashboard does NOT latch (`isOnboarding` stays `true`); latches only after `followedCount >= 1`.
- [x] 7.7 Reactivity: `finish()` flips `isCompleted`/`isOnboarding` and fires the `pwa-install-service` watcher and `app-shell` bindings (asserts the `@observable` backing field).

## 8. Verify, ship to prod

- [x] 8.1 Run `make check` (lint + test + typecheck) until green.
- [x] 8.2 This change adds new rendered UI (dashboard empty-state CTA in 4.3, non-blocking coach-mark changes in 2.5), so visual baselines WILL change: delete all visual-baselines artifacts on main to force baseline regeneration (mandatory — an intentional UI change otherwise blocks merge).
- [x] 8.3 Open the frontend PR (Refs #444); drive CI green and merge.
- [x] 8.4 Cut the frontend GitHub Release (SemVer tag) to retag the prod AR image and trigger the automated prod-pin bump (frontend prod is AR-only; ArgoCD auto-syncs). Confirm the rollout.
