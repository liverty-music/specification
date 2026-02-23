## 1. Auth Callback Routing

- [x] 1.1 Modify `auth-callback.ts` to route based on `isSignUp`: if `state?.isSignUp` is true, navigate to `/onboarding/discover` after `provisionUser()`; otherwise navigate to `/dashboard`
- [x] 1.2 Remove the call to `onboardingService.redirectBasedOnStatus()` from `auth-callback.ts` (both in the success path and the already-authenticated fallback path)

## 2. Welcome Page Simplification

- [x] 2.1 Simplify `welcome-page.ts` `canLoad` to redirect authenticated users directly to `/dashboard` without calling `onboardingService.getRedirectTarget()`
- [x] 2.2 Remove `IOnboardingService` dependency from `welcome-page.ts`

## 3. OnboardingService Cleanup

- [x] 3.1 Remove `hasCompletedOnboarding()` method from `onboarding-service.ts`
- [x] 3.2 Remove `getRedirectTarget()` method from `onboarding-service.ts`
- [x] 3.3 Simplify `redirectBasedOnStatus()` to always navigate to `/dashboard` (or remove if no longer called)
- [x] 3.4 Remove `IArtistService` dependency from `OnboardingService` if no longer used

## 4. Dead Code Removal

- [x] 4.1 Remove `ONBOARDING_COMPLETE_KEY` constant and `localStorage.setItem` call from `artist-discovery-page.ts`

## 5. Tests

- [x] 5.1 Update `onboarding-service.spec.ts` tests to reflect removed methods and simplified behavior
- [x] 5.2 Verify existing auth-callback and welcome-page tests pass (update if needed)
- [x] 5.3 Run full frontend test suite and fix any failures
