## Context

The Loading Sequence screen (Step 2 in onboarding) displays for exactly 3 seconds via `ONBOARDING_DISPLAY_MS`, during which no backend data is fetched. The phase messages rotate too quickly to be read (Phase 1 for 2s, Phase 2 for 1s, Phase 3 never shown). This screen adds a hollow delay with no value -- no data loading, no expectation building, no meaningful content. The Dashboard already has a loading skeleton with promise-based states (pending/success/error) that handle real data fetching naturally.

The Loading Sequence route is also used by authenticated users for post-follow data aggregation (`loadingService.aggregateData()`), so the route itself cannot be removed entirely.

## Goals / Non-Goals

### Goals

- Remove the Loading Sequence screen from the onboarding flow so users go directly from Discover to Dashboard.
- Remove the onboarding-specific timer path (`isOnboardingFlow` + `ONBOARDING_DISPLAY_MS`) from the loading-sequence component.
- Clean up z-index declarations in `loading-sequence.css` that are unnecessary within Shadow DOM.
- Update specs to reflect the shortened onboarding journey.

### Non-Goals

- Removing the loading-sequence route entirely (still used for authenticated data aggregation).
- Changing `OnboardingStep` numeric values (would break localStorage state for existing users).
- Redesigning the dashboard loading state or skeleton UI.
- Modifying the coach mark overlay or other tutorial steps (Steps 3-6 are unchanged).

## Decisions

### Decision 1: Keep OnboardingStep enum values unchanged

The `OnboardingStep` enum values (LP=0, DISCOVER=1, LOADING=2, DASHBOARD=3, etc.) are persisted in localStorage under `liverty:onboardingStep`. Changing numeric values would invalidate stored state for users who are mid-onboarding. Instead, the Discover page CTA will call `onboarding.setStep(OnboardingStep.DASHBOARD)` directly, skipping over the LOADING value. The LOADING=2 value is retained in the enum but never entered during onboarding.

**Rationale:** Avoids a migration concern for in-flight users. The `STEP_ROUTE_MAP` entry for LOADING can remain as a safety net -- if any user somehow has `onboardingStep=2` in localStorage, the route guard will still handle it gracefully.

### Decision 2: Retain loading-sequence route for authenticated users

The loading-sequence component has two code paths:

1. **Onboarding path** (`isOnboardingFlow = true`): Timer-based 3s display, no data fetching. This path is removed.
2. **Authenticated path**: Calls `loadingService.aggregateData()`, waits for completion, then navigates to dashboard. This path is retained.

The `canLoad()` guard already distinguishes these two cases. Only the onboarding branch in `loading()` and `attached()` is removed, along with the `isOnboardingFlow` flag, `displayTimer`, and `ONBOARDING_DISPLAY_MS` constant.

### Decision 3: Remove z-index from loading-sequence.css using `isolation: isolate`

All 6 z-index declarations in `loading-sequence.css` exist within Shadow DOM scope. Add `isolation: isolate` to the root wrapper element to create an explicit stacking context. Within this boundary, elements stack by DOM source order (later siblings paint above earlier ones) without z-index. Remove all 6 `z-index` declarations.

This follows the project-wide z-index elimination strategy (see `eliminate-z-index-stacking` change) which uses `isolation: isolate` for component-internal stacking.

Affected selectors: `.container::before` (z-index: 0), `.pulsing-orb` (z-index: 1), `.message-container` (z-index: 1), `.step-dots` (z-index: 1), `.step-label` (z-index: 1), `.progress-label` (z-index: 1).

## Risks / Trade-offs

### Risk: Users mid-onboarding at Step 2

Users who have `onboardingStep=2` in localStorage when this change deploys will be routed to the loading-sequence page. Since the onboarding timer path is removed, the `canLoad()` guard will redirect them: if they have guest followed artists, the authenticated path runs (which will fail gracefully and redirect to dashboard); if not, they redirect to discover.

**Mitigation:** The `canLoad()` guard already handles both cases. No special migration logic is needed.

### Risk: Dashboard UX without loading screen prelude

Removing the 3-second loading screen means users land on the Dashboard immediately after Discover. The Dashboard has its own skeleton loading state, but the transition may feel abrupt compared to the previous animated bridge.

**Mitigation:** The Dashboard already has promise-based loading states (pending/success/error) and skeleton UI. Concert data is pre-populated by fire-and-forget `SearchNewConcerts` calls during artist discovery. The region selector BottomSheet overlay at Step 3 provides a natural transition moment.

### Trade-off: Dead enum value

Keeping LOADING=2 in the enum adds a dead value that could confuse future developers. However, this is preferable to breaking existing users' localStorage state. A comment in the code can clarify that the value is deprecated.
