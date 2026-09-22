# Post Signup Dialog

## Purpose

Consolidates notification permission and PWA install prompts into a single dialog shown after the first successful signup, providing a streamlined post-authentication experience.

## Requirements

### Requirement: Post-Signup Dialog on First Authentication

The system SHALL display a dialog after the first successful **sign-up** that consolidates a celebration message with optional power-up actions (notification permission, PWA install), without front-loading guidance for features the user has not yet encountered.

Whether an authenticated callback is treated as a first sign-up SHALL be determined by the **flow the user initiated** — the sign-up flow versus the sign-in flow — carried as a signal that round-trips through the OIDC authorization request and back to the auth-callback. It SHALL NOT be inferred solely from the absence of a locally cached user identifier, because a returning user can arrive with an empty local cache (new browser or device, cleared storage, or a prior anonymous/guest session that never cached an identifier) and MUST NOT be treated as a new sign-up.

#### Scenario: Dialog shown after first signup

- **WHEN** the auth-callback route completes an authenticated callback whose originating flow is the **sign-up** flow
- **AND** `localStorage['liverty:postSignup:shown']` is not set
- **THEN** the system SHALL set `localStorage['liverty:postSignup:shown']` to the pending marker
- **AND** the system SHALL navigate to `/dashboard`
- **AND** the Dashboard SHALL display the post-signup dialog on load

#### Scenario: Dialog not shown on subsequent logins

- **WHEN** the auth-callback route completes for a returning user
- **AND** `localStorage['liverty:postSignup:shown']` is already set
- **THEN** the system SHALL NOT show the post-signup dialog

#### Scenario: Sign-in with an empty local cache does not trigger the dialog

- **WHEN** the auth-callback route completes an authenticated callback whose originating flow is the **sign-in** flow
- **AND** no user identifier is cached locally (e.g. a new browser/device, cleared storage, or a prior guest session)
- **THEN** the system SHALL NOT set `localStorage['liverty:postSignup:shown']` to the pending marker
- **AND** the system SHALL NOT display the celebration overlay or the post-signup dialog
- **AND** the user SHALL be navigated to `/dashboard` without a first-run payoff

#### Scenario: Dialog content leads with celebration

- **WHEN** the post-signup dialog is displayed
- **THEN** the first content row SHALL be a celebration message acknowledging completion of onboarding
- **AND** it SHALL offer a notification opt-in action if notification permission has not yet been requested
- **AND** it SHALL show a notification denied message if notification permission has been denied
- **AND** it SHALL offer a PWA install action if the app is installable and not yet installed
- **AND** it SHALL provide a dismiss/close action in the footer

#### Scenario: Footer button label when all actions are complete

- **WHEN** the post-signup dialog is displayed
- **AND** the app is not installable (already installed, or the browser lacks install support)
- **AND** notification permission has been granted
- **THEN** the footer button SHALL display the label "Close"

#### Scenario: Footer button label when actions remain

- **WHEN** the post-signup dialog is displayed
- **AND** either the app is still installable OR notification permission has not been granted
- **THEN** the footer button SHALL display the label "Later"

#### Scenario: Notification opt-in from dialog

- **WHEN** the user taps the notification opt-in button in the post-signup dialog
- **THEN** the system SHALL call `PushService.create()` (backed by `PushNotificationService.Create` RPC)
- **AND** the system SHALL NOT write any `localStorage` flag for push notification enabled state
- **AND** on success, the notification row SHALL show a confirmed state
- **AND** on failure or denial, the notification row SHALL show an error state
- **AND** the settings page SHALL subsequently derive the toggle state from the backend via `PushNotificationService.Get` without relying on any `localStorage` flag

#### Scenario: PWA install from dialog — native prompt

- **WHEN** the user taps the install button in the post-signup dialog
- **AND** the native install prompt has been captured
- **THEN** the system SHALL trigger the deferred `beforeinstallprompt` event

#### Scenario: PWA install row hidden on iOS Safari

- **WHEN** the post-signup dialog is displayed
- **AND** the browser does not support the `BeforeInstallPromptEvent` API (i.e. iOS Safari)
- **THEN** the PWA install row SHALL NOT be shown in the dialog
- **AND** the persistent `pwa-install-banner` provides the iOS install path instead

#### Scenario: Dialog dismissed

- **WHEN** the user taps the dismiss button
- **THEN** the post-signup dialog SHALL close
- **AND** the notification prompt SHALL NOT be shown again in the same session (coordinated via the prompt coordination)
- **AND** the `pwa-install-banner` SHALL become visible (it is not suppressed by post-signup dialog dismissal)

### Requirement: Dialog reliably opens when active is true at creation time
The post-signup dialog SHALL reliably open when `active` is bound to `true` at component creation time, not only when `active` transitions from `false` to `true` after the component is attached.

#### Scenario: Dashboard sets showPostSignupDialog in loading() before attach
- **WHEN** `DashboardRoute.loading()` sets `showPostSignupDialog = true`
- **AND** the post-signup dialog receives `active = true` during its `binding` phase
- **THEN** `activeChanged()` SHALL set `isOpen = true`
- **AND** the inner `<bottom-sheet>` SHALL open successfully (via its attached-lifecycle fallback)
- **AND** the dialog SHALL be visible to the user with its full content

### Requirement: Dialog title and aria-label use i18n bindings
All user-visible strings in the post-signup dialog SHALL use i18n translation bindings. No hardcoded display strings are permitted in the template.

#### Scenario: Title renders in active locale
- **WHEN** the post-signup dialog is displayed
- **AND** the active locale is `en`
- **THEN** the `<h2>` title SHALL render using the `postSignup.title` translation key in the EN translation
- **AND** the rendered text SHALL be in English (e.g., `Account registration complete!`)

#### Scenario: Title renders in Japanese locale
- **WHEN** the post-signup dialog is displayed
- **AND** the active locale is `ja`
- **THEN** the `<h2>` title SHALL render using the `postSignup.title` translation key in the JA translation
- **AND** the rendered text SHALL be `✅ アカウント登録完了！`

#### Scenario: aria-label follows active locale
- **WHEN** the post-signup dialog is displayed
- **AND** the active locale is `en`
- **THEN** the wrapping `<bottom-sheet>` element SHALL have an `aria-label` rendered from the `postSignup.ariaLabel` translation key in the EN translation

#### Scenario: Translation key parity
- **WHEN** `postSignup.title` or `postSignup.ariaLabel` keys exist in the Japanese translation resource
- **THEN** the same keys SHALL exist in the English translation resource

### Requirement: Dialog footer button reflects completion state

The footer button label in the post-signup dialog SHALL dynamically reflect whether the user has completed all available actions.

#### Scenario: Button switches to "Close" after enabling notifications

- **WHEN** the user taps the notification opt-in button
- **AND** enabling push notifications succeeds
- **AND** installing the app as a PWA is not offered (no separate install action is pending)
- **THEN** the notification permission SHALL become granted
- **AND** all available actions SHALL be considered complete
- **AND** the footer button SHALL display "Close"

### Requirement: Celebration Precedes Post-Signup Dialog

On the post-signup dashboard redirect, the full (confetti) celebration overlay SHALL be shown before the PostSignupDialog. The PostSignupDialog SHALL open when the celebration overlay is dismissed, sequencing the emotional payoff ahead of the functional setup actions.

#### Scenario: Dialog opens after celebration dismissal

- **WHEN** a newly signed-up user is redirected to the dashboard
- **AND** the full celebration overlay (per `onboarding-celebration` "Two-Tier Celebration Overlay") is shown
- **THEN** the system SHALL NOT display the PostSignupDialog while the celebration overlay is visible
- **AND** the system SHALL display the PostSignupDialog once the celebration overlay is dismissed

#### Scenario: Region selection still precedes both

- **WHEN** a newly signed-up user is redirected to the dashboard
- **AND** `needsRegion` is `true`
- **THEN** the system SHALL resolve the home-area selection first
- **AND** only then evaluate the celebration overlay, followed by the PostSignupDialog on dismissal

### Requirement: PWA Install Row Shows Fallback Instructions When Native Prompt Unavailable

When the browser supports PWA install but the native prompt has not been captured, the post-signup dialog SHALL show a manual install guide rather than hiding the row.

#### Scenario: Install row shows "How to add" disclosure when deferredPrompt is absent

- **WHEN** the post-signup dialog is displayed
- **AND** the browser supports PWA install
- **AND** the native install prompt has not yet been captured
- **THEN** the install row SHALL display a "How to add" disclosure control (a native `<details>`/`<summary>` rendered as a button) instead of the native install button
- **AND** the disclosure SHALL be collapsed by default (the instruction steps hidden)

#### Scenario: Toggling "How to add" reveals inline instructions

- **WHEN** the user activates the "How to add" disclosure (click, or keyboard via the native `<summary>`)
- **THEN** the install row SHALL expand to show numbered steps for browser-menu-based installation:
  1. Open the browser menu (⋮)
  2. Select "Add to Home Screen"
  3. Tap "Add" to finish
- **AND** the "How to add" summary SHALL remain visible above the expanded steps and stay toggleable (the native disclosure can be collapsed again)

#### Scenario: Install row reactively upgrades to native button on prompt arrival

- **WHEN** the post-signup dialog is open
- **AND** the browser fires `beforeinstallprompt` (native prompt arrives after dialog opened)
- **THEN** the native install prompt becomes available
- **AND** the install row SHALL update reactively to show the native install button
- **AND** the "How to add" disclosure SHALL be replaced by the native install button
