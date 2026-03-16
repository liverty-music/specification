## 1. OnboardingStep string values

- [x] 1.1 Change `OnboardingStep` values from numbers to strings (`'lp'`, `'discovery'`, `'dashboard'`, `'detail'`, `'my-artists'`, `'completed'`), rename `DISCOVER` → `DISCOVERY`, remove `LOADING` and `SIGNUP`
- [x] 1.2 Add `STEP_ORDER` array and `stepIndex()` function for ordinal comparison
- [x] 1.3 Add `ONBOARDING_STEPS` Set and update `isOnboarding` to use Set membership
- [x] 1.4 Update `STEP_ROUTE_MAP` to remove `LOADING`/`SIGNUP` entries
- [x] 1.5 Update `loadPersistedState()` to validate string step values, remove numeric/legacy backward compat

## 2. Rename `guestArtists` → `guest`

- [x] 2.1 Rename `GuestArtistsState` → `GuestState` and `AppState.guestArtists` → `AppState.guest` in `app-state.ts`
- [x] 2.2 Update `reducer.ts` — all `state.guestArtists` → `state.guest`
- [x] 2.3 Update `middleware.ts` — persistence reads from `state.guest`
- [x] 2.4 Update `loadPersistedState()` — hydrates into `guest` key
- [x] 2.5 Update services (`local-artist-client.ts`, `guest-data-merge-service.ts`, `follow-service-client.ts`, `concert-service.ts`) — all `getState().guestArtists` → `getState().guest`
- [x] 2.6 Update routes (`discovery-route.ts`, `auth-callback-route.ts`, `dashboard-route.ts`) — all `getState().guestArtists` → `getState().guest`
- [x] 2.7 Update test files (`mock-store.ts`, `reducer.spec.ts`, `middleware.spec.ts`, `discovery-route.spec.ts`) — all `guestArtists` → `guest`

## 3. Rename `tutorial` → `onboarding`

- [x] 3.1 Rename route data `tutorialStep` → `onboardingStep` in `app-shell.ts`
- [x] 3.2 Update `auth-hook.ts` — rename `tutorialStep` variable, update comments, use `stepIndex()` comparison
- [x] 3.3 Rename getters in `dashboard-route.ts` — `isTutorialStep3` → `isOnboardingStepDashboard`, `isTutorialStep4` → `isOnboardingStepDetail`
- [x] 3.4 Rename methods in `dashboard-route.ts` — `onTutorialCardTapped` → `onOnboardingCardTapped`, `onTutorialMyArtistsTapped` → `onOnboardingMyArtistsTapped`
- [x] 3.5 Rename getter in `my-artists-route.ts` — `isTutorialStep5` → `isOnboardingStepMyArtists`, update comments
- [x] 3.6 Rename variable in `auth-callback-route.ts` — `isTutorialSignup` → `isOnboardingSignup`
- [x] 3.7 Update `coach-mark.html` — `aria-label="Tutorial tip"` → `"Onboarding tip"`
- [x] 3.8 Update comments and log messages in `onboarding-service.ts`, `welcome-route.ts`, `discovery-route.ts`, `connect-error-router.ts`, `auth-service.ts`
- [x] 3.9 Update i18n `translation.json` — "completing the tutorial" → "completing onboarding"
- [x] 3.10 Update test files with renamed getters/methods/variables

## 4. Logger middleware refactor

- [x] 4.1 Create `createLoggingMiddleware(logger: ILogger)` factory in `middleware.ts`, remove standalone `loggingMiddleware`
- [x] 4.2 Update `main.ts` — create logger-scoped middleware via factory, conditionally register with `import.meta.env.DEV` guard
- [x] 4.3 Update middleware unit tests

## 5. State transition diagram

- [x] 5.1 Create mermaid onboarding state machine diagram in `openspec/specs/state-transition-diagram/spec.md`
- [x] 5.2 Create mermaid guest state machine diagram in same file

## 6. Edge-case unit tests

- [x] 6.1 Test `onboarding/advance` to same step (no-op returns new object)
- [x] 6.2 Test `guest/unfollow` for non-existent artist (returns state with empty filter result)
- [x] 6.3 Test `guest/setUserHome` overwrite (replaces existing home)
- [x] 6.4 Test `guest/clearAll` on already-empty state
- [x] 6.5 Test spotlight state preserved across `onboarding/advance`
- [x] 6.6 Test `onboarding/complete` from non-onboarding state (LP)

## 7. Cleanup

- [x] 7.1 Remove unused `ILocalArtistClient` registration from `main.ts`
- [x] 7.2 Run full lint and test suite (`make check`)
