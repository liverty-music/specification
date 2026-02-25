## Why

The current onboarding flow requires users to sign up via Zitadel before experiencing any app value. This creates a high-friction entry point where users must commit to account creation before understanding what the product offers. By deferring sign-up to the end of a guided tutorial, users experience the core value proposition (personalized live event discovery, artist following, passion level customization) before being asked to register. This reduces initial drop-off and increases conversion quality because users who do sign up have already demonstrated engagement.

## What Changes

- **Replace upfront authentication with a linear tutorial mode**: New users proceed through a guided, step-locked onboarding flow (Artist Discovery → Dashboard reveal → Concert detail → My Artists → Passion Level) without authentication. Sign-up occurs only at the final step after the user has experienced the product.
- **Introduce `onboardingStep` state management**: Replace the boolean `isOnboarding` concept with a numeric step tracker (0-6, COMPLETED) persisted in LocalStorage, enabling tutorial interruption and resumption across sessions.
- **Add coach mark / spotlight overlay system**: Each tutorial step highlights a single interactive element (card, tab, toggle) and locks all other interactions, guiding users through a linear path.
- **Add sign-up modal at tutorial completion**: A non-dismissible Passkey authentication modal appears after the user sets their first Passion Level, triggering account creation and local-to-server data merge.
- **Add secondary [Login] link on Landing Page**: Existing users on new devices or with expired tokens can bypass the tutorial entirely via a secondary login link.
- **Guest data merge on authentication**: LocalStorage guest data (followed artists, passion levels, region selection) is synced to the backend upon successful Passkey authentication.
- **`isAuthenticated = true` overrides all tutorial restrictions**: Regardless of `onboardingStep` value, an authenticated user always gets full unrestricted access. This handles multi-device scenarios where a new device has no onboarding history.

## Capabilities

### New Capabilities
- `onboarding-tutorial`: Linear tutorial mode with step-locked progression (Steps 0-6), coach mark overlays, spotlight UI, and interaction restrictions per step.
- `guest-data-merge`: Sync locally stored guest session data (followed artists, passion levels, region) to backend APIs upon successful authentication.

### Modified Capabilities
- `frontend-onboarding-flow`: Remove upfront authentication requirement. Artist Discovery, Loading, and Dashboard are now accessed in guest mode during the tutorial. Region selection moves to Dashboard loading phase (Step 3).
- `frontend-route-guard`: Add onboarding step awareness. Routes during tutorial are unlocked sequentially by `onboardingStep` value. `isAuthenticated = true` bypasses all tutorial restrictions regardless of step.
- `user-auth`: Remove "Sign Up" / "Sign In" buttons from LP. Replace with `[Get Started]` primary CTA and `[Login]` secondary link. Authentication is deferred to tutorial Step 6 (Passkey only).
- `landing-page`: CTA changes based on `onboardingStep` and `isAuthenticated` state. New users see `[Get Started]` + `[Login]`; returning unauthenticated users with `COMPLETED` step see `[Login]` only; authenticated users skip LP entirely.
- `user-account-sync`: Extended to handle guest data merge. After Passkey authentication at Step 6, the frontend calls Follow and SetPassionLevel RPCs to persist locally accumulated data.

## Impact

- **Frontend (Aurelia 2)**: Major changes to routing guards, onboarding flow, landing page, dashboard, and My Artists components. New coach mark overlay system. LocalStorage state management for `onboardingStep` and guest data.
- **Backend (Go / Connect-RPC)**: Read-only RPCs (`ArtistService/ListTop`, `ListSimilar`, `Search`, `ConcertService/List`) are added to the `authn-go` public procedure allowlist so onboarding users can access real data without authentication. Existing `UserService.Create`, `ArtistService.Follow`, and `ArtistService.SetPassionLevel` RPCs remain authenticated and are reused for guest data merge.
- **Authentication (Zitadel)**: No IdP changes. Passkey authentication flow remains the same; only the frontend trigger point changes (from LP to tutorial Step 6).
- **Protobuf / API**: No schema changes required. No new RPCs. The public/authenticated distinction is enforced at the HTTP middleware layer, not in the proto definitions.
