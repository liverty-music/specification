## 1. ListByUser 401 Error Fix

- [x] 1.1 Inject `IAuthService` into `DashboardService` and add `isAuthenticated` check in `fetchJourneyMap()` (return empty Map immediately when unauthenticated)
- [x] 1.2 Change `TicketJourneyRpcClient` field initialization to constructor pattern, unifying on `createClient` + `Client` type

## 2. Bottom Sheet Display Timing Fix

- [x] 2.1 `bottom-sheet.ts` — defer `scrollTo()` in `openChanged()` by one frame using `requestAnimationFrame`

## 3. Coach Mark View Transition Error Fix

- [x] 3.1 Add `this.onboarding.deactivateSpotlight()` to `detaching()` in `dashboard-route.ts`
- [x] 3.2 Remove `router.load('my-artists')` from `onOnboardingMyArtistsTapped()`, keep only `setStep()` (`currentTarget.click()` → Aurelia Router `useHref` intercept handles navigation)

## 4. Verification

- [x] 4.1 Confirm lint and tests pass with `make check` (TS error in user-client.ts is pre-existing)
- [x] 4.2 Visually verify bottom-sheet layout in browser
- [x] 4.3 End-to-end manual verification of onboarding flow in dev environment (guest user: Welcome → Discovery → Dashboard → Home Selector → Coach Marks → My Artists)
- [x] 4.4 Confirm `currentTarget.click()` programmatic click correctly fires Aurelia Router's `useHref` intercept (verified detail → my-artists step transition via coach mark card tap)
