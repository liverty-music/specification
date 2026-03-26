## 1. OnboardingService — readyForDashboard

- [x] 1.1 Add threshold constants `DASHBOARD_FOLLOW_TARGET = 5` and `DASHBOARD_CONCERT_TARGET = 3` to `OnboardingService` (move from `discovery-route.ts`)
- [x] 1.2 Add `followedCount: number` and `artistsWithConcertsCount: number` public properties (initialized to `0`) to `OnboardingService`
- [x] 1.3 Add `setDiscoveryCounts(followed: number, concerts: number): void` method to update both counts
- [x] 1.4 Add `readyForDashboard: boolean` computed getter — returns `true` only when `step === 'discovery'` AND (`followedCount >= DASHBOARD_FOLLOW_TARGET` OR `artistsWithConcertsCount >= DASHBOARD_CONCERT_TARGET`)
- [x] 1.5 Write unit tests for `readyForDashboard` covering all 4 scenarios in the spec (follow threshold, concert threshold, below threshold, wrong step)

## 2. DiscoveryRoute — wire counts into OnboardingService

- [x] 2.1 Remove the local `TUTORIAL_FOLLOW_TARGET` and `TUTORIAL_TOTAL_FOLLOW_TARGET` constants (now owned by `OnboardingService`)
- [x] 2.2 Add a `@watch` on `followedCount` and `concertService.artistsWithConcertsCount` to call `this.onboarding.setDiscoveryCounts(...)` whenever either changes
- [x] 2.3 In `detaching()`, call `this.onboarding.setDiscoveryCounts(0, 0)` to reset counts when leaving the discovery page
- [x] 2.4 In `loading()`, call `this.onboarding.setDiscoveryCounts(...)` once after hydration — `@watch` only fires on changes, not on the initial value, so an explicit sync is required when counts are already non-zero at component load time

## 3. AuthHook — allow navigation when readyForDashboard

- [x] 3.1 In the Priority 2 block (after the `stepIndex` check), add: if `routeStep === 'dashboard' && this.onboarding.readyForDashboard` → call `this.onboarding.setStep(OnboardingStep.DASHBOARD)` and return `true`
- [x] 3.2 Write unit tests for the new AuthHook scenario (TC-RG-05: discovery-step user with readyForDashboard=true navigates to dashboard → allowed + step advanced)
- [x] 3.3 Write unit test for the inverse (TC-RG-06: discovery-step user with readyForDashboard=false navigates to dashboard → redirected to discovery)

## 4. Verification

- [x] 4.1 Run `make check` in `frontend/` — all lint and unit tests pass
- [x] 4.2 Manual smoke test: follow 5 artists → wait for coach mark to fade → tap Home nav → confirm navigation to dashboard succeeds
- [x] 4.3 Manual smoke test: follow 4 artists (no concerts) → tap Home nav → confirm redirect back to discovery (guard still blocks when condition not met)
