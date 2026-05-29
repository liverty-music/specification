## ADDED Requirements

### Requirement: Cross-border data-transfer consent is collected at signup
The system SHALL collect explicit consent for cross-border transfer of personal data to PostHog (Netherlands) as the final step of the signup flow before the user reaches the authenticated experience. The consent screen SHALL name PostHog as the third-party recipient and link to the privacy policy enumerating the purpose of transfer.

#### Scenario: New user completes signup and reaches consent screen
- **WHEN** a new user completes account creation in Zitadel and is redirected back to the Aurelia 2 PWA
- **THEN** the application SHALL render a consent screen before the main authenticated UI
- **AND** the consent screen SHALL identify PostHog (Klant Solutions B.V., Netherlands) as the third-party recipient
- **AND** the consent screen SHALL link to the privacy policy section enumerating the purpose of the cross-border transfer

#### Scenario: User declines consent on the signup screen
- **WHEN** the user selects "Set up later" on the consent screen
- **THEN** the application SHALL proceed to the authenticated experience without enabling identified PostHog tracking
- **AND** the application SHALL persist a consent record marking analytics as not granted
- **AND** the application SHALL display an entry point in settings for the user to grant consent later

---

### Requirement: Consent is collected per purpose with separate toggles
The consent screen SHALL present at least two purpose-specific toggles: one for product analytics (PostHog) and one for marketing measurement. Each toggle SHALL have its own default value, its own descriptive label, and its own privacy-policy anchor.

#### Scenario: Both toggles default to off (explicit opt-in)
- **WHEN** the consent screen is rendered for the first time
- **THEN** the analytics consent toggle SHALL default to off (explicit opt-in)
- **AND** the marketing-measurement consent toggle SHALL default to off (explicit opt-in)
- **AND** each toggle SHALL be independently controllable
- **AND** the application SHALL NOT treat an absent toggle interaction as consent

#### Scenario: User declines analytics but accepts marketing measurement
- **WHEN** the user toggles analytics off and marketing on, then confirms
- **THEN** the application SHALL record consent for marketing measurement only
- **AND** PostHog identified tracking SHALL remain disabled

---

### Requirement: Anonymous pre-consent telemetry is restricted to non-PII memory-only mode
Before consent is granted, the application SHALL restrict any telemetry emitted to PostHog to a closed allowlist of anonymous-funnel events that satisfy all of the following: persistence MUST be memory-only (no cookies, no `localStorage`), IP collection MUST be disabled at the SDK level, and no `distinct_id` linkable to a user identity SHALL be sent.

The pre-consent allowlist SHALL be limited to:
- `page.viewed` — landing-page and discovery-page navigation
- `account.signup.started` — the user clicks the signup CTA, which necessarily precedes the consent screen since the consent screen is itself the final step of the signup flow

Any other event emitted before consent SHALL be rejected by the AnalyticsService at the call site. The allowlist SHALL be encoded in code, not merely documented.

#### Scenario: First-visit anonymous user emits a page view
- **WHEN** an unidentified user visits the landing page for the first time
- **THEN** the application MAY initialise PostHog with `persistence: 'memory'` and `ip: false`
- **AND** the application MAY emit a `page.viewed` event with an anonymous identifier
- **AND** the application SHALL NOT set any persistent cookie or `localStorage` entry for PostHog

#### Scenario: Anonymous user starts signup before the consent screen renders
- **WHEN** an unidentified user clicks the signup CTA
- **THEN** the application MAY emit an `account.signup.started` event with an anonymous identifier
- **AND** the event payload SHALL include only the `source` enum (e.g. `landing`, `cta`, `deep_link`)
- **AND** the application SHALL apply the same memory-only persistence and IP-disabled rules as for `page.viewed`

#### Scenario: Pre-consent event outside the allowlist is rejected
- **WHEN** application code attempts to emit any event other than `page.viewed` or `account.signup.started` before consent is granted
- **THEN** the AnalyticsService SHALL drop the event without contacting PostHog
- **AND** the AnalyticsService SHALL log the rejected event name for debugging

#### Scenario: Pre-consent event does not include identifying properties
- **WHEN** the application emits a pre-consent anonymous event
- **THEN** the event payload SHALL NOT include the user's email, Zitadel `sub`, `UserId`, or any other identifier mapped to a real account
- **AND** the event payload SHALL NOT include precise geolocation finer than country

---

### Requirement: Consent state is persisted and user-controllable from settings
The application SHALL persist the user's consent state and SHALL provide a settings control through which the user can revoke or grant consent at any time after signup. Revoking consent SHALL stop further identified tracking immediately.

#### Scenario: User revokes analytics consent from settings
- **WHEN** the user toggles analytics consent off in the settings page
- **THEN** the application SHALL call `posthog.opt_out_capturing()` immediately
- **AND** the application SHALL persist the updated consent state
- **AND** subsequent navigation SHALL NOT emit any PostHog event

#### Scenario: User grants analytics consent from settings after initial decline
- **WHEN** a user who previously declined consent toggles analytics on in settings
- **THEN** the application SHALL invoke deferred PostHog initialisation if not already initialised
- **AND** the application SHALL call `posthog.identify(user.id.value, properties)` with the user's `UserId`
- **AND** the application SHALL emit subsequent events normally

---

### Requirement: Identified-mode PostHog initialisation is gated on consent
The application SHALL NOT call `posthog.identify(...)` or enable persistent-storage PostHog mode until the user has granted analytics consent for the current device.

#### Scenario: Logged-in user without consent generates only anonymous telemetry
- **WHEN** a user is authenticated via Zitadel but has analytics consent set to false on the current device
- **THEN** the application SHALL NOT call `posthog.identify` with the user's `UserId`
- **AND** any PostHog events emitted SHALL use an anonymous identifier with memory-only persistence
- **AND** no link SHALL be created between the user's identity and the anonymous PostHog profile
