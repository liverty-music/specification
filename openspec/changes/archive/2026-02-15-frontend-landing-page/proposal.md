## Why

The current frontend has a generic welcome page placeholder with no value proposition or authentication integration. New users need a landing page that communicates the core service promise ("Never miss your favorite artist's live show again") and provides frictionless Passkey authentication via Zitadel, serving as the entry point to the onboarding flow.

## What Changes

- Replace the existing `WelcomePage` with a purpose-built Landing Page component that presents the hero copy and a Sign Up / Sign In CTA.
- Integrate the existing `auth-service` to trigger the Zitadel OIDC flow (Passkey authentication) from the CTA button.
- Implement post-authentication routing: redirect authenticated users to the Artist Discovery step (or Dashboard if onboarding is already complete).
- Add mobile-first responsive styling optimized for smartphone portrait mode.

## Capabilities

### New Capabilities
- `landing-page`: The first-view landing page UI component, hero messaging, and CTA-to-auth integration.

### Modified Capabilities
- `user-auth`: Add routing logic for post-authentication redirect to onboarding flow (Artist Discovery) vs. returning user redirect to Dashboard.
- `frontend-onboarding-flow`: Update the overall flow to formally define the Landing Page as Step 1 entry point.

## Impact

- **Frontend**: New landing page component replaces `WelcomePage`. Route configuration updates for onboarding flow entry.
- **Auth**: Post-login redirect logic changes (callback route needs to check onboarding completion status).
- **No backend changes**: All authentication infrastructure (Zitadel, JWT validation) already exists.
