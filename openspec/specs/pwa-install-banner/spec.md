# PWA Install Banner

## Purpose

Defines a persistent full-width banner that promotes PWA installation to signed-in users, replacing the floating action button. The banner covers both native one-tap install (Chrome/Edge) and manual guided install (iOS Safari), and persists across sessions with a per-session dismiss until the app is installed.

## Requirements

### Requirement: Banner Visible to Authenticated Non-Installed Users After Onboarding

The system SHALL display the `pwa-install-banner` to authenticated users who have not installed the PWA, once onboarding is completed. The banner SHALL NOT be shown to unauthenticated (guest) users.

#### Scenario: Authenticated user has not installed the PWA

- **WHEN** the user is authenticated
- **AND** onboarding is completed (`OnboardingStep.COMPLETED`)
- **AND** the app has not been installed (`PwaInstallService.shouldShowInstallBanner` is `true`)
- **AND** the session-dismiss flag is NOT set in `sessionStorage`
- **THEN** the system SHALL display the `pwa-install-banner`

#### Scenario: Guest user is not shown the banner

- **WHEN** the user is NOT authenticated
- **THEN** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: App already installed — banner not shown

- **WHEN** the app has been installed (detected via `localStorage['pwa.installed']`, `navigator.standalone === true`, or `display-mode: standalone`)
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL be `false`
- **AND** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: Banner not shown during onboarding

- **WHEN** the user is in active onboarding steps (DISCOVERY, DASHBOARD, MY_ARTISTS)
- **THEN** the system SHALL NOT display the `pwa-install-banner`

---

### Requirement: Banner CTA Install Flow by Platform

The banner SHALL trigger the appropriate install action based on platform and available deferred prompt.

#### Scenario: Native one-tap install (Chrome/Edge with deferred prompt)

- **WHEN** the user taps the CTA button
- **AND** `PwaInstallService.canShowFab` is `true` (deferred prompt captured, not iOS)
- **THEN** the system SHALL call `deferredPrompt.prompt()`
- **AND** the native browser install dialog SHALL appear

#### Scenario: Guide sheet (iOS Safari or no deferred prompt)

- **WHEN** the user taps the CTA button
- **AND** `PwaInstallService.canShowFab` is `false` (iOS Safari or deferred prompt not yet captured)
- **THEN** the system SHALL open a bottom sheet containing step-by-step install instructions

#### Scenario: iOS guide sheet content

- **WHEN** the guide sheet is shown
- **AND** the platform is iOS (`PwaInstallService.isIos` is `true`)
- **THEN** the sheet SHALL display:
  1. Safari の共有ボタン（□↑）をタップ
  2. 「ホーム画面に追加」を選択
  3. 「追加」をタップ

#### Scenario: Chrome guide sheet content

- **WHEN** the guide sheet is shown
- **AND** the platform is NOT iOS
- **THEN** the sheet SHALL display:
  1. ブラウザのメニュー（⋮）をタップ
  2. 「ホーム画面に追加」を選択
  3. 「追加」をタップ

#### Scenario: Manual confirm from guide sheet

- **WHEN** the user taps the "追加しました" button in the guide sheet
- **THEN** the system SHALL call `PwaInstallService.confirmInstalled()`
- **AND** the guide sheet SHALL close
- **AND** the banner SHALL be permanently removed

#### Scenario: CTA mode upgrades reactively when deferred prompt arrives

- **WHEN** the banner is visible in guide mode
- **AND** the browser fires `beforeinstallprompt` (deferred prompt arrives)
- **THEN** `PwaInstallService.canShowFab` becomes `true`
- **AND** the banner CTA SHALL reactively switch to native one-tap mode without a page reload

---

### Requirement: Banner Disappears Permanently After Installation

The system SHALL remove the banner permanently once the app is installed.

#### Scenario: App installed via native dialog

- **WHEN** the browser fires the `appinstalled` event
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL become `false`
- **AND** the banner SHALL be removed from the DOM
- **AND** the banner SHALL NOT reappear in subsequent sessions

#### Scenario: App installed confirmed manually (iOS)

- **WHEN** `PwaInstallService.confirmInstalled()` is called
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL become `false`
- **AND** the banner SHALL be removed from the DOM
- **AND** the banner SHALL NOT reappear in subsequent sessions

---

### Requirement: Session-Level Dismiss

The banner SHALL support a per-session dismiss that suppresses the banner until the next session.

#### Scenario: User taps the close button

- **WHEN** the banner is visible
- **AND** the user taps the close button (`×`)
- **THEN** the banner SHALL be hidden for the remainder of the session
- **AND** the dismiss state SHALL be persisted in `sessionStorage`

#### Scenario: Banner reappears on next session

- **WHEN** the user dismissed the banner in a previous session
- **AND** the user starts a new session (page load / new tab)
- **AND** the app has NOT been installed
- **THEN** the session-dismiss state SHALL be cleared
- **AND** the banner SHALL be displayed again

#### Scenario: Session dismiss is NOT a permanent suppression

- **WHEN** the user has dismissed the banner via the close button
- **THEN** the banner dismissal SHALL NOT be persisted in `localStorage`
- **AND** the system SHALL NOT treat this as a permanent "user declined to install" signal

---

### Requirement: Banner Suppressed While PostSignupDialog Is Open

The banner SHALL NOT be visible while the `PostSignupDialog` is open to avoid visual conflict at the bottom of the screen.

#### Scenario: PostSignupDialog open — banner hidden

- **WHEN** the `PostSignupDialog` is open
- **THEN** the system SHALL suppress the `pwa-install-banner`
- **AND** the banner SHALL NOT be rendered in the DOM

#### Scenario: PostSignupDialog closed — banner visible

- **WHEN** the `PostSignupDialog` is closed (user taps Later/Close)
- **AND** `PwaInstallService.shouldShowInstallBanner` is `true`
- **AND** session-dismiss flag is NOT set
- **THEN** the banner SHALL be rendered

---

### Requirement: Banner Visual Presentation

The `pwa-install-banner` SHALL use the same visual design language as `signup-prompt-banner`.

#### Scenario: Banner is fixed at the bottom above the nav bar

- **WHEN** the banner is visible
- **THEN** the banner SHALL be positioned fixed at `inset-block-end: calc(3.5rem + env(safe-area-inset-bottom, 0px))`
- **AND** the banner SHALL span the full inline width of the screen (`inset-inline: 0`)

#### Scenario: Banner frosted glass and gradient border

- **WHEN** the banner is rendered
- **THEN** the background SHALL use a frosted glass surface (dark base at ~85% opacity with `backdrop-filter: blur`)
- **AND** the top border SHALL be a 2px gradient from `--color-brand-primary` to `--color-brand-secondary`

#### Scenario: CTA button glow pulse animation

- **WHEN** the banner is rendered
- **AND** `prefers-reduced-motion` is not set to `reduce`
- **THEN** the CTA button SHALL display a continuous glow pulse animation using `--color-brand-primary` cycling every 2.5 seconds

#### Scenario: Reduced motion — no animation

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the CTA button glow animation SHALL be suppressed
- **AND** the banner SHALL appear without a slide-up animation

#### Scenario: Banner slides in on appearance

- **WHEN** the banner becomes visible
- **AND** `prefers-reduced-motion` is not set to `reduce`
- **THEN** the banner SHALL animate in with a slide-up from below over 400ms

---

### Requirement: Banner Accessibility

The banner SHALL be accessible to keyboard and assistive technology users.

#### Scenario: Banner element has an accessible label

- **WHEN** the banner is rendered
- **THEN** the root `<aside>` element SHALL have an `aria-label` identifying it as the install prompt

#### Scenario: Close button has an accessible name

- **WHEN** the close button is rendered
- **THEN** it SHALL have an `aria-label` (e.g., "閉じる") so assistive technology announces its purpose

#### Scenario: Banner is removed from DOM when hidden

- **WHEN** the banner is not visible (session-dismissed, installed, or PostSignupDialog open)
- **THEN** the banner element SHALL be removed from the DOM (`if.bind`, not `show.bind`)
- **AND** neither the CTA button nor the close button SHALL be reachable via keyboard navigation

---

### Requirement: PwaInstallService Banner Visibility API

`PwaInstallService` SHALL expose a reactive property and a method to support the banner's lifecycle.

#### Scenario: shouldShowInstallBanner is true for Chrome/Edge non-installed users

- **WHEN** `PwaInstallService.browserSupportsPwa` is `true`
- **AND** the app has not been installed
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL be `true`

#### Scenario: shouldShowInstallBanner is true for iOS non-installed users

- **WHEN** `PwaInstallService.isIos` is `true`
- **AND** the app has not been installed
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL be `true`

#### Scenario: shouldShowInstallBanner becomes false on appinstalled

- **WHEN** the browser fires the `appinstalled` event
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL reactively update to `false`

#### Scenario: confirmInstalled marks the app as installed

- **WHEN** `PwaInstallService.confirmInstalled()` is called
- **THEN** the service SHALL persist `localStorage['pwa.installed'] = 'true'`
- **AND** `PwaInstallService.shouldShowInstallBanner` SHALL become `false`
