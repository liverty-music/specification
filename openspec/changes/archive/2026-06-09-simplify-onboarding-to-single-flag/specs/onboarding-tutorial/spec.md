## REMOVED Requirements

### Requirement: Linear Step Progression

**Reason**: There is no longer a linear onboarding step machine to progress through. Onboarding state collapses to a single `isOnboarding` boolean (see `frontend-onboarding-flow` → "Single-Flag Onboarding State"), and forced navigation ordering is replaced by a soft gate. The discrete steps (`'lp'`, `'discovery'`, `'dashboard'`, `'my-artists'`, `'completed'`) and their per-step advance effects no longer exist.

**Migration**: Remove all `setStep()` calls and `onboardingStep`-keyed branching. The Welcome "Get Started" action simply navigates to discovery (no step set, since `isOnboarding` already defaults to `true`). Dashboard arrival no longer advances a step; it triggers the `finish()` completion latch instead (see `frontend-onboarding-flow`). First-visit help auto-open continues to gate on `isOnboarding` (per `onboarding-page-help`).

### Requirement: Route guard onboarding enforcement

**Reason**: The auth hook no longer compares step ordering via `stepIndex()`; onboarding step metadata on routes (`data.onboardingStep`) and ordinal gating are removed in favor of guest free roam (see `frontend-route-guard` → "Global Auth Hook").

**Migration**: Remove `data.onboardingStep` from route definitions and delete the `stepIndex()`-based allow/redirect branches in `AuthHook`. Guests are permitted to load application routes; account-only features are hidden at point of use per `guest-mode-access`.
