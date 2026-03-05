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

### Requirement: CSS z-index removal

All z-index declarations in `loading-sequence.css` SHALL be removed. Since the component uses Shadow DOM, stacking context is scoped to the shadow root. Element stacking SHALL rely on `position: relative` and DOM source order.

> **Delta:** Six z-index declarations are removed from the following selectors: `.container::before` (was z-index: 0), `.pulsing-orb` (was z-index: 1), `.message-container` (was z-index: 1), `.step-dots` (was z-index: 1), `.step-label` (was z-index: 1), `.progress-label` (was z-index: 1).
