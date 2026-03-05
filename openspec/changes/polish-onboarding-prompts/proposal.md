## Why

The PWA install banner, notification prompt, and sign-up modal all lack entrance/exit animations, appearing and disappearing instantly. This is inconsistent with the rest of the onboarding flow, which uses spring easing (800ms cubic-bezier), staggered fade-slide-up, and layered effects. The contrast makes prompts feel mechanical and disruptive. Additionally, the PWA banner has hardcoded English text (no i18n), and the Step 5 Passion Level explanation has a 3-second silent delay before appearing.

## What Changes

- Add `fade-slide-up` entrance and `fade-slide-down` exit animations to `notification-prompt` and `pwa-install-prompt` components, matching the design system's spring easing
- Enhance the sign-up modal (Step 6) with a scale+fade entrance animation and a subtle background glow, matching the visual polish of the Discover HUD
- Localize all PWA install banner text via i18n keys (`pwa.title`, `pwa.description`, `pwa.install`, `pwa.notNow`)
- Replace the Step 5 Passion Level explanation's 3-second `setTimeout` with immediate visual feedback (e.g., brief highlight on the changed passion level) followed by the explanation modal after 800ms

## Capabilities

### New Capabilities

### Modified Capabilities

- `app-shell-layout`: PWA install prompt text becomes i18n-aware; entrance/exit animations added
- `onboarding-tutorial`: Step 5 passion explanation timing changes from 3s delay to immediate feedback + 800ms delay

## Impact

- `frontend/src/components/notification-prompt/notification-prompt.html` — Add animation classes
- `frontend/src/components/pwa-install-prompt/pwa-install-prompt.html` — Add animation classes, replace hardcoded text with i18n keys
- `frontend/src/components/signup-modal/signup-modal.html` — Add entrance animation
- `frontend/src/routes/my-artists/my-artists-page.ts` — Change passion explanation delay from 3000ms to 800ms
- `frontend/src/locales/` — Add PWA i18n keys for all supported languages
