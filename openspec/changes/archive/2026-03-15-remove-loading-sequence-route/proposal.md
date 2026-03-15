## Why

The loading-sequence route (`/onboarding/loading`) was designed to display an animated waiting screen while concert data was aggregated after artist follows. This use case no longer exists: the Discover page now triggers `SearchNewConcerts` fire-and-forget during each artist follow, confirms concert data availability via the concert data gate, and navigates directly to Dashboard. The route's `canLoad()` guard already redirects onboarding users to Dashboard, and the "authenticated non-onboarding" path (local-only follows without backend state) is unreachable in practice. The route, its service, its spec, and its i18n keys are dead code.

## What Changes

- Delete the loading-sequence route: `loading-sequence.ts`, `loading-sequence.html`, `loading-sequence.css`
- Delete the loading-sequence service: `loading-sequence-service.ts`
- Remove the route definition from `my-app.ts`
- Remove the `OnboardingStep.LOADING` route mapping from `onboarding-service.ts` (retain the enum value `2` for localStorage backward compatibility)
- Remove loading i18n keys from `ja/translation.json` and `en/translation.json`
- Delete the `loading-sequence` capability spec

## Capabilities

### New Capabilities

### Modified Capabilities

- `onboarding-tutorial`: Remove the Step 2 (LOADING) deprecated scenario entirely — it is no longer referenced by any code
- `frontend-onboarding-flow`: Remove the "SHALL NOT navigate to `/onboarding/loading`" negative requirement (the route no longer exists, so the constraint is vacuous)

## Impact

- `frontend/src/routes/onboarding-loading/` — entire directory deleted
- `frontend/src/services/loading-sequence-service.ts` — deleted
- `frontend/src/my-app.ts` — route entry removed
- `frontend/src/services/onboarding-service.ts` — route mapping entry removed
- `frontend/src/locales/ja/translation.json` — `loading` key removed
- `frontend/src/locales/en/translation.json` — `loading` key removed
- `specification/openspec/specs/loading-sequence/` — capability spec deleted
- `specification/openspec/specs/onboarding-tutorial/spec.md` — Step 2 scenario removed
- `specification/openspec/specs/frontend-onboarding-flow/spec.md` — negative requirement removed
