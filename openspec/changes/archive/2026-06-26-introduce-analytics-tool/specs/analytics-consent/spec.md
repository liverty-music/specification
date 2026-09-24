## ADDED Requirements

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
