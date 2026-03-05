## Why

The Loading Sequence screen (Step 2) displays for only 3 seconds during onboarding, during which no backend data is fetched. Phase messages rotate too quickly to read (Phase 1 for 2s, Phase 2 for 1s, Phase 3 never shown). The screen adds a hollow delay that creates no value — no data loading, no expectation building, no meaningful content. The Dashboard already has a loading skeleton and promise-based states (pending/success/error) that handle real data fetching naturally.

## What Changes

- Remove the Loading Sequence route (`onboarding/loading`) from the onboarding flow
- Update `OnboardingStep` to skip the LOADING step: Discover (Step 1) CTA navigates directly to Dashboard (Step 3)
- Retain the Loading Sequence route for authenticated non-onboarding use (initial concert aggregation after first follow), but remove the `ONBOARDING_DISPLAY_MS` timer path
- Remove `loading-sequence.css` z-index declarations (6 occurrences) as part of the route simplification
- Update onboarding spec to reflect the shortened flow

## Capabilities

### New Capabilities

### Modified Capabilities

- `onboarding-tutorial`: Remove Step 2 (Loading) from the linear tutorial progression; Step 1 (Discover) advances directly to Step 3 (Dashboard)
- `loading-sequence`: Remove onboarding-specific display timer; Loading Sequence only serves authenticated data aggregation use case
- `frontend-onboarding-flow`: Update the onboarding journey to skip the loading screen

## Impact

- `frontend/src/services/onboarding-service.ts` — Step progression skips LOADING
- `frontend/src/routes/onboarding-loading/loading-sequence.ts` — Remove onboarding timer path
- `frontend/src/routes/onboarding-loading/loading-sequence.css` — Remove 6 z-index declarations
- `frontend/src/routes/discover/discover-page.ts` — CTA navigates directly to `/dashboard`
- `specification/openspec/specs/onboarding-tutorial/spec.md` — Update step definitions
- `specification/openspec/specs/loading-sequence/spec.md` — Remove onboarding display requirement
- `specification/openspec/specs/frontend-onboarding-flow/spec.md` — Update journey flow
