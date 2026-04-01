## Why

After onboarding completes, users have no persistent, low-friction path to install the PWA. The existing Toast-based install prompt is a one-shot mechanism that fires only for authenticated users on the second session after completion — missing the peak motivation moment and entirely excluding guest users. A persistent FAB on the Nav Bar surface gives every user (guest or authenticated) a discoverable, non-intrusive install entry point from the moment they first experience the app's value.

## What Changes

- Add a `pwa-install-fab` component: a persistent floating action button anchored above the Nav Bar (right side), visible after `OnboardingStep.COMPLETED` for all users regardless of auth state
- On Android/Chrome: tapping the FAB triggers `beforeinstallprompt.prompt()` directly
- On iOS Safari: tapping the FAB opens a `bottom-sheet` with step-by-step "Add to Home Screen" instructions (Safari share icon → "ホーム画面に追加")
- FAB disappears permanently once the app is installed (`appinstalled` event)
- Remove the `dismiss` mechanism from `PwaInstallService` — with a persistent passive FAB, one-shot dismissal is no longer the right model
- Remove auth and session-count gating from PWA install eligibility — replaced by onboarding completion only
- When `signup-prompt-banner` is visible, the FAB overlays the banner's button row (right side), using the horizontal whitespace beside the "アカウント作成" button — no position offset calculation needed
- Entry animation: slide-up on first appearance + 2-pulse ripple ring; idle state: brand gradient glow; tap: scale press feedback

## Capabilities

### New Capabilities

- `pwa-install-fab`: Persistent FAB component for PWA install, post-onboarding, guest and authenticated users; includes iOS instruction sheet

### Modified Capabilities

- `prompt-timing`: Remove auth and session-count requirements for PWA install prompt; onboarding completion is the sole eligibility gate
- `post-signup-dialog`: PWA install row in PostSignupDialog remains, but now relies on `pwa-install-fab` service state rather than the old session-count gate

## Impact

- **Frontend only** — all changes in `frontend/src/`
- Files affected:
  - `src/components/pwa-install-fab/` — new component (FAB + iOS instruction sheet)
  - `src/services/pwa-install-service.ts` — remove dismiss, remove auth/session-count gate, add `appinstalled` listener, expose iOS detection
  - `src/app-shell.html` / `src/app-shell.css` — mount FAB alongside existing overlays
  - `src/components/pwa-install-prompt/` — existing Toast prompt can be retired (or kept as fallback — decision in design)
- No API, backend, proto, or infrastructure changes
