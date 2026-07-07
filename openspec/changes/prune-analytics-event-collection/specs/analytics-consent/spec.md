## MODIFIED Requirements

### Requirement: Full non-PII catalogue is captured anonymously before identification
Before a user is identified — anonymous visitors who have not opted out — the application SHALL capture the **full non-PII event catalogue** (not a restricted allowlist), subject to: no property linking the events to a real account SHALL be sent, and the events SHALL carry no `distinct_id` mapped to a user identity. Persistence MAY use `localStorage` with an anonymous identifier so anonymous funnels survive page reloads. There is no pre-consent allowlist: every `active`, non-PII catalogue event is eligible for anonymous capture.

This requirement covers only the pre-identification anonymous state. A user who has explicitly opted out is a different state: `opt_out_capturing()` suppresses all capture, so an opted-out user emits no telemetry of any kind (see "Analytics opt-out state is persisted and user-controllable from settings").

#### Scenario: Anonymous visitor's full discovery behaviour is captured
- **WHEN** an unidentified visitor who has not opted out searches artists and opens a concert detail sheet
- **THEN** the application MAY emit `artist.search`, `concert.detail.viewed`, `notification.requested`, and any other `active` non-PII catalogue event with an anonymous identifier
- **AND** the application MAY persist the anonymous identifier in `localStorage`
- **AND** no event SHALL include the user's email, Zitadel `sub`, `UserId`, or any other account-mapped identifier

#### Scenario: Opted-out authenticated user generates no telemetry
- **WHEN** an authenticated user has turned the Analytics toggle off
- **THEN** the application SHALL have called `posthog.opt_out_capturing()`, which suppresses all capture
- **AND** the application SHALL NOT emit any PostHog event — neither identified nor anonymous — while opted out
- **AND** the application SHALL NOT call `posthog.identify` with the user's `UserId`
- **AND** persistence SHALL be memory-only (no anonymous identifier persisted to `localStorage`)
- **AND** no link SHALL be created between the user's identity and any PostHog profile

### Requirement: Anonymous behaviour is merged into the identified profile on login
When a previously-anonymous user is identified (login or signup, analytics not opted out), the application SHALL call `posthog.identify(user.id.value, ...)` such that the pre-identification anonymous event history is **merged into** the identified profile, so pre-signup discovery behaviour stays connected to post-signup conversion. The application SHALL NOT call `posthog.reset()` on the normal identify path; `reset()` is reserved for sign-out and for analytics opt-out, where severing the identity link is the intended effect.

#### Scenario: Pre-signup discovery connects to post-signup conversion
- **WHEN** an anonymous visitor searches and opens concert details, then signs up and is identified
- **THEN** the anonymous events captured before signup SHALL be attributed to the identified `UserId` profile
- **AND** a funnel from anonymous `artist.search` / `concert.detail.viewed` to identified `artist.follow.completed` SHALL be constructible for that user
