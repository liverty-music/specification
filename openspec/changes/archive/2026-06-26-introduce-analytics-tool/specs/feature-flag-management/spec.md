## ADDED Requirements

### Requirement: Feature flags require a documented description record on creation
Every PostHog feature flag SHALL be created with a description block containing: `OWNER` (GitHub user), `HYPOTHESIS` (one-line statement of the assumption), `KPI` (the metric the flag will move), `KILL_DATE` (creation date plus 90 days), and `ISSUE` (URL of the tracking GitHub issue). Flags lacking any of these fields SHALL be considered non-compliant.

#### Scenario: Engineer creates a new feature flag
- **WHEN** an engineer creates a new feature flag in PostHog
- **THEN** the flag description SHALL include `OWNER`, `HYPOTHESIS`, `KPI`, `KILL_DATE`, and `ISSUE` fields
- **AND** the `KILL_DATE` SHALL be no later than the creation date plus 90 calendar days
- **AND** the `ISSUE` URL SHALL point to an existing open GitHub issue

#### Scenario: Existing flag is reviewed for compliance
- **WHEN** the monthly stale-flag review runs
- **THEN** the review SHALL list every flag whose description omits any required field
- **AND** the review SHALL list every flag whose `KILL_DATE` has passed
- **AND** the review SHALL list every flag at 0% or 100% rollout for more than 30 days

---

### Requirement: Significant experiments evaluate flags only after `identify`
Feature flags whose variants influence revenue, conversion, or otherwise affect identified-user behaviour SHALL be evaluated only after `posthog.identify(...)` has completed for the current user. Flags evaluated against anonymous identifiers SHALL be limited to release toggles, geographic gates, and emergency kill switches whose variants do not depend on per-user state.

#### Scenario: Recommendation algorithm experiment is gated post-identify
- **WHEN** a user opens the discovery page while not yet identified
- **THEN** the application SHALL NOT evaluate the `recommendation-algo-v2` experiment flag
- **AND** the application SHALL render the control variant
- **AND** once `posthog.identify` completes, the application SHALL re-evaluate the flag and render the assigned variant

#### Scenario: Release toggle evaluates against anonymous user
- **WHEN** an anonymous user visits a page gated by the `new-landing-page` release toggle
- **THEN** the application MAY evaluate the flag with the anonymous identifier
- **AND** the evaluation SHALL be stable for the current device for the duration of the rollout

---

### Requirement: Flag evaluation always has a default value on PostHog unavailability
Every feature-flag evaluation in the frontend and backend SHALL specify a default value that the system uses when PostHog is unreachable, when the SDK has not yet loaded flag definitions, or when the flag does not exist. The default SHALL represent the safe, conservative behaviour.

#### Scenario: PostHog is unreachable during backend flag evaluation
- **WHEN** the backend evaluates a feature flag and the PostHog API is unreachable
- **THEN** the evaluator SHALL return the default value specified at the call site
- **AND** the evaluator SHALL NOT block the handler waiting for PostHog
- **AND** the evaluator SHALL log the failure for observability

#### Scenario: Frontend evaluates a flag before SDK has loaded definitions
- **WHEN** the frontend calls `AnalyticsService.getFeatureFlag(flagKey, defaultValue)` before PostHog has finished loading flag definitions
- **THEN** the call SHALL return the supplied default value synchronously
- **AND** subsequent calls after the SDK loads SHALL return the resolved value
- **AND** the frontend SHALL NOT block UI rendering on flag resolution unless the flag is explicitly marked as render-blocking

---

### Requirement: Frontend bootstraps flags from the last-known persisted value
On initialisation, the frontend SHALL bootstrap PostHog feature-flag values from the last-known values persisted in `localStorage` so that the first render uses the same variant the user saw on the previous session, then refresh from PostHog asynchronously.

#### Scenario: Returning user sees the same variant on first render
- **WHEN** a returning user with a previously assigned `recommendation-algo-v2` variant opens the app
- **THEN** the application SHALL read the persisted variant from `localStorage` during bootstrap
- **AND** the application SHALL render with that variant before contacting PostHog
- **AND** the application SHALL refresh flag values from PostHog in the background and update only if the assigned variant changes

#### Scenario: First-time user gets default until PostHog responds
- **WHEN** a user with no persisted flag values opens the app for the first time
- **THEN** the application SHALL render with the default value for each flag
- **AND** once PostHog returns resolved values, the application SHALL update reactive views that depend on flags

---

### Requirement: Stale flags are reviewed monthly and decided at or before the kill date
A monthly review SHALL identify flags whose `KILL_DATE` has passed and flags whose rollout has been at 0% or 100% for more than 30 days. Each identified flag SHALL be either removed (rollout finalised, code path cleaned) or extended with a new documented `KILL_DATE`.

#### Scenario: Flag at 100% rollout for 35 days appears in monthly review
- **WHEN** the monthly stale-flag review runs on day 35 after a flag reached 100% rollout
- **THEN** the review report SHALL list the flag as a removal candidate
- **AND** the owner SHALL either delete the flag and remove the corresponding code path or extend the `KILL_DATE` with documented justification

#### Scenario: Flag past its `KILL_DATE` is escalated
- **WHEN** the monthly review runs and a flag's `KILL_DATE` has passed
- **THEN** the review SHALL escalate the flag to the owner and to the project lead
- **AND** an open GitHub issue SHALL be created to track resolution within the following review cycle
