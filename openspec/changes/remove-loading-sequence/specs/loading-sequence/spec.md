## REMOVED Requirements

### Requirement: Minimum Display Duration (onboarding path)

> **Delta:** The `ONBOARDING_DISPLAY_MS` (3-second) timer that enforced a minimum display time during onboarding is removed. The loading sequence no longer serves the onboarding flow. All scenarios under "Minimum Display Duration" that reference onboarding or the display timer are removed.

Previously:
- The loading sequence displayed for a minimum of 3 seconds during onboarding regardless of data load speed.
- The `isOnboardingFlow` flag toggled the timer path in `attached()`.
- The `displayTimer` fired after `ONBOARDING_DISPLAY_MS`, set `onboardingStep` to DASHBOARD, and navigated to `/dashboard`.

All of the above are removed. The loading sequence now exclusively serves the authenticated data aggregation flow.

---

## MODIFIED Requirements

### Requirement: Data Aggregation Orchestration

The loading sequence SHALL only be used for authenticated users who need `loadingService.aggregateData()` after following artists. It SHALL NOT be entered during the onboarding tutorial flow.

> **Delta:** Previously, the loading sequence served two purposes: (1) a timed display during onboarding, and (2) data aggregation for authenticated users. Purpose (1) is removed. The component retains only the authenticated aggregation path.

### Requirement: CSS z-index removal via `isolation: isolate`

All z-index declarations in `loading-sequence.css` SHALL be removed. The root wrapper element SHALL use `isolation: isolate` to create an explicit stacking context. Within this boundary, elements stack by DOM source order (later siblings paint above earlier ones) without z-index.

This follows the project-wide z-index elimination strategy (see `eliminate-z-index-stacking` change) which uses `isolation: isolate` for component-internal stacking.

> **Delta:** Six z-index declarations are removed from the following selectors: `.container::before` (was z-index: 0), `.pulsing-orb` (was z-index: 1), `.message-container` (was z-index: 1), `.step-dots` (was z-index: 1), `.step-label` (was z-index: 1), `.progress-label` (was z-index: 1). `isolation: isolate` is added to the root wrapper.
