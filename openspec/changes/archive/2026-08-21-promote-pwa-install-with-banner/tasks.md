## 1. PwaInstallService — Extend API

- [x] 1.1 Add `@observable public shouldShowInstallBanner = false` property to `PwaInstallService`
- [x] 1.2 Add `private updateBannerVisibility()` helper that sets `shouldShowInstallBanner = !this.installed && (this.browserSupportsPwa || this.isIos)`
- [x] 1.3 Call `updateBannerVisibility()` in `evaluateVisibility()` (after the existing `canShowFab` update)
- [x] 1.4 Call `shouldShowInstallBanner = false` in `listenForAppInstalled()` handler (alongside existing `canShowFab = false`)
- [x] 1.5 Add `public confirmInstalled()` method: set `this.installed = true`, write `localStorage['pwa.installed'] = 'true'`, set `this.canShowFab = false`, set `this.shouldShowInstallBanner = false`
- [x] 1.6 Update `PwaInstallService` unit tests (`pwa-install-service.spec.ts`) to cover `shouldShowInstallBanner` reactive updates and `confirmInstalled()`

## 2. pwa-install-banner Component — Scaffold

- [x] 2.1 Create `src/components/pwa-install-banner/pwa-install-banner.ts` (Aurelia 2 convention-based component)
- [x] 2.2 Create `src/components/pwa-install-banner/pwa-install-banner.html` (template)
- [x] 2.3 Create `src/components/pwa-install-banner/pwa-install-banner.css` (`@layer block { @scope (pwa-install-banner) { ... } }`)

## 3. pwa-install-banner Component — ViewModel

- [x] 3.1 Inject `IPwaInstallService` via `resolve()`; read `shouldShowInstallBanner`, `canShowFab`, `isIos`
- [x] 3.2 Add `@observable dismissed = false`; read initial value from `sessionStorage` in `binding()` lifecycle hook
- [x] 3.3 Add `@watch((vm) => vm.pwaInstall.canShowFab)` watcher to reactively sync `installMode` (`'native' | 'guide'`) — same pattern as `PostSignupDialog.canShowFabChanged()`
- [x] 3.4 Add `dismiss()` method: set `this.dismissed = true` and write to `sessionStorage`
- [x] 3.5 Add `onInstall()` method: call `pwaInstall.install()` when in native mode (use `busy-on-click`)
- [x] 3.6 Add `isGuideSheetOpen = false` property; guide sheet opens when CTA is tapped in guide mode
- [x] 3.7 Add `onConfirmInstalled()` method: call `pwaInstall.confirmInstalled()`, close guide sheet
- [x] 3.8 Expose `get isVisible(): boolean` = `pwaInstall.shouldShowInstallBanner && !dismissed` (used by host for `if.bind`)

## 4. pwa-install-banner Component — Template

- [x] 4.1 Root `<aside>` with `if.bind="isVisible"` and `aria-label` bound to i18n key
- [x] 4.2 Label paragraph bound to `pwaInstallBanner.label` i18n key
- [x] 4.3 CTA `<button>` with `busy-on-click.bind="() => onCta()"` and label `pwaInstallBanner.cta`; `onCta()` calls `onInstall()` in native mode or opens guide sheet in guide mode
- [x] 4.4 Close `<button>` with `click.trigger="dismiss()"`, `aria-label` bound to `pwaInstallBanner.close` i18n key
- [x] 4.5 `<bottom-sheet>` for guide sheet: `open.bind="isGuideSheetOpen"`, `sheet-closed.trigger="isGuideSheetOpen = false"`; contains platform-appropriate step list and a "追加しました" confirm button

## 5. pwa-install-banner Component — CSS

- [x] 5.1 Fixed position: `inset-block-end: calc(3.5rem + env(safe-area-inset-bottom, 0px))`, `inset-inline: 0`
- [x] 5.2 Frosted glass background: `oklch(18% 0.04 275deg / 85%)` + `backdrop-filter: blur(12px)`
- [x] 5.3 Gradient top border: `border-block-start: 2px solid; border-image: linear-gradient(to right, var(--color-brand-primary), var(--color-brand-secondary)) 1`
- [x] 5.4 Slide-up entrance animation (400ms ease-out, `translateY(100%) → translateY(0)`) under `@media (prefers-reduced-motion: no-preference)`
- [x] 5.5 CTA button pulsing glow (`cta-glow` keyframes, 2.5s ease-in-out infinite) under `@media (prefers-reduced-motion: no-preference)`
- [x] 5.6 Close button: subtle icon or text, positioned in top-right corner with adequate touch target (min 44px)

## 6. i18n Keys

- [x] 6.1 Add `pwaInstallBanner.*` keys to `src/locales/en/translation.json`: `label`, `cta`, `close`, `guideTitle`, `guideStep1`, `guideStep2`, `guideStep3`, `guideConfirm`
- [x] 6.2 Add `pwaInstallBanner.*` keys to `src/locales/ja/translation.json` with Japanese text
- [x] 6.3 iOS-specific guide step keys (Share button → ホーム画面に追加 flow) for `ja` locale
- [x] 6.4 Chrome-specific guide step keys (⋮ menu → ホーム画面に追加 flow) for `ja` locale; ensure EN parity

## 7. App Shell — Swap Component

- [x] 7.1 Remove `<import from="./components/pwa-install-fab/pwa-install-fab">` from `app-shell.html`
- [x] 7.2 Add `<import from="./components/pwa-install-banner/pwa-install-banner">` to `app-shell.html`
- [x] 7.3 Replace `<pwa-install-fab if.bind="showNav">` with `<pwa-install-banner if.bind="showNav && isAuthenticated">` (auth gate per D5 in design)
- [x] 7.4 Suppress banner while PostSignupDialog is open: pass or derive a suppression condition so the banner is hidden when `showPostSignupDialog` is `true` (e.g., `if.bind="showNav && isAuthenticated && !showPostSignupDialog"`)

## 8. Delete pwa-install-fab Component

- [x] 8.1 Delete `src/components/pwa-install-fab/pwa-install-fab.ts`
- [x] 8.2 Delete `src/components/pwa-install-fab/pwa-install-fab.html`
- [x] 8.3 Delete `src/components/pwa-install-fab/pwa-install-fab.css`
- [x] 8.4 Delete `src/components/pwa-install-fab/pwa-install-fab.spec.ts`
- [x] 8.5 Search codebase for any remaining `pwa-install-fab` references and remove them

## 9. Tests

- [x] 9.1 Write unit tests for `pwa-install-banner` VM: session dismiss initialisation in `binding()`, `dismiss()` writes to `sessionStorage`, `isVisible` computed correctly, `@watch` on `canShowFab` switches `installMode`
- [x] 9.2 Test `confirmInstalled()` path: guide sheet confirm → `pwaInstall.confirmInstalled()` called → `isGuideSheetOpen` closes
- [x] 9.3 Verify `make check` passes (TypeScript, CSS lint, unit tests)

## 10. Ship to Prod

- [x] 10.1 Open frontend PR, confirm CI green
- [x] 10.2 Merge PR and create GitHub Release (v1.56.0) to trigger prod deploy
- [x] 10.3 Verify in prod: banner appears on a signed-in, non-installed Chrome session; native install dialog triggers; banner disappears after install
- [x] 10.4 Verify in prod: iOS Safari session shows banner with guide sheet; "追加しました" closes banner
