## Why

The welcome page currently switches between "Get Started" and "Log In" based on `onboardingStep` stored in localStorage. This creates UX problems: returning users on a new device or after clearing browser data see "Get Started" instead of "Log In"; users who completed onboarding but abandoned OAuth signup see only "Log In" with no path back to onboarding; and the `<a>` login link lacks `href`/`tabindex`, breaking keyboard navigation and screen reader access. Additionally, `onboarding.complete()` is called redundantly in two places, and the `handleGetStarted()` method unnecessarily clears guest artist data.

## What Changes

- **Always show both CTAs**: Remove the `showGetStarted` conditional toggle. Display "Get Started" (primary) and "Log In" (secondary) buttons on every visit, regardless of localStorage state.
- **Both CTAs as `<button>` elements**: Replace the secondary `<a>` login link with a styled `<button>`, fixing the accessibility gap and making the two actions visually parallel.
- **Consolidate `onboarding.complete()`**: Remove the redundant call in `auth-callback-route.ts`; keep only the one in `guest-data-merge-service.ts` at the end of the merge flow.
- **Stop clearing guest data on "Get Started"**: Remove `guest/clearAll` dispatch from `handleGetStarted()`, preserving previously followed artists when re-entering onboarding.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `landing-page`: Remove conditional CTA switching; always render both "Get Started" and "Log In" buttons. Remove the "completed user sees Login only" scenario.

## Impact

- **Frontend** (`frontend/`):
  - `src/routes/welcome/welcome-route.ts` — Remove `showGetStarted` getter, remove `guest/clearAll` dispatch
  - `src/routes/welcome/welcome-route.html` — Remove `if.bind` conditionals, add secondary button
  - `src/routes/welcome/welcome-route.css` — Add `.welcome-btn-secondary` style
  - `src/routes/auth-callback/auth-callback-route.ts` — Remove redundant `onboarding.complete()` call
- **Tests**: Update welcome-route and auth-callback-route unit tests
- **No backend or API changes**
