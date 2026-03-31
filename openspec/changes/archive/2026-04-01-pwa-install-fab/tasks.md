## 1. PwaInstallService Refactor

- [x] 1.1 Remove `dismiss()` method and `StorageKeys.pwaInstallPromptDismissed` read/write from `PwaInstallService`
- [x] 1.2 Remove `incrementSessionCount()`, `persistCompletedSessionCountIfNeeded()`, and related session-count logic from `PwaInstallService`
- [x] 1.3 Remove `auth.isAuthenticated` gate from `evaluateVisibility()`
- [x] 1.4 Remove `promptCoordinator.canShowPrompt('pwa-install')` gate and `markShown('pwa-install')` call from `evaluateVisibility()`
- [x] 1.5 Add `appinstalled` event listener in `PwaInstallService` constructor; on fire set `canShow = false` and persist installed state to localStorage (`StorageKeys.pwaInstalled`)
- [x] 1.6 Add installed-state check on init: if `StorageKeys.pwaInstalled === 'true'` or `navigator.standalone === true` or `matchMedia('(display-mode: standalone)').matches`, set `canShow = false` permanently
- [x] 1.7 Add iOS detection property `get isIos(): boolean` using `!('BeforeInstallPromptEvent' in window)` combined with userAgent check for Safari
- [x] 1.8 Expose `canShowFab` as the public observable (rename from `canShow` or alias); `canShowFab` is `true` when `onboarding.isCompleted && !installed && (deferredPrompt !== null || isIos)`
- [x] 1.9 Update unit tests for `PwaInstallService` to cover new eligibility logic

## 2. pwa-install-fab Component

- [x] 2.1 Create `src/components/pwa-install-fab/pwa-install-fab.ts` — inject `IPwaInstallService`; expose `isVisible`, `isIos`, `isSheetOpen`; implement `handleTap()` (branch on `isIos`), `handleInstall()`, `closeSheet()`
- [x] 2.2 Create `src/components/pwa-install-fab/pwa-install-fab.html` — FAB button with download SVG icon; conditional `<bottom-sheet>` for iOS instructions (3-step list + 閉じる button)
- [x] 2.3 Create `src/components/pwa-install-fab/pwa-install-fab.css` — `position: fixed`, `inset-inline-end: var(--space-s)`, `inset-block-end: calc(3.5rem + env(safe-area-inset-bottom, 0px) + var(--space-s))`; brand gradient `box-shadow` glow; entry animation (`slide-up` + `ripple-pulse` 2 iterations); tap `scale(0.92)` feedback; `prefers-reduced-motion` fallback to fade
- [x] 2.4 Add i18n keys for FAB aria-label and iOS instruction sheet content (ja + en)
- [x] 2.5 Write unit tests for `pwa-install-fab` component (visibility binding, tap routing by platform, sheet open/close)

## 3. App Shell Integration

- [x] 3.1 Add `<import from="./components/pwa-install-fab/pwa-install-fab">` to `app-shell.html`
- [x] 3.2 Mount `<pwa-install-fab if.bind="showNav"></pwa-install-fab>` in `app-shell.html` alongside existing overlays
- [x] 3.3 Add `pwa-install-fab` to the `position: fixed; block-size: 0` overlay rule in `app-shell.css` to keep it out of the grid flow

## 4. Retire pwa-install-prompt Toast

- [x] 4.1 Remove `<pwa-install-prompt if.bind="showNav">` from `app-shell.html`
- [x] 4.2 Remove `<import>` for `pwa-install-prompt` from `app-shell.html`
- [x] 4.3 Delete `src/components/pwa-install-prompt/` directory (component + tests)
- [x] 4.4 Remove `pwa-install-prompt` from `app-shell.css` overlay rule
- [x] 4.5 Remove `StorageKeys.pwaSessionCount` and `StorageKeys.pwaCompletedSessionCount` from `storage-keys.ts`

## 5. PostSignupDialog Update

- [x] 5.1 Update `PostSignupDialog.canInstallPwa` getter to use `pwaInstall.canShowFab` (rename if needed)
- [x] 5.2 Update `PostSignupDialog.activeChanged()` to no longer call `promptCoordinator.markShown('pwa-install')` — FAB is not suppressed by dialog dismissal
- [x] 5.3 Verify iOS case: on iOS, `canShowFab` is `true` (no `deferredPrompt` needed), so `onInstallPwa()` in the dialog should either open the iOS sheet or be hidden — update dialog logic accordingly
- [x] 5.4 Update `PostSignupDialog` unit tests

## 6. Cleanup

- [x] 6.1 Remove `StorageKeys.pwaInstallPromptDismissed` from `storage-keys.ts`
- [x] 6.2 Search codebase for any remaining references to removed storage keys and clean up
- [x] 6.3 Run `make check` and fix any lint/type errors
