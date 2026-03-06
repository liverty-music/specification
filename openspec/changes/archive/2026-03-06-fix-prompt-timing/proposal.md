## Why

The PWA install banner and push notification prompt appear during onboarding (Step 3 Dashboard) before the user has created an account or completed the tutorial. This disrupts the guided onboarding flow, competes visually with coach marks and the region selector, and asks for permissions before the user has experienced the value of the service. The onboarding was designed to build motivation through Steps 1-5 before requesting sign-up (Step 6) and notification permission (Step 7), but neither prompt checks onboarding or authentication state.

## What Changes

- Add `onboarding.isCompleted` guard to `PwaInstallService.evaluateVisibility()` so the PWA install banner never appears during the tutorial (Steps 1-6)
- Add `authService.isAuthenticated` and `onboarding.isCompleted` guards to `NotificationPrompt` so the push notification prompt only appears after account creation
- Move `<notification-prompt>` from `dashboard.html` (route-level) to `my-app.html` (app shell level), gated by authentication and onboarding completion state
- Introduce a `PromptCoordinator` service to ensure only one prompt (PWA install or notification) is shown per session, preventing simultaneous display
- Show notification prompt on the first session after Step 7 completion (motivation is highest), and PWA install on a subsequent session

## Capabilities

### New Capabilities

- `prompt-timing`: Rules for when PWA install and push notification prompts are eligible to display, including authentication, onboarding, and session-based guards

### Modified Capabilities

- `onboarding-tutorial`: Add requirement that no permission prompts (PWA install, push notification) SHALL appear during onboarding Steps 1-6
- `app-shell-layout`: Notification prompt moves from dashboard route to app shell, gated by auth + onboarding state

## Impact

- `frontend/src/services/pwa-install-service.ts` — Add onboarding dependency and guard
- `frontend/src/components/notification-prompt/notification-prompt.ts` — Add auth + onboarding guards
- `frontend/src/routes/dashboard.html` — Remove `<notification-prompt>` import and usage
- `frontend/src/my-app.html` — Add `<notification-prompt>` with conditional display
- `frontend/src/services/` — New `PromptCoordinator` service for single-prompt-per-session logic
