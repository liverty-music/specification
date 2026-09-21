# Pwa Install Banner

## Purpose

Invites a signed-in, not-yet-installed user to install the app to their device once onboarding is complete, adapting its install flow to the platform, and hiding itself once installed, dismissed for the session, or while another prompt is open.

## Requirements

### Requirement: PWA Install Prompt i18n

The PWA install prompt SHALL use i18n keys for all user-facing text, consistent with the notification prompt's existing i18n pattern.

#### Scenario: PWA install prompt displays localized text

- **WHEN** the PWA install prompt is visible
- **THEN** the title text SHALL be rendered via the `pwa.title` i18n key
- **AND** the description text SHALL be rendered via the `pwa.description` i18n key
- **AND** the install button label SHALL be rendered via the `pwa.install` i18n key
- **AND** the dismiss button label SHALL be rendered via the `pwa.notNow` i18n key
- **AND** the text SHALL NOT be hardcoded in the template

---

### Requirement: Prompt Entrance and Exit Animations

The PWA install prompt and notification prompt SHALL animate when entering and leaving the viewport, providing visual continuity with the rest of the onboarding flow.

#### Scenario: Prompt entrance animation

- **WHEN** the PWA install prompt or notification prompt becomes visible
- **THEN** the prompt SHALL animate in using a fade-slide-up effect (opacity 0 -> 1, translateY 16px -> 0)
- **AND** the animation duration SHALL be 600ms with ease-out timing
- **AND** the animation SHALL reuse the existing `fade-slide-up` keyframe defined in `my-app.css`

#### Scenario: Prompt exit animation

- **WHEN** the PWA install prompt or notification prompt is dismissed
- **THEN** the prompt SHALL animate out using a fade-slide-down effect (opacity 1 -> 0, translateY 0 -> 16px)
- **AND** the animation duration SHALL be 600ms with ease-out timing
- **AND** the element SHALL remain in the DOM until the exit animation completes

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the prompt entrance and exit animations SHALL be skipped
- **AND** the prompt SHALL appear and disappear instantly

### Requirement: Install-prompt listener registers before routing

The install-prompt event listener for `beforeinstallprompt` SHALL be registered before any route navigation begins, so that the event is not missed during the OIDC auth-callback page load.

#### Scenario: Listener registered before auth-callback navigation

- **WHEN** the application boots and the app shell activates
- **THEN** install-prompt handling SHALL be initialized as part of app shell activation
- **AND** the `beforeinstallprompt` event listener SHALL be registered before any route transition begins
- **AND** any `beforeinstallprompt` event fired during the `/auth/callback` route SHALL be captured

#### Scenario: Install row shows native button when prompt captured during auth-callback

- **WHEN** Chrome fires `beforeinstallprompt` during the `/auth/callback` page load
- **AND** the user completes sign-up and the post-signup dialog opens on the dashboard
- **THEN** the captured install prompt SHALL be available to show
- **AND** the post-signup dialog SHALL display the native install button in the install row

### Requirement: PWA Install Prompt Blocked During Onboarding

The system SHALL NOT display the `pwa-install-banner` while the user is in active onboarding steps (DISCOVERY, DASHBOARD, MY_ARTISTS).

#### Scenario: User is mid-tutorial on the dashboard

- **WHEN** the user is at onboarding step DASHBOARD
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL capture the event
- **AND** the system SHALL NOT display the `pwa-install-banner`
- **AND** the native install prompt SHALL remain unavailable

#### Scenario: User has not started onboarding (LP step)

- **WHEN** the user is at onboarding step LP
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL NOT display the `pwa-install-banner`

### Requirement: PWA Install Banner Eligible After Onboarding Completion

The `pwa-install-banner` SHALL be eligible immediately after onboarding completion for authenticated users who have not installed the app.

#### Scenario: First session after completion — authenticated user

- **WHEN** the user has completed onboarding
- **AND** the user IS authenticated
- **AND** the app has not been installed
- **THEN** the system SHALL display the `pwa-install-banner`

#### Scenario: Guest user after onboarding — banner not shown

- **WHEN** the user has completed onboarding
- **AND** the user is NOT authenticated
- **THEN** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: Completion within the same session

- **WHEN** the user transitions to `OnboardingStep.COMPLETED` within the current session
- **AND** the user is authenticated
- **THEN** the banner SHALL become visible immediately in that same session

---

### Requirement: Banner Visible to Authenticated Non-Installed Users After Onboarding

The system SHALL display the `pwa-install-banner` to authenticated users who have not installed the PWA, once onboarding is completed. The banner SHALL NOT be shown to unauthenticated (guest) users.

#### Scenario: Authenticated user has not installed the PWA

- **WHEN** the user is authenticated
- **AND** onboarding is completed (`OnboardingStep.COMPLETED`)
- **AND** the app has not been installed
- **AND** the session-dismiss flag is NOT set in `sessionStorage`
- **THEN** the system SHALL display the `pwa-install-banner`

#### Scenario: Guest user is not shown the banner

- **WHEN** the user is NOT authenticated
- **THEN** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: App already installed — banner not shown

- **WHEN** the app has been installed (detected via `localStorage['pwa.installed']`, `navigator.standalone === true`, or `display-mode: standalone`)
- **THEN** the system SHALL determine the banner should not be shown
- **AND** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: Banner not shown during onboarding

- **WHEN** the user is in active onboarding steps (DISCOVERY, DASHBOARD, MY_ARTISTS)
- **THEN** the system SHALL NOT display the `pwa-install-banner`

### Requirement: Banner CTA Install Flow by Platform

The banner SHALL trigger the appropriate install action based on platform and available deferred prompt.

#### Scenario: Native one-tap install (Chrome/Edge with deferred prompt)

- **WHEN** the user taps the CTA button
- **AND** the native install prompt has been captured (not iOS)
- **THEN** the system SHALL call `deferredPrompt.prompt()`
- **AND** the native browser install dialog SHALL appear

#### Scenario: Guide sheet (iOS Safari or no deferred prompt)

- **WHEN** the user taps the CTA button
- **AND** the native install prompt is unavailable (iOS Safari or not yet captured)
- **THEN** the system SHALL open a bottom sheet containing step-by-step install instructions

#### Scenario: iOS guide sheet content

- **WHEN** the guide sheet is shown
- **AND** the platform is iOS
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
- **THEN** the system SHALL record that installation was confirmed
- **AND** the guide sheet SHALL close
- **AND** the banner SHALL be permanently removed

#### Scenario: CTA mode upgrades reactively when deferred prompt arrives

- **WHEN** the banner is visible in guide mode
- **AND** the browser fires `beforeinstallprompt` (deferred prompt arrives)
- **THEN** the native install prompt becomes available
- **AND** the banner CTA SHALL reactively switch to native one-tap mode without a page reload

### Requirement: Banner Disappears Permanently After Installation

The system SHALL remove the banner permanently once the app is installed.

#### Scenario: App installed via native dialog

- **WHEN** the browser fires the `appinstalled` event
- **THEN** the system SHALL determine the banner should no longer be shown
- **AND** the banner SHALL be removed from the DOM
- **AND** the banner SHALL NOT reappear in subsequent sessions

#### Scenario: App installed confirmed manually (iOS)

- **WHEN** the user confirms manual installation
- **THEN** the system SHALL determine the banner should no longer be shown
- **AND** the banner SHALL be removed from the DOM
- **AND** the banner SHALL NOT reappear in subsequent sessions

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

### Requirement: Banner Suppressed While Post-Signup Dialog Is Open

The banner SHALL NOT be visible while the post-signup dialog is open to avoid visual conflict at the bottom of the screen.

#### Scenario: Post-signup dialog open — banner hidden

- **WHEN** the post-signup dialog is open
- **THEN** the system SHALL suppress the banner
- **AND** the banner SHALL NOT be rendered in the DOM

#### Scenario: Post-signup dialog closed — banner visible

- **WHEN** the post-signup dialog is closed (user taps Later/Close)
- **AND** the system determines the install banner should be shown
- **AND** session-dismiss flag is NOT set
- **THEN** the banner SHALL be rendered

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

### Requirement: Banner visibility state and installed confirmation

The system SHALL expose a reactive property and a method to support the install banner's lifecycle.

#### Scenario: Install banner shown for Chrome/Edge non-installed users

- **WHEN** the browser supports PWA installation
- **AND** the app has not been installed
- **THEN** the install banner SHALL be shown

#### Scenario: Install banner shown for iOS non-installed users

- **WHEN** the browser is iOS
- **AND** the app has not been installed
- **THEN** the install banner SHALL be shown

#### Scenario: Install banner hides on appinstalled

- **WHEN** the browser fires the `appinstalled` event
- **THEN** the install banner SHALL reactively hide

#### Scenario: Confirming installation marks the app as installed

- **WHEN** the installed-confirmation action is invoked
- **THEN** the system SHALL persist that the app has been installed
- **AND** the install banner SHALL hide
