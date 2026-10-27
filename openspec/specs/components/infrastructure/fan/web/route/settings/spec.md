# Settings

## Purpose

Provides the settings screen where a user manages their account, push notification and language preferences, and analytics and session-replay consent, adapting its account section for guests and signed-in users alike.

## Requirements

### Requirement: Settings exposes Analytics and Session-replay opt-out toggles
The settings page SHALL present two independent opt-out toggles under the "Privacy & Analytics" section: **Analytics** (controls PostHog event capture, identification, and persistent storage) and **Session replay** (controls session recording only). Both SHALL default to on for authenticated users and SHALL be independently controllable. Each SHALL carry a plain-language description and a privacy-policy anchor.

The pre-opt-out field formerly named `marketingMeasurement` SHALL be renamed `sessionReplay`; the persisted consent-state version SHALL bump and migrate prior `v1` payloads.

#### Scenario: Both toggles default to on
- **WHEN** an authenticated user opens the settings page without having changed either toggle
- **THEN** the Analytics toggle SHALL render as on
- **AND** the Session-replay toggle SHALL render as on
- **AND** each toggle SHALL be independently controllable

#### Scenario: User disables session replay but keeps event analytics
- **WHEN** the user turns the Session-replay toggle off and leaves Analytics on
- **THEN** the application SHALL call `posthog.set_config` to stop session recording
- **AND** the application SHALL continue capturing catalogue events and SHALL keep the identified profile active

---

### Requirement: Analytics opt-out state is persisted and user-controllable from settings
The application SHALL persist the user's per-purpose opt-out state and SHALL let the user change it at any time from the settings page. Turning Analytics off SHALL stop identified tracking immediately; turning it back on SHALL resume identified tracking.

#### Scenario: User opts out of analytics from settings
- **WHEN** the user turns the Analytics toggle off
- **THEN** the application SHALL call `posthog.opt_out_capturing()` immediately
- **AND** the application SHALL persist the updated opt-out state
- **AND** subsequent navigation SHALL NOT emit any identified PostHog event

#### Scenario: User re-enables analytics after opting out
- **WHEN** a user who previously opted out turns Analytics back on
- **THEN** the application SHALL call `posthog.opt_in_capturing()` to clear the persisted opt-out flag (which `identify()` does not clear on its own)
- **AND** the application SHALL invoke deferred PostHog initialisation if not already initialised
- **AND** the application SHALL call `posthog.identify(user.id.value, properties)` with the user's `UserId`
- **AND** because capture was fully suppressed while opted out, the anonymous profile carries no opted-out telemetry, so the `identify` merge cannot link opted-out events to the user's identity (no preceding `reset()` is required)
- **AND** the application SHALL emit subsequent events normally

### Requirement: Persistent auth entry point in Settings

The system SHALL provide an always-reachable sign-in / sign-up entry point for guests from the `'discovery'` step onward, so a returning user who entered the guest flow can authenticate without completing onboarding. This entry point is hosted in Settings (see `settings` spec).

#### Scenario: Guest reaches auth entry during early onboarding

- **WHEN** a guest user is at the `'discovery'` step or later
- **AND** the user opens Settings
- **THEN** the system SHALL present a sign-in / sign-up call to action

#### Scenario: Returning user recovers from mis-tapping Get Started

- **WHEN** a user taps [Get Started] on Welcome and enters the guest discovery step
- **AND** the user actually intended to log in
- **THEN** the user SHALL be able to open Settings and start sign-in without first satisfying any onboarding progression condition

### Requirement: Stale subscription self-healing on settings load

The system SHALL keep the browser's push subscription and the backend's stored subscription convergent automatically, without requiring user interaction, whenever the user has already granted browser notification permission. Recovery SHALL cover both divergence directions:

- **Backend missing the browser's subscription** — the browser has an active subscription the backend does not know about.
- **Browser missing a subscription entirely** — the browser has no active subscription (e.g., after the push service invalidated it, a `410 Gone` cleanup on the backend, a PWA reinstall, or site-data clearing), even though permission is still granted.

In the second case, when permission is granted, the system SHALL create a fresh browser subscription with the configured VAPID application server key and register it via `PushSubscriptionService.Create`. The system SHALL NOT leave a permission-granted user silently unsubscribed. When permission is NOT granted, the system SHALL surface an OFF/re-enable affordance rather than silently doing nothing.

#### Scenario: Self-heal on settings page load

- **WHEN** the settings page loads
- **AND** `PushManager.getSubscription()` returns a non-null subscription
- **AND** `PushSubscriptionService.Get` returns `NOT_FOUND` for that endpoint
- **THEN** the system SHALL call `PushSubscriptionService.Create` with the browser's existing subscription material
- **AND** on success, the UI toggle SHALL reflect the ON state
- **AND** the user SHALL NOT be prompted to re-grant notification permission

#### Scenario: No self-heal when browser has no subscription

- **WHEN** the settings page loads
- **AND** `PushManager.getSubscription()` returns `null`
- **AND** browser notification permission is NOT `granted`
- **THEN** the UI toggle SHALL reflect the OFF state
- **AND** the system SHALL NOT call `Create` or `Get`
- **AND** the system SHALL offer the user an affordance to enable notifications

#### Scenario: Auto re-subscribe when browser has no subscription but permission is granted

- **WHEN** the app resolves push state (e.g., on settings page load or app startup)
- **AND** browser notification permission is `granted`
- **AND** `PushManager.getSubscription()` returns `null`
- **THEN** the system SHALL call `PushManager.subscribe()` with the configured VAPID application server key
- **AND** SHALL register the resulting subscription via `PushSubscriptionService.Create`
- **AND** on success the UI toggle SHALL reflect the ON state
- **AND** the user SHALL NOT be prompted to re-grant notification permission

#### Scenario: Self-heal failure degrades to OFF

- **WHEN** the self-heal `subscribe()` or `Create` call fails
- **THEN** the UI toggle SHALL reflect the OFF state
- **AND** the system SHALL surface the error via standard frontend error handling
- **AND** SHALL NOT swallow the failure silently

### Requirement: Subscription registration failures are observable on the client

Push subscription registration (`PushManager.subscribe()` and the `PushSubscriptionService.Create` RPC) SHALL NOT fail silently. Failures SHALL be logged on the client and reflected in the notification toggle state, so a user who believes they enabled notifications is not left silently unsubscribed.

#### Scenario: subscribe() throws during enable

- **WHEN** the user enables notifications
- **AND** `PushManager.subscribe()` throws
- **THEN** the failure SHALL be logged on the client
- **AND** the UI toggle SHALL reflect the OFF (not-enabled) state
- **AND** the user SHALL NOT be shown a success state

### Requirement: Push Notification Toggle
The system SHALL allow users to control push notification delivery for the current browser session. The toggle's displayed state SHALL be derived from the backend push subscription record combined with the browser's `PushManager` state — never from `localStorage`.

#### Scenario: Toggle state on page load — subscribed on this browser
- **WHEN** the Settings page loads
- **AND** `PushManager.getSubscription()` returns a non-null subscription
- **AND** `PushSubscriptionService.Get(endpoint)` returns an existing `PushSubscription`
- **THEN** the Push Notifications toggle SHALL display ON

#### Scenario: Toggle state on page load — not subscribed on this browser
- **WHEN** the Settings page loads
- **AND** `PushManager.getSubscription()` returns `null`
- **THEN** the Push Notifications toggle SHALL display OFF
- **AND** the system SHALL NOT call `PushSubscriptionService.Get` for a non-existent endpoint

#### Scenario: Toggle state on page load — browser has subscription but backend does not (self-heal)
- **WHEN** the Settings page loads
- **AND** `PushManager.getSubscription()` returns a non-null subscription
- **AND** `PushSubscriptionService.Get` returns `NOT_FOUND`
- **THEN** the system SHALL call `PushSubscriptionService.Create` with the browser's existing subscription material
- **AND** on success, the Push Notifications toggle SHALL display ON
- **AND** the user SHALL NOT be shown a permission prompt during self-heal

#### Scenario: Toggling notifications ON
- **WHEN** a user toggles the Push Notifications switch ON
- **THEN** the system SHALL call `PushManager.subscribe()` and `PushSubscriptionService.Create` with the resulting subscription material
- **AND** on success, the toggle SHALL reflect ON
- **AND** the system SHALL NOT write any `localStorage` flag for this state

#### Scenario: Toggling notifications OFF (this browser only)
- **WHEN** a user toggles the Push Notifications switch OFF
- **THEN** the system SHALL call `PushSubscriptionService.Delete(endpoint)` with the current browser's endpoint
- **AND** the system SHALL call `PushSubscription.unsubscribe()` on the browser subscription object
- **AND** other browsers registered by the same user SHALL continue to receive notifications
- **AND** the toggle SHALL reflect OFF

#### Scenario: Toggle state is not cached in localStorage
- **WHEN** the Settings page is rendered
- **THEN** the system SHALL NOT read `localStorage['userNotificationsEnabled']` to determine toggle state
- **AND** the `userNotificationsEnabled` key SHALL NOT appear in the `StorageKeys` catalog

### Requirement: About Section
The system SHALL provide access to legal and licensing information via in-app routes.

#### Scenario: Legal links
- **WHEN** the About section is displayed
- **THEN** the system SHALL show links to Terms of Service, Privacy Policy, and OSS Licenses
- **AND** each link SHALL target its in-app route (`/legal/terms`, `/legal/privacy`, `/legal/licenses`) rather than an external URL
- **AND** tapping a link SHALL navigate to the corresponding in-app legal document page

---

### Requirement: Language Preference
The system SHALL allow users to change the display language of the application. While authenticated, the change SHALL be persisted to the backend user row via `UserService.SetPreferredLanguage` and, once applied, also saved on this device per `components/infrastructure/fan/web/global/i18n` "Language Kept Across Sign-in and Sign-out". Settings SHALL NOT read browser local storage for the language preference: the row and the selector derive from the current user's preferred language.

#### Scenario: Displaying language option
- **WHEN** the Settings page is displayed for an authenticated user
- **THEN** the system SHALL show a "Language" row displaying the current language name derived from the current user's preferred language (e.g., "日本語" or "English")
- **AND** the system SHALL NOT read browser local storage to populate this row

#### Scenario: Displaying language option before backfill completes
- **WHEN** the Settings page is displayed and the current user's preferred language is absent (legacy NULL row, or backfill RPC still in flight after hydration)
- **THEN** the system SHALL derive the displayed language name from the currently active locale (the value the backfill RPC will send)
- **AND** the system SHALL NOT read browser local storage to populate this row
- **AND** the row SHALL re-evaluate automatically once the current user's preferred language becomes populated by the backfill response

#### Scenario: Changing language
- **WHEN** a user taps the "Language" row
- **THEN** the system SHALL display a selection UI with available languages: 日本語, English
- **AND** WHEN the user selects a language different from the current one
- **THEN** the system SHALL call `UserService.SetPreferredLanguage` with the new value
- **AND** on success, the system SHALL change the active locale
- **AND** all UI text on the Settings page and throughout the app SHALL immediately update to the selected language
- **AND** the language saved on this device SHALL then hold the selected language, so the first screen after a sign-out opens in it
- **AND** subsequent reads of the current user's preferred language SHALL return the new value (write-through per `user-profile-hydration`)

#### Scenario: Language change RPC failure
- **WHEN** the `SetPreferredLanguage` RPC fails (network or server error)
- **THEN** the active locale SHALL end at the value it held before the change was attempted (the implementation MAY apply the new locale optimistically and revert on failure, consistent with `frontend-i18n`'s "Authenticated language switch RPC failure" scenario; the user-observable end-state SHALL be unchanged)
- **AND** the displayed "Language" row SHALL end at the prior value (since the row is derived from the current user's preferred language, which is restored when the optimistic update is reverted)
- **AND** the language saved on this device SHALL end at the value it held before the change was attempted
- **AND** the system SHALL surface a Snack notification indicating the change could not be saved

#### Scenario: Re-selecting the current language is a no-op
- **WHEN** a user taps the "Language" row and selects the language already in effect
- **THEN** the system SHALL close the selection UI without issuing an RPC
- **AND** no DB write SHALL occur

### Requirement: Sign Out
The system SHALL allow authenticated users to sign out of their account. The Sign Out control SHALL be rendered only when the user is authenticated and SHALL be hidden for guest (unauthenticated) users. It SHALL stand apart from every other control, in a group of its own below the ACCOUNT section with at least 24px between them, so a tap meant for an account row never signs the user out. Only the Delete account control SHALL come after it.

#### Scenario: Sign out action
- **WHEN** an authenticated user taps the "Sign Out" button
- **THEN** the system SHALL clear the user's authentication session
- **AND** the system SHALL navigate to the Landing Page
- **AND** the Sign Out button SHALL be visually distinct (e.g., red text) and positioned at the bottom of the settings list, above only the Delete account control

#### Scenario: Sign out apart from account rows
- **WHEN** an authenticated user views the ACCOUNT section with the Passkeys row as its last row
- **THEN** the Sign Out control SHALL be in a separate group below it, at least 24px away, not adjoining the Passkeys row

#### Scenario: Sign out hidden for guests
- **WHEN** an unauthenticated (guest) user views the Settings page
- **THEN** the system SHALL NOT render the Sign Out control

### Requirement: Guest-Adaptive Account Section

The system SHALL adapt the Settings page to authentication state. For guests, the system SHALL present the sign-in / sign-up call to action as a visually emphasized hero placed at the TOP of the Settings page (before the preferences content), and SHALL hide account-bound controls (email address, email verification status, resend-verification, sign-out). For authenticated users, the system SHALL NOT render the guest hero, and the bottom ACCOUNT section SHALL present the existing account controls.

#### Scenario: Guest sees a prominent sign-in hero at the top

- **WHEN** an unauthenticated user views the Settings page
- **THEN** the system SHALL render a guest call-to-action hero at the top of the page, above the preferences content
- **AND** the hero SHALL be visually distinct from the standard list cards (e.g. brand-tinted background and a filled primary action)
- **AND** the hero SHALL offer a primary "ログイン" action and a secondary "新規登録" action that initiate the OIDC sign-in / sign-up flow
- **AND** the email address row, email-verification badge, and resend-verification button SHALL NOT be rendered

#### Scenario: Authenticated user sees account controls and no guest hero

- **WHEN** an authenticated user views the Settings page
- **THEN** the system SHALL NOT render the guest hero
- **AND** the bottom ACCOUNT section SHALL render the email address, the verification badge, the resend-verification button (when unverified), and the Sign Out control

### Requirement: Guest Language Preference

The system SHALL allow a guest user to change the display language from
Settings. For guests, the change SHALL apply to the active locale only and
SHALL NOT call `UserService.SetPreferredLanguage` (no backend persistence is
possible without an account). The language selector's selected-state indicator
and the Language row SHALL derive from an observable current-language
value — NOT from a one-time read of the active locale that cannot be observed
for reactivity — so they reflect the active locale reactively for guests.

#### Scenario: Guest changes language

- **WHEN** an unauthenticated user selects a language different from the current one
- **THEN** the system SHALL change the active locale
- **AND** all UI text SHALL immediately update to the selected language
- **AND** the system SHALL NOT call `UserService.SetPreferredLanguage`

#### Scenario: Selector highlight follows the active locale for guests

- **WHEN** an unauthenticated user changes the language (e.g. English → 日本語)
- **AND** subsequently reopens the language selector
- **THEN** the selector SHALL highlight the newly active language (日本語)
- **AND** SHALL NOT continue highlighting the previously active language
- **AND** the Settings "Language" row SHALL display the newly active language name

#### Scenario: Guest home area sourced from the user store

- **WHEN** an unauthenticated user views or changes "My Home Area"
- **THEN** the system SHALL read and write the home-area code via the user data store
  (backed by guest local storage for a guest) rather than branching on auth state
  at the call site

### Requirement: Settings Page Layout and Scroll

The Settings page SHALL render a fixed page header and a vertically scrollable
content area. The settings section list SHALL scroll within the content area
without displacing or overlapping the fixed header, and the bottom navigation
bar SHALL remain unaffected. The content scroll container SHALL follow the
project's shared route scroll pattern: the content track grid item SHALL set
`min-block-size: 0` so it can shrink within its track, and scrolling SHALL be
owned by a scroll container whose minimum size does not prevent overflow.

#### Scenario: First preferences row is visible on load
- **WHEN** the Settings page loads
- **THEN** the PREFERENCES section title and its first row ("My Home Area")
  SHALL be visible within the content area
- **AND** they SHALL NOT be clipped by or rendered behind the fixed page header

#### Scenario: Section list scrolls within the content area
- **WHEN** the settings content exceeds the available viewport height
- **THEN** the section list SHALL scroll vertically within the content area
- **AND** the page header SHALL remain pinned at the top
- **AND** the bottom navigation bar SHALL remain pinned at the bottom

#### Scenario: Content track item can shrink
- **WHEN** the Settings route lays out its `header` / `content` grid
- **THEN** the content-area grid item SHALL set `min-block-size: 0`
- **AND** the scroll container SHALL engage `overflow-y: auto` rather than
  expanding the grid track to full content height

### Requirement: Toggle Control Layout Integrity

The system SHALL render each Settings toggle switch at a fixed control size whose visual thumb remains fully contained within the toggle track and within the enclosing card, independent of the length of any adjacent label or description in the same row. The toggle track SHALL NOT shrink below its declared size when competing for horizontal space with sibling content.

#### Scenario: Toggle paired with a long multi-line description

- **WHEN** a toggle row is rendered with a description long enough to wrap onto multiple lines
- **THEN** the toggle track SHALL retain its declared control width (it SHALL NOT collapse)
- **AND** the toggle thumb SHALL remain fully inside the track in both the ON and OFF positions
- **AND** no part of the thumb or track SHALL overflow the right edge of the enclosing card

#### Scenario: Toggle vertical alignment against multi-line content

- **WHEN** a toggle row's text column spans multiple lines
- **THEN** the toggle control SHALL align to the first line of the label it controls rather than floating to the vertical centre of the whole text block

### Requirement: Expandable Toggle Description

The system SHALL allow a toggle row's descriptive text to be collapsed by default and expanded on demand, without compromising the accessibility semantics of the switch. The expand/collapse control and the switch SHALL be distinct, sibling interactive elements — the switch SHALL NOT contain another interactive control.

#### Scenario: Collapsed description with expand affordance

- **WHEN** a toggle row has a collapsible description and is in the collapsed state
- **THEN** the description SHALL NOT be rendered (the label and the expand affordance serve as the summary)
- **AND** an expand affordance (e.g. a rotating chevron) SHALL be shown next to the label to indicate more content is available

#### Scenario: Expanding and collapsing the description

- **WHEN** the user activates the description's disclosure control
- **THEN** the full description SHALL be revealed and the disclosure control's `aria-expanded` state SHALL reflect "true"
- **AND** activating it again SHALL collapse the description and set `aria-expanded` to "false"
- **AND** toggling the disclosure SHALL NOT change the switch's on/off value

#### Scenario: Switch remains operable and accessibly separate

- **WHEN** a toggle row presents both a disclosure control and a switch
- **THEN** the switch SHALL expose `role="switch"` with `aria-checked` reflecting its value
- **AND** the switch SHALL be an interactive element that is a sibling of (not a descendant of) the disclosure control
- **AND** the switch's activation target SHALL be at least 24px on both axes (WCAG 2.5.8 AA), with the adjacent disclosure control providing a larger neighbouring target — the row no longer adds block-axis padding to the switch, so the track sits pixel-aligned with the other rows' trailing controls (see design decision D0: card-grid + row-subgrid)

#### Scenario: No expand affordance when nothing to expand

- **WHEN** a toggle row has no description, or a description that fits within the collapsed length
- **THEN** no expand affordance SHALL be shown

### Requirement: Privacy & Analytics Consent Toggle Labeling

The Settings page SHALL present the analytics consent toggles using labels and descriptions that name the consent *purpose* (what the data is used for), not the data's processing *geography*. Each consent toggle on the Settings page SHALL remain a persistent, user-controlled opt-out for the corresponding consent purpose. The Settings page SHALL NOT present a per-region ("domestic" vs "overseas") processing toggle, and SHALL NOT remove a consent purpose's Settings opt-out while that purpose can be granted at signup.

#### Scenario: Product-analytics toggle is purpose-labeled

- **WHEN** the Privacy & Analytics section is rendered
- **THEN** the product-analytics toggle SHALL be bound to the product-analytics consent purpose
- **AND** its label and description SHALL describe improving the product experience from anonymous usage data
- **AND** its description SHALL state that no personally identifying information is collected

#### Scenario: Marketing-measurement toggle is purpose-labeled (not geography)

- **WHEN** the Privacy & Analytics section is rendered
- **THEN** the second toggle SHALL be bound to the `marketingMeasurement` consent purpose
- **AND** its label and description SHALL describe ad-effectiveness measurement, not "overseas" or "cross-border" data processing
- **AND** turning it off SHALL be stated to have no effect on other features

#### Scenario: Settings opt-out persists for a purpose granted at signup

- **WHEN** a user granted a consent purpose at the signup consent screen
- **THEN** the Settings page SHALL render a corresponding toggle that lets the user withdraw that consent
- **AND** the toggle SHALL reflect the persisted consent state on load

### Requirement: Platform-Conditional Sound Effects Hint

The Settings page SHALL only show the iOS-specific sound-effects behavior hint on iOS devices. On non-iOS platforms the system SHALL NOT display a hint that references iOS-only behavior.

#### Scenario: iOS device shows the iOS hint

- **WHEN** the Settings page is rendered on an iOS device
- **THEN** the sound-effects row SHALL display the iOS-specific hint about the device's silent/manner mode

#### Scenario: Non-iOS device does not show the iOS hint

- **WHEN** the Settings page is rendered on a non-iOS platform (Android, desktop)
- **THEN** the sound-effects row SHALL NOT display the iOS-specific hint

### Requirement: Language Selector Single-Select Semantics
The language selection UI SHALL be exposed to assistive technology as a single-select control so screen-reader users can perceive which language is active and that exactly one may be chosen. A visual-only `data-selected` highlight with an `aria-hidden` check icon SHALL NOT be the sole indicator of selection.

#### Scenario: Language options form a radiogroup
- **WHEN** the language selection UI is displayed
- **THEN** the option container SHALL expose `role="radiogroup"` (or use native `<input type="radio">`) with an accessible group name
- **AND** each language option SHALL expose `role="radio"` (or be a native radio) with `aria-checked` reflecting whether it is the active language
- **AND** the currently active language option SHALL have `aria-checked="true"` and all others `aria-checked="false"`

#### Scenario: Selected language is announced
- **WHEN** a screen-reader user navigates the language options
- **THEN** the active option SHALL be announced as the checked/selected radio
- **AND** selection state SHALL NOT depend on a CSS `data-selected` attribute or an `aria-hidden` check icon alone

---

### Requirement: Settings Async Status Live Region
Asynchronous status changes on the Settings page SHALL be announced to assistive technology via a polite live region rather than updating silently.

#### Scenario: Resend-verification status is announced
- **WHEN** the resend-verification button transitions between its states (idle → "Sending…" → "Sent")
- **THEN** the status change SHALL be conveyed through an `aria-live="polite"` region
- **AND** the email verification badge transition (Verified ↔ Not-verified) SHALL likewise be announced politely

---

### Requirement: Toggle Hint Association And Disabled Push Row
Descriptive hint text for a toggle row SHALL be programmatically associated with its control, and a control that is unavailable due to missing configuration SHALL remain discoverable by assistive technology.

#### Scenario: Toggle hint associated via aria-describedby
- **WHEN** a toggle row (`role="switch"`) has accompanying hint/description text
- **THEN** the switch SHALL reference that text via `aria-describedby`

#### Scenario: VAPID-unavailable push row stays discoverable
- **WHEN** push notifications are unavailable because the VAPID public key is missing
- **THEN** the push row SHALL use `aria-disabled="true"` plus an explanation rather than the native `disabled` attribute (which removes the control from assistive-technology discovery)

---

### Requirement: Settings Group List Semantics
Each Settings card SHALL expose list semantics so assistive technology announces a bounded list of items rather than a flat run of buttons interspersed with separator noise.

#### Scenario: Cards expose list semantics
- **WHEN** a Settings card containing multiple rows is rendered
- **THEN** the card SHALL use `role="list"` (or `<ul>`) with each row as a `role="listitem"` (or `<li>`)
- **AND** decorative `<hr>` separators between rows SHALL be removed (visual separation handled by CSS)

---

### Requirement: Email And Verification Badge Association
The account email and its verification badge SHALL be programmatically associated, and verification status SHALL be conveyed by more than color alone.

#### Scenario: Badge associated with email and not color-only
- **WHEN** the account section renders the email address and the Verified / Not-verified badge
- **THEN** the badge SHALL be programmatically associated with the email (e.g., via `aria-describedby` or an accessible-name relationship)
- **AND** the badge SHALL convey status with a non-color cue (text and/or icon) in addition to color

---

### Requirement: Consent Toggle Observable Binding
The Settings consent toggles SHALL bind directly to the observable consent state, with no component-local mirror of that state.

#### Scenario: Consent toggles reflect service state without a mirror
- **WHEN** the Settings page renders the analytics / marketing-measurement consent toggles
- **THEN** the toggle bindings SHALL derive from the observable consent state directly
- **AND** the component SHALL NOT maintain separate mirror fields or write-back handlers for consent state

#### Scenario: External consent change updates the toggles
- **WHEN** consent state changes outside the Settings toggle handlers (e.g., via the onboarding consent screen earlier in the session)
- **THEN** the Settings toggles SHALL reflect the new state on next render without manual re-sync

### Requirement: Language Selection Sheet Dismiss And Error Surfacing
The language selection sheet SHALL close after a selection is applied (or is a no-op), and a non-`ConnectError` failure SHALL be surfaced rather than leaving the row silently stale.

#### Scenario: Sheet closes after successful change
- **WHEN** a user selects a language different from the current one and the change is applied successfully
- **THEN** the selection sheet SHALL close after the change is applied
- **AND** the Language row SHALL reflect the new language

#### Scenario: Re-selecting the current language closes without an RPC
- **WHEN** a user selects the language already in effect
- **THEN** the sheet SHALL close and no RPC SHALL be issued

#### Scenario: Non-ConnectError failure is surfaced
- **WHEN** applying a language change raises a non-`ConnectError` (a programmer error reaching the handler)
- **THEN** the error SHALL propagate to the global error boundary
- **AND** the UI SHALL NOT present a silently dismissed sheet with the row still showing the old language as if the change succeeded

### Requirement: Settings Page Header Label
The Settings page header SHALL render the invariant English brand label "Settings" — the Layer B navigation tab label — rather than a locale-switched title string, so that the Settings header is consistent with the tab pages whose headers all bind an invariant `nav.*` label.

#### Scenario: Header reads "Settings" regardless of active locale
- **WHEN** the Settings page is loaded with the active locale set to Japanese
- **THEN** the page header SHALL display "Settings"
- **AND** it SHALL NOT display a Japanese translation of the header (e.g. "設定")

#### Scenario: Header shares the navigation tab label source
- **WHEN** the Settings route renders its `page-header`
- **THEN** the header title SHALL resolve from the same invariant label that names the page header's Settings entry (the `nav.settings` key, "Settings" in both JA and EN locales)
- **AND** the header SHALL NOT depend on a separate localized `settings.title` string

### Requirement: The fan edits their name and phone number

The settings screen SHALL show the fan's saved full name and phone number, say that they are shown on the face of the fan's tickets, and let the fan change them with UserService.Update. A phone number SHALL be entered in the domestic form and sent in E.164 form.

#### Scenario: Fan changes their phone number
- **WHEN** a fan with the saved phone number 090-1234-5678 enters 090-9876-5432 and saves
- **THEN** UserService.Update is called with `+819098765432` and the screen shows the new number

#### Scenario: No details saved yet
- **WHEN** a fan who never gave a name or phone number opens the settings screen
- **THEN** both fields are empty and can be filled in

### Requirement: Guest hero offers sign-in help

The guest call-to-action hero at the top of the Settings page SHALL show a "can't sign in" text link below its sign-in and sign-up actions that opens the passkey recovery screen.

#### Scenario: Guest opens sign-in help from Settings

- **WHEN** an unauthenticated user taps "can't sign in" in the Settings guest hero
- **THEN** the app navigates to `/passkey-recovery`

### Requirement: Passkey management requires a recent sign-in

For a signed-in fan, the ACCOUNT section SHALL show a Passkeys row that opens passkey management. Opening passkey management SHALL send the fan to the hosted login to sign in again, every time, however recently the fan signed in, and SHALL return them to passkey management afterwards. The access gained this way SHALL last only while passkey management stays open: leaving it, or reloading the app, SHALL require signing in again.

#### Scenario: Recent sign-in

- **WHEN** a fan who signed in 2 minutes ago opens the Passkeys row
- **THEN** the hosted login asks the fan to sign in again, and after it succeeds passkey management opens

#### Scenario: Older sign-in

- **WHEN** a fan who signed in 3 days ago opens the Passkeys row
- **THEN** the hosted login asks the fan to sign in again, and after it succeeds passkey management opens

#### Scenario: Re-opening after leaving

- **WHEN** the fan leaves passkey management and opens it again a minute after signing in again
- **THEN** the hosted login asks the fan to sign in again

### Requirement: Passkey management lists, adds and removes passkeys

Passkey management SHALL list every passkey registered for the fan's identity. Each passkey SHALL be shown by its provider name when its Passkey record has one, otherwise by its name, or "Passkey" when it has neither, and SHALL show the date it was added when it has a Passkey record. A passkey without a record (added before records were kept, or whose change was never announced) SHALL be shown by its name without a date. It SHALL offer to add a passkey on the device in hand, which opens the hosted login to create it and returns to passkey management, where the new passkey is listed. When the fan comes back to passkey management from that hosted login, whether the creation finished or the fan went back, passkey management SHALL compare the list with the one before leaving and SHALL say the outcome once per attempt in a snack: that the passkey was added, or that no passkey was added and that a device whose passkey manager already holds one can sign in with it as it is. Before the fan leaves, passkey management SHALL say that a creation that does not finish is left with the hosted login's back action, which returns here. Next to the add action, passkey management SHALL say that no passkey is created when the device's passkey manager already holds one for the account, and that the device can then sign in with it as it is. Each listed passkey SHALL offer removal behind a confirmation that says the passkey is also kept by the device's passkey manager and should be deleted there too; after confirming, the passkey SHALL no longer be listed and SHALL no longer sign in. When only one passkey is listed, its removal SHALL be disabled with the explanation that the last passkey cannot be removed and that another passkey must be added first. When the list cannot be read or a removal fails, passkey management SHALL say so and offer to try again, and SHALL keep the list as it was.

#### Scenario: Two passkeys

- **WHEN** a fan with passkeys named `Apple iPhone, iOS, Mobile Safari` and `Windows, Chrome` opens passkey management
- **THEN** both are listed with those names and both offer removal

#### Scenario: Recorded passkey

- **WHEN** a listed passkey named `Google Pixel 9, Android, Chrome` has a Passkey record with provider name `Google Password Manager`, added on 2026-10-20
- **THEN** it is shown as `Google Password Manager` with the date 2026-10-20

#### Scenario: Passkey without a record

- **WHEN** a listed passkey named `Windows, Chrome` has no Passkey record
- **THEN** it is shown as `Windows, Chrome` without a date

#### Scenario: Add a passkey on this device

- **WHEN** the fan taps add and creates a passkey on the device in hand
- **THEN** passkey management lists one more passkey

#### Scenario: Remove a passkey

- **WHEN** the fan removes `Windows, Chrome` and confirms
- **THEN** it is no longer listed and can no longer sign in to the account

#### Scenario: Last passkey

- **WHEN** only one passkey is listed
- **THEN** its removal is disabled and the explanation is shown

#### Scenario: Removal fails

- **WHEN** a removal fails
- **THEN** passkey management says so, offers to try again and still lists the passkey

#### Scenario: Passkey added

- **WHEN** the fan comes back from the hosted login with one more passkey listed than before
- **THEN** a snack says the passkey was added

#### Scenario: Passkey not added

- **WHEN** the fan comes back from the hosted login, by finishing or by going back, and the list is the same as before
- **THEN** a snack says no passkey was added and that a device whose passkey manager already holds one can sign in with it as it is

#### Scenario: Device that already holds a passkey

- **WHEN** a fan views passkey management
- **THEN** the add action is accompanied by the note that no passkey is created when the device's passkey manager already holds one for the account

### Requirement: The verification badge shows the current state

For a signed-in fan, the email verification badge SHALL reflect the identity provider's current state of the address, read again each time Settings opens and each time the fan returns to its tab, not only the state at sign-in. In Japanese the badge SHALL read 確認済み for a verified address and 未確認, with the resend action, for an address that is not verified, the word the verification email and the email verification screen use. When the address has been verified since sign-in, on this device or another, the badge SHALL show 確認済み and the resend action SHALL disappear. When the state cannot be read, the badge SHALL keep the last known state.

#### Scenario: Verified on another device

- **WHEN** a fan signed in on a laptop before verifying, verifies from their phone, and returns to Settings on the laptop
- **THEN** the badge shows 確認済み and no resend action is shown

#### Scenario: Not yet verified

- **WHEN** a fan whose address is not verified opens Settings in Japanese
- **THEN** the badge shows 未確認 next to the resend action

#### Scenario: State cannot be read

- **WHEN** reading the current state fails
- **THEN** the badge keeps showing the last known state

### Requirement: Delete account entry below Sign Out

For a signed-in fan, Settings SHALL show a 「アカウントを削除」 (Delete account) control below the Sign Out control, in a group of its own at least 24px away from it, that opens the withdrawal screen. It SHALL NOT be shown to a guest.

#### Scenario: Signed-in fan

- **WHEN** a signed-in fan views Settings
- **THEN** the Delete account control is shown below Sign Out, apart from it, and opens the withdrawal screen

#### Scenario: Guest

- **WHEN** a guest views Settings
- **THEN** no Delete account control is shown
