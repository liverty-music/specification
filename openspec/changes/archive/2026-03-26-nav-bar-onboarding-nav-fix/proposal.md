## Why

After the discovery coach mark fades (2-second auto-dismiss), the `AuthHook` blocks navigation to `/dashboard` because `onboardingStep` is still `'discovery'` and `spotlightActive` is `false`. Tapping any nav bar icon while in this state silently redirects back to discovery, violating the existing spec requirement that "the user MAY tap the Dashboard icon at any time (including after the spotlight fades)."

## What Changes

- Add `readyForDashboard: boolean` computed getter to `OnboardingService` — returns `true` when step is `'discovery'` and the progression condition is met (≥5 follows OR ≥3 artists with concerts).
- Update `AuthHook` to allow dashboard navigation when `onboarding.readyForDashboard` is `true`, and advance the step to `'dashboard'` at that point.
- Add the missing guard scenario to `frontend-route-guard` spec so the rule is explicit and testable.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `frontend-route-guard`: Add scenario — unauthenticated user in `'discovery'` step who has met the progression condition SHALL be allowed to navigate to `/dashboard` via the nav bar, and the system SHALL advance `onboardingStep` to `'dashboard'` at that point.

## Impact

- **`src/services/onboarding-service.ts`** — new `readyForDashboard` getter (depends on `IFollowServiceClient` and `IConcertService` counts, or accepts them as an argument for testability).
- **`src/hooks/auth-hook.ts`** — one additional condition in Priority 2 branch.
- **`src/routes/discovery/discovery-route.ts`** — wires follow/concert counts into `OnboardingService` (or passes them to a new method).
- No proto changes, no backend changes, no BSR release needed.
