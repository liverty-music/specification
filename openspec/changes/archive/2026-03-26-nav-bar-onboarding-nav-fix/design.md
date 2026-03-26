## Context

`AuthHook.canLoad()` guards every route transition. For unauthenticated users in onboarding, it compares `stepIndex(currentStep) >= stepIndex(routeStep)` to decide whether to allow navigation. There is a special bypass for `routeStep === 'dashboard' && spotlightActive`, but once the 2-second coach-mark timer fires and `deactivateSpotlight()` is called, that bypass is no longer available.

The result: a user who has met the dashboard-unlock condition (≥5 follows or ≥3 artists with concerts) but didn't tap the coach mark during its 2-second window cannot navigate to `/dashboard` via the nav bar. The AuthHook silently redirects them back to `/discovery`.

The existing `frontend-onboarding-flow` spec already states "the user MAY tap the Dashboard icon at any time (including after the spotlight fades)", so this is an implementation gap, not a requirements gap.

## Goals / Non-Goals

**Goals:**
- Allow an unauthenticated user who has met the progression condition to navigate to `/dashboard` via the nav bar, even after the coach mark has faded.
- Keep the progression condition authoritative in `OnboardingService`, not in `AuthHook`.
- Preserve testability: the condition check must be injectable / mockable without DOM or timer state.

**Non-Goals:**
- Auto-navigating to dashboard when the condition is met (pull model, not push).
- Changing the coach-mark fade duration or UX.
- Any backend changes.

## Decisions

### D1: Add `readyForDashboard` getter to `OnboardingService` — inject counts via a single method

**Decision**: `DiscoveryRoute` calls `onboarding.setDiscoveryCounts(followed, concerts)` via two `@watch` decorators (one per count). `OnboardingService.readyForDashboard` computes the result from those stored values. A single method rather than two separate setters keeps the update atomic and the call sites uniform.

**Why this over alternatives:**

| Alternative | Problem |
|---|---|
| AuthHook reads counts directly from FollowServiceClient + ConcertService | AuthHook gains discovery-domain knowledge; harder to unit-test in isolation |
| Pass counts as arguments to a method on OnboardingService | Caller must know the thresholds; leaks domain logic out of the service |
| Duplicate the condition in AuthHook | Two sources of truth; diverge over time |

**Trade-off**: `OnboardingService` now holds two counters that are only meaningful during the discovery step. They will be `0` at all other steps but are harmless.

### D2: AuthHook check order — `readyForDashboard` sits inside the existing Priority 2 block

The new condition is inserted between the existing `stepIndex` check and the `spotlightActive` check:

```
Priority 2 (isOnboarding):
  1. stepIndex(currentStep) >= stepIndex(routeStep)  → allow (existing)
  2. readyForDashboard && routeStep === 'dashboard'   → advance step + allow (new)
  3. spotlightActive && routeStep === 'dashboard'     → advance step + allow (existing, now redundant but kept for clarity)
  4. fallthrough → redirect to current step's route
```

Keeping the `spotlightActive` check as a separate branch (instead of merging with `readyForDashboard`) makes each case explicit and independently testable.

### D3: Step advancement happens in AuthHook, not in DiscoveryRoute

When the condition passes via `readyForDashboard`, `AuthHook` calls `onboarding.setStep('dashboard')` — same as the existing `spotlightActive` branch. This keeps all step-advancement-on-navigation logic in one place.

## Risks / Trade-offs

- **`OnboardingService` counter staleness**: If `DiscoveryRoute` detaches before counts are reset, stale counts remain. Mitigation: `DiscoveryRoute.detaching()` resets `onboarding.setDiscoveryCounts(0, 0)` (or equivalent).
- **Double-advancement**: If `spotlightActive` is somehow still `true` when `readyForDashboard` is also `true`, both checks fire in sequence but `setStep` is idempotent (same value), so no harm.
- **Future threshold changes**: The progression thresholds live in `discovery-route.ts` (constants `TUTORIAL_FOLLOW_TARGET`, `TUTORIAL_TOTAL_FOLLOW_TARGET`). `readyForDashboard` in `OnboardingService` checks raw counts, not the thresholds — so the counts passed by `DiscoveryRoute` must be pre-filtered (pass the *boolean* result, or pass raw counts alongside the threshold constants). Passing raw counts with constants kept in `OnboardingService` is the cleanest; this is captured as an open question.

## Open Questions

- **Q1** ~~Open~~ **Resolved**: `OnboardingService` owns the threshold constants (`DASHBOARD_FOLLOW_TARGET = 5`, `DASHBOARD_CONCERT_TARGET = 3`) and accepts raw counts via `setDiscoveryCounts`. This keeps the condition fully unit-testable in `onboarding-service.spec.ts` without importing discovery-domain constants. `readyForDashboard` computes the result internally.
