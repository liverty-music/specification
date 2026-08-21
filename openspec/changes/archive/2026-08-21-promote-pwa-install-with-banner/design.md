## Context

The app currently has two PWA install affordances:
- `pwa-install-fab` — a 2.75 rem FAB in the bottom-right corner, shown post-onboarding to all users (guest + authenticated). Dismissed permanently by tapping and completing the native dialog; iOS uses an instruction bottom-sheet with a close-only button.
- `PostSignupDialog` — a bottom-sheet shown once after new account creation. Contains an inline install row for Chrome/Edge only (iOS is excluded via `canShowInstallOption`).

`PwaInstallService` currently exposes:
- `@observable canShowFab` — requires `beforeinstallprompt` captured AND onboarding completed (or iOS)
- `canShowInstallOption` — requires `!installed && browserSupportsPwa` (excludes iOS)
- `isIos`, `browserSupportsPwa` — stable getters

The `signup-prompt-banner` component provides the proven visual pattern (see spec). It is auth-state-exclusive with the new banner: guests see `signup-prompt-banner`, authenticated users see `pwa-install-banner`.

See proposal.md for motivation.

## Goals / Non-Goals

**Goals**:
- Single install CTA replacing the FAB for all post-signup scenarios
- iOS users included in the banner flow via guide sheet
- Session-level dismiss that does not permanently suppress the banner
- Reactively switches between native and guide CTA modes

**Non-Goals**:
- Analytics/tracking of install conversion (deferred)
- Changes to `PostSignupDialog` install row logic (unchanged)
- Notification prompt UI changes (unchanged)

## Decisions

### D1: `shouldShowInstallBanner` as `@observable` property (not a getter)

`PwaInstallService.installed` is a private, non-observable field. A plain getter derived from it will not trigger Aurelia's template re-evaluation when `installed` changes (via `appinstalled` or `confirmInstalled()`). Making `shouldShowInstallBanner` an `@observable` property — updated explicitly in `evaluateVisibility()`, `listenForAppInstalled()`, and `confirmInstalled()` — ensures templates react correctly.

Alternative considered: make `installed` observable. Rejected because `installed` is internal state; exposing it as observable widens the API surface unnecessarily and risks misuse by other components.

### D2: `if.bind` over `show.bind` for the banner element

The banner contains two interactive elements (CTA + close button). Using `show.bind` (DOM kept but hidden) would require `aria-hidden` and `tabindex` management on each child — the same complexity the FAB manages for a single button. Since the banner should disappear entirely when hidden (no a11y reason to keep it in the tree), `if.bind` is simpler and correct: removes both buttons from the tab order automatically.

Alternative considered: `show.bind` + explicit `aria-hidden`/`tabindex` per child, matching the FAB pattern. Rejected because the multi-child case adds brittleness without benefit.

### D3: Session-level dismiss via `sessionStorage` (not `localStorage`)

`localStorage` dismiss would permanently suppress the banner for users who tapped close on impulse but still intend to install later. `sessionStorage` clears on tab close / new session, so the banner naturally re-surfaces — persistent pressure without being permanently dismissible.

### D4: Reuse `signup-prompt-banner` visual language (no new design tokens)

The banner uses existing design tokens (`--color-brand-primary`, `--color-brand-secondary`, `--space-*`, `--step-*`) and the same CSS structure (`@layer block { @scope (pwa-install-banner) { ... } }`). This keeps the two banners visually consistent without introducing a shared base component, which would require a new abstraction for two consumers.

### D5: Banner is auth-gated (`shouldShowInstallBanner` checked at app-shell level alongside `isAuthenticated`)

Guests already see `signup-prompt-banner`. Showing `pwa-install-banner` to guests too would stack two banners. The auth gate (`if.bind="showNav && isAuthenticated"` at the app-shell level, or equivalent) ensures mutual exclusivity.

### D6: `confirmInstalled()` as explicit iOS completion signal

iOS's `appinstalled` event is unreliable (fired inconsistently across iOS versions). A "追加しました" button in the guide sheet lets the user signal completion, which `confirmInstalled()` records to `localStorage['pwa.installed']` and sets `shouldShowInstallBanner = false`. On the next standalone launch, `detectInstalled()` will confirm via `navigator.standalone`, providing a second verification layer.

### D7: Banner suppressed (not co-rendered) while PostSignupDialog is open

Both are `position: fixed` at the bottom. Co-rendering them would cause visual overlap. The host (`DashboardRoute` or `app-shell`) suppresses the banner while `showPostSignupDialog` is true — the same mechanism used to suppress the notification prompt. The banner becomes visible after the dialog is dismissed.

## Risks / Trade-offs

- **iOS `appinstalled` never fires** → Mitigated by `confirmInstalled()` in guide sheet. On next standalone launch, `detectInstalled()` auto-detects via `navigator.standalone`.
- **`beforeinstallprompt` arrives after banner renders** → Handled by `@watch((vm) => vm.pwaInstall.canShowFab)` in the banner VM, same pattern as `PostSignupDialog`. CTA mode upgrades reactively without needing to re-mount the banner.
- **Session dismiss state lost if tab crashes** → Acceptable; the banner simply reappears. Worst case is a slightly more frequent appearance in crash-heavy sessions.

## Migration Plan

1. Add `shouldShowInstallBanner` and `confirmInstalled()` to `PwaInstallService` (additive — no existing callers affected).
2. Implement `pwa-install-banner` component.
3. Swap `<pwa-install-fab>` for `<pwa-install-banner>` in `app-shell.html`.
4. Delete `pwa-install-fab` component files.
5. Add i18n keys (`pwaInstallBanner.*`) to both locale files.
6. Update `PostSignupDialog` spec reference (iOS path → banner).
7. No rollback needed — the FAB component files are deleted, not gated. If rollback is required, restore from git.

## Open Questions

None — all scope questions resolved during the explore phase.
