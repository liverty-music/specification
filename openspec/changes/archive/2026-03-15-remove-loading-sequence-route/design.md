## Context

The loading-sequence route was introduced to display an animated multi-phase screen while concert data was aggregated after artist follows. The Discover page now handles concert search inline (fire-and-forget `SearchNewConcerts` per follow, concert data gate before CTA activation), making the loading-sequence route unreachable. The route's `canLoad()` guard already redirects all onboarding users to Dashboard. The "authenticated non-onboarding with local-only follows" code path is unreachable because follows always go through the backend for authenticated users.

## Goals / Non-Goals

**Goals:**
- Remove all loading-sequence code (route, service, styles, template)
- Remove the route definition from the router
- Clean up i18n keys used only by loading-sequence
- Delete the `loading-sequence` capability spec
- Update `onboarding-tutorial` and `frontend-onboarding-flow` specs to remove dead references

**Non-Goals:**
- Changing the `OnboardingStep` enum — the `LOADING = 2` value is retained for localStorage backward compatibility (users with `onboardingStep=2` are redirected by existing guards)
- Modifying the Discover page's concert search behavior (unchanged)
- Removing backend `SearchNewConcerts` or `ListSearchStatuses` RPCs (still used by Discover)

## Decisions

### 1. Full directory deletion vs. keeping stubs

**Decision**: Delete `routes/onboarding-loading/` entirely.

**Rationale**: The `canLoad()` guard already redirects all reachable users. No stub is needed because the route entry in `my-app.ts` will also be removed — there is no URL that can reach a deleted route. Users with `onboardingStep=2` in localStorage are handled by `onboarding-service.ts` step mapping, which we update to point to `dashboard` instead of `onboarding/loading`.

**Alternative considered**: Keep a minimal redirect-only route. Rejected because removing the route entry from the router achieves the same — unknown routes fall through to the default route.

### 2. OnboardingStep.LOADING enum value

**Decision**: Retain `LOADING = 2` in the enum, remove only its route mapping entry.

**Rationale**: Existing users may have `onboardingStep=2` in localStorage. The onboarding service's step validation already handles values < current step by advancing forward. Removing the enum value would require a migration path. Keeping it as a no-op value is simpler and safe.

### 3. Spec cleanup scope

**Decision**: Delete `specs/loading-sequence/` entirely. Update two existing specs with REMOVED deltas.

**Rationale**: The loading-sequence capability has no remaining use cases. The `onboarding-tutorial` Step 2 scenario and `frontend-onboarding-flow` negative requirement reference a route that will no longer exist.

## Risks / Trade-offs

- [Risk] Users with `onboardingStep=2` in localStorage navigate to the app → **Mitigation**: The `OnboardingStep.LOADING` enum value is retained. The onboarding service's step-to-route mapping is updated to map `LOADING` → `dashboard`, ensuring these users land on Dashboard. Existing route guards in the auth hook handle unauthenticated users.

- [Risk] Deep links to `/onboarding/loading` → **Mitigation**: With the route removed from `my-app.ts`, the router's fallback behavior handles unknown paths. No 404 page is needed as the router redirects to the default route.
