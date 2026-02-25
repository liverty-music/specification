## 1. Onboarding State Management

- [x] 1.1 Create `OnboardingService` (Aurelia singleton) that reads/writes `liverty:onboardingStep` from LocalStorage and exposes reactive `currentStep` property
- [x] 1.2 Define `OnboardingStep` enum/constants (0-6, COMPLETED=7) with step-to-route mapping
- [x] 1.3 Add invalid value handling: reset to 0 if `liverty:onboardingStep` is corrupted or out of range

## 2. Local Client (LocalStorage-backed)

- [x] 2.1 Create `GuestDataService` (Aurelia singleton) that manages `liverty:guest:followedArtists` (JSON array of artist ID + name + passion level) in LocalStorage
- [x] 2.2 Add `liverty:guest:region` storage for region selection during onboarding
- [x] 2.3 Add cleanup method to clear all `liverty:guest:*` keys
- [x] 2.4 Rename `GuestDataService` to `LocalArtistClient` with RPC-matching method names (`follow`, `unfollow`, `listFollowed`, `setPassionLevel`)
- [x] 2.5 Rename `isInTutorial` / `isInOnboarding` checks throughout codebase to `isOnboarding` for consistency

## 3. Route Guard Modifications

- [x] 3.1 Update `AuthHook.canLoad()` to check `isAuthenticated` first (highest priority — bypasses all tutorial restrictions)
- [x] 3.2 Add `onboardingStep` awareness: allow tutorial routes when step matches, redirect otherwise
- [x] 3.3 Add `tutorialStep` route metadata (`data: { auth: false, tutorialStep: N }`) to onboarding routes
- [x] 3.4 Make `/dashboard` and `/my-artists` accessible without auth when `onboardingStep` matches their tutorial step (3 and 5 respectively)

## 4. Landing Page Changes

- [x] 4.1 Replace "Sign Up" / "Sign In" buttons with primary [Get Started] CTA and secondary [Login] text link
- [x] 4.2 Implement CTA branching logic: show [Get Started] + [Login] for new users, [Login] only for `onboardingStep = COMPLETED`
- [x] 4.3 Add `isAuthenticated = true` redirect: skip LP entirely, navigate to Dashboard
- [x] 4.4 Handle `onboardingStep = 6`: immediately display SignUp modal instead of LP content

## 5. Coach Mark Overlay Component

- [x] 5.1 Create `<coach-mark>` custom element with spotlight overlay (dimmed background + highlight cutout around target element)
- [x] 5.2 Add tooltip rendering with configurable message text and position
- [x] 5.3 Implement interaction lock: only the highlighted element accepts tap/click, all others blocked by overlay
- [x] 5.4 Add target element retry logic with exponential backoff (up to 5s) when target is not in DOM

## 6. Tutorial Step Screens

- [x] 6.1 Step 1 (Artist Discovery): Add progress bar (0/3), store follows in `GuestDataService` instead of backend RPC, show [Generate Dashboard] CTA at 3+ follows
- [x] 6.2 Step 2 (Loading): Trigger loading animation, auto-advance to Step 3 on completion
- [x] 6.3 Step 3 (Dashboard): Display region selection BottomSheet, disable scroll, apply spotlight to first concert card with coach mark
- [x] 6.4 Step 4 (Detail BottomSheet): Prevent BottomSheet dismissal, highlight [My Artists] tab with coach mark
- [x] 6.5 Step 5 (My Artists): Highlight first artist's Passion Level toggle with coach mark, show notification control explanation after toggle change
- [x] 6.6 Step 6 (SignUp Modal): Display non-dismissible Passkey auth modal, re-display on page reload

## 7. Guest Data Merge

- [x] 7.1 Implement merge sequence after Passkey auth: `UserService.Create` → `ArtistService.Follow` × N → `ArtistService.SetPassionLevel` × N
- [x] 7.2 Handle `ALREADY_EXISTS` from `UserService.Create` as success
- [x] 7.3 Implement best-effort follow calls: log and continue on individual failures
- [x] 7.4 Add loading indicator during merge, set `onboardingStep = COMPLETED` on completion, clear guest data

## 8. User Auth Flow Updates

- [x] 8.1 Update OIDC callback handler to detect tutorial-originated registration (Step 6) and trigger guest data merge
- [x] 8.2 Update OIDC callback handler for [Login] link flow: redirect to Dashboard without merge
- [x] 8.3 Remove `state.isRegistration` logic, replace with `onboardingStep`-based detection

## 9. Backend Public Endpoint Allowlist

- [x] 9.1 Add `publicProcedures` parameter to `NewAuthFunc` in `internal/infrastructure/auth/authn.go`: check `req.URL.Path` against the set; if public and no token, return `nil, nil`; if public and token present, validate normally
- [x] 9.2 Define allowlist in `internal/di/provider.go`: `ArtistService/ListTop`, `ArtistService/ListSimilar`, `ArtistService/Search`, `ConcertService/List`
- [x] 9.3 Update `authn_test.go`: add test cases for public procedure without token (pass), public procedure with valid token (pass with claims), public procedure with invalid token (pass without claims), protected procedure without token (reject)

## 10. Frontend Service Client Onboarding Abstraction

- [x] 10.1 Extend `ArtistServiceClient` to check `OnboardingService.isOnboarding` before write RPCs: `follow()` → `LocalArtistClient.follow()`, `unfollow()` → `LocalArtistClient.unfollow()`; read RPCs (`listTop`, `listSimilar`, `search`) pass through to backend (public)
- [x] 10.2 Add `listFollowed()` method to `ArtistServiceClient`: during onboarding, read from `LocalArtistClient.listFollowed()`; otherwise call `ArtistService/ListFollowed` RPC
- [x] 10.3 Extend `ConcertServiceClient` to check `OnboardingService.isOnboarding` in `listByFollower()`: during onboarding, read artist IDs from `LocalArtistClient.listFollowed()` and call `ConcertService/List` per artist (public RPC), merging results; otherwise call `ConcertService/ListByFollower` RPC
- [x] 10.4 Remove `if (isInTutorial)` branching from `ArtistDiscoveryPage.onArtistSelected()` — the service client handles the split transparently

## 11. Onboarding UI Restrictions

- [x] 11.1 Disable `SetPassionLevel` interaction during onboarding in My Artists page: coach mark demonstrates the concept visually without invoking any service method or persisting a level change
- [x] 11.2 Block `Unfollow` interaction (swipe-to-unfollow, long-press) during onboarding in My Artists page
- [x] 11.3 Update `createAuthRetryInterceptor` in `connect-error-router.ts`: when `auth.user` is null (guest/onboarding), skip silent refresh and hard redirect, propagate error to caller
