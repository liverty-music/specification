## Why

Users who complete onboarding and later unfollow all artists are incorrectly redirected back to the artist discovery page. The current `hasCompletedOnboarding()` check equates "has followed artists" with "has completed onboarding", which are two distinct concepts. This causes poor UX for existing users who want to start fresh with their artist list. (GitHub Issue: liverty-music/specification#89)

## What Changes

- **Replace implicit onboarding check with explicit sign-up detection**: Use the existing `isSignUp` flag from OIDC state in `auth-callback.ts` to route new users to `/onboarding/discover`. Existing users always go to `/dashboard`.
- **Simplify `welcome-page.ts` canLoad**: Authenticated users are always redirected to `/dashboard`, removing the `hasCompletedOnboarding()` dependency.
- **Remove `OnboardingService` onboarding-check methods**: `hasCompletedOnboarding()`, `getRedirectTarget()` are deleted. `redirectBasedOnStatus()` is simplified to always route to dashboard for non-signup flows.
- **Remove dead localStorage key**: Delete the unused `ONBOARDING_COMPLETE_KEY` (`liverty:onboarding_complete`) from `artist-discovery-page.ts`.

## Capabilities

### New Capabilities

_(none — this is a simplification, not a new capability)_

### Modified Capabilities

- `frontend-onboarding-flow`: The onboarding completion check changes from "has followed artists" to "is a sign-up flow via OIDC state". Post-authentication routing logic is simplified.

## Impact

- **Frontend**: `auth-callback.ts`, `onboarding-service.ts`, `welcome-page.ts`, `artist-discovery-page.ts`, `loading-sequence.ts`
- **Backend/Proto**: No changes required
- **Database**: No migration required
- **Risk**: Low — routing logic is simplified, not made more complex. Region selection overlay (`needsRegion`) is independent and unaffected.
