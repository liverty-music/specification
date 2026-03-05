## Tasks

### 1. Update Discover page CTA to navigate directly to Dashboard

**File:** `frontend/src/routes/discover/discover-page.ts`

In `onViewSchedule()`, change:
- `onboarding.setStep(OnboardingStep.LOADING)` -> `onboarding.setStep(OnboardingStep.DASHBOARD)`
- `router.load('onboarding/loading')` -> `router.load('/dashboard')`
- Update the log message from "advancing to loading step" to "advancing to dashboard"

### 2. Remove onboarding timer from loading-sequence

**File:** `frontend/src/routes/onboarding-loading/loading-sequence.ts`

Remove:
- `isOnboardingFlow` property
- `displayTimer` property
- `ONBOARDING_DISPLAY_MS` constant
- The `if (this.onboarding.isOnboarding)` branch in `loading()` that sets `isOnboardingFlow = true` and returns early
- The `if (this.isOnboardingFlow)` branch in `attached()` that sets the display timer
- The `displayTimer` cleanup in `unbinding()`
- The `OnboardingStep` import (if no longer used after removal)
- The `IOnboardingService` import and `onboarding` dependency (if no longer used)

The remaining code in `loading()` and `attached()` (the authenticated aggregation path) stays as-is.

### 3. Remove z-index from loading-sequence.css

**File:** `frontend/src/routes/onboarding-loading/loading-sequence.css`

Remove `z-index` declarations from the following selectors:
- `.container::before` -- remove `z-index: 0;`
- `.pulsing-orb` -- remove `z-index: 1;`
- `.message-container` -- remove `z-index: 1;`
- `.step-dots` -- remove `z-index: 1;`
- `.step-label` -- remove `z-index: 1;`
- `.progress-label` -- remove `z-index: 1;`

### 4. Update route guard (canLoad) if needed

**File:** `frontend/src/routes/onboarding-loading/loading-sequence.ts`

Review the `canLoad()` method:
- The `if (this.onboarding.isOnboarding)` branch can be removed since onboarding users will no longer reach this route. If an onboarding user somehow navigates here, the authenticated fallback path handles it.
- Alternatively, simplify to redirect onboarding users to dashboard immediately in `canLoad()`.

### 5. Update specs

**Files:**
- `specification/openspec/specs/onboarding-tutorial/spec.md` -- Apply delta from `specs/onboarding-tutorial/spec.md`
- `specification/openspec/specs/loading-sequence/spec.md` -- Apply delta from `specs/loading-sequence/spec.md`
- `specification/openspec/specs/frontend-onboarding-flow/spec.md` -- Apply delta from `specs/frontend-onboarding-flow/spec.md`

### 6. Tests

- **Unit test:** Verify `DiscoverPage.onViewSchedule()` calls `onboarding.setStep(OnboardingStep.DASHBOARD)` and `router.load('/dashboard')`.
- **Unit test:** Verify `LoadingSequence` no longer has onboarding timer behavior (no `isOnboardingFlow`, no `displayTimer`).
- **Unit test:** Verify `LoadingSequence.canLoad()` redirects onboarding users appropriately (or the branch is removed).
- **Visual regression:** Confirm loading-sequence still renders correctly without z-index (authenticated path).

### 7. Verification

- Complete the onboarding flow end-to-end: LP -> Discover -> follow 3 artists -> tap CTA -> lands on Dashboard directly (no loading screen).
- Verify the loading-sequence route still works for authenticated users with local followed artists (post-follow aggregation).
- Verify a user with `onboardingStep=2` in localStorage is handled gracefully (redirected, not stuck).
- Verify loading-sequence CSS stacking is correct without z-index (starfield behind orb, orb behind text).
