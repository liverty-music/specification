## ADDED Requirements

### Requirement: Analytics operates under an EU-adequacy opt-out model, not a consent gate
The system SHALL treat identified product analytics as **enabled by default** for authenticated users and SHALL provide an always-available opt-out, rather than gating analytics behind an explicit opt-in. Cross-border transfer of personal data to PostHog (Klant Solutions B.V., Netherlands) is permitted without per-user statutory consent under APPI Article 28, because the EU has held the Personal Information Protection Commission's adequacy designation since January 2019. The obligation that survives adequacy is the **notification or publication of the purpose of use (利用目的の通知・公表)**, which the system SHALL satisfy through the privacy policy and an always-available opt-out control, not through a signup consent screen.

The platform is pre-launch; there is no previously-collected opt-in/decline state to migrate, so the default-on posture applies uniformly to all accounts at launch.

#### Scenario: Authenticated user is analysed by default
- **WHEN** a user is authenticated via Zitadel and has never changed the analytics setting
- **THEN** the application SHALL treat the analytics opt-out state as off (i.e. analytics enabled)
- **AND** the application SHALL call `posthog.identify(user.id.value, properties)` after `UserService.GetMe` returns
- **AND** the application SHALL enable persistent-storage PostHog mode

#### Scenario: Purpose of use is published rather than gated
- **WHEN** the application begins transferring analytics data to PostHog Cloud EU
- **THEN** the privacy policy SHALL name PostHog (Klant Solutions B.V., Netherlands) as the third-party recipient and enumerate the purpose of the cross-border transfer
- **AND** the application SHALL NOT block analytics on an affirmative pre-collection consent action
- **AND** the application SHALL surface an opt-out entry point in settings that is reachable without re-onboarding

---

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

### Requirement: Full non-PII catalogue is captured anonymously before and without identification
Before a user is identified — anonymous visitors, and authenticated users who have opted out of analytics — the application SHALL capture the **full non-PII event catalogue** (not a restricted allowlist), subject to: no property linking the events to a real account SHALL be sent, and the events SHALL carry no `distinct_id` mapped to a user identity. The earlier closed pre-consent allowlist (`page.viewed`, `account.signup.started` only) is removed.

Persistence differs by user state, because the two states carry different privacy expectations:
- **Anonymous visitors** (never identified): persistence MAY use `localStorage` with an anonymous identifier so anonymous funnels survive page reloads.
- **Opted-out authenticated users**: persistence SHALL be memory-only, consistent with the opt-out behaviour (see the "Anonymous behaviour is merged into the identified profile on login" and "Analytics opt-out state is persisted" requirements). A user who has actively opted out SHALL NOT have an anonymous identifier persisted to `localStorage`.

#### Scenario: Anonymous visitor's full discovery behaviour is captured
- **WHEN** an unidentified visitor browses the landing page, searches artists, and views artist detail
- **THEN** the application MAY emit `page.viewed`, `artist.search`, `artist.discovery.viewed`, and any other non-PII catalogue event with an anonymous identifier
- **AND** the application MAY persist the anonymous identifier in `localStorage`
- **AND** no event SHALL include the user's email, Zitadel `sub`, `UserId`, or any other account-mapped identifier

#### Scenario: Opted-out authenticated user generates only anonymous telemetry
- **WHEN** an authenticated user has turned the Analytics toggle off
- **THEN** the application SHALL NOT call `posthog.identify` with the user's `UserId`
- **AND** any events emitted SHALL use an anonymous identifier
- **AND** persistence SHALL be memory-only (no anonymous identifier persisted to `localStorage`)
- **AND** no link SHALL be created between the user's identity and the anonymous PostHog profile

---

### Requirement: Anonymous behaviour is merged into the identified profile on login
When a previously-anonymous user is identified (login or signup, analytics not opted out), the application SHALL call `posthog.identify(user.id.value, ...)` such that the pre-identification anonymous event history is **merged into** the identified profile, so pre-signup discovery behaviour stays connected to post-signup conversion. The application SHALL NOT call `posthog.reset()` on the normal identify path; `reset()` is reserved for sign-out and for analytics opt-out, where severing the identity link is the intended effect.

#### Scenario: Pre-signup discovery connects to post-signup conversion
- **WHEN** an anonymous visitor follows artists, then signs up and is identified
- **THEN** the anonymous events captured before signup SHALL be attributed to the identified `UserId` profile
- **AND** a funnel from anonymous `artist.discovery.viewed` to identified `ticket.purchase.completed` SHALL be constructible for that user

#### Scenario: Opt-out severs the link rather than merging
- **WHEN** an identified user turns the Analytics toggle off
- **THEN** the application SHALL call `posthog.opt_out_capturing()` and `posthog.reset()`
- **AND** the application SHALL revert persistence to memory-only
- **AND** subsequent navigation SHALL NOT emit any identified PostHog event

---

### Requirement: Sensitive personal information and minor-identifying data are structurally excluded
The system SHALL NOT capture APPI 要配慮個人情報 (sensitive personal information: race, creed, social status, medical history, criminal record, history of being a crime victim, physical/mental disability, and the other statutory categories) through any analytics path, including event properties and session replay. Because an opt-out model cannot lawfully cover sensitive categories (which always require explicit opt-in and cannot be acquired via opt-out) nor reliably stand in for guardian consent for minors, the exclusion SHALL be enforced in code — through the event-property allowlist and replay masking — not by relying on consent. The system SHALL NOT capture data that identifies a user as a minor (e.g. precise birth date or age); age-related properties, if any, SHALL be bucketized.

#### Scenario: A sensitive property is rejected before emission
- **WHEN** application code attempts to emit an event whose properties include a sensitive category or a precise birth date
- **THEN** the AnalyticsService SHALL reject or strip the offending property before contacting PostHog
- **AND** the AnalyticsService SHALL log the rejection for debugging

#### Scenario: Session replay never records a sensitive region
- **WHEN** a screen renders content in a sensitive or minor-identifying category
- **THEN** that region SHALL be marked so session replay masks or blocks it
- **AND** the recorded replay SHALL NOT reveal the sensitive content

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
- **AND** the application SHALL emit subsequent events normally
