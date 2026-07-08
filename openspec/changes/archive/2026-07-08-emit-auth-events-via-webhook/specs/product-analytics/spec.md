## ADDED Requirements

### Requirement: Account authentication events are emitted server-side

The system SHALL emit account authentication analytics events from the backend, attributed to the platform-internal `UserId` (UUID), not the Zitadel `sub` claim.

`account.login` SHALL be emitted **once per user-initiated login** and SHALL NOT be emitted on a token refresh (a silent `refresh_token` grant is not a login). The login signal SHALL be derived from a backend source that is login-specific and that structurally cannot alter the authentication request/response. Specifically, it SHALL be derived from a Zitadel Actions v2 **`event` execution** bound to the `session.user.checked` event — a fire-and-forget execution that fires after the login event is persisted, carries the logging-in user at `payload.userID`, and cannot manipulate any API request or response. This event type was determined empirically (via the Events API): it fires once per interactive login through the hosted Login UI, does not fire on a `refresh_token` grant, and does not fire for machine (jwt_profile) token grants. The source SHALL NOT be a `request`/`response` (method) execution, because those replace the API payload with the webhook return and can break sign-in. The login metric SHALL never be inflated by refreshes, and the source SHALL NOT rely on any per-request runtime discrimination heuristic.

Account signup SHALL be represented by the existing `user.created` event. The system SHALL NOT emit a separate `account.signup.completed` event, because signup occurs at the same instant as `user.created`; emitting both would double-count signups.

The webhook handler on the login path SHALL NOT call the PostHog SDK directly. It SHALL publish a domain event (NATS subject `ACCOUNT.login`) that the `analytics-consumer` forwards to PostHog, and the publish SHALL be non-blocking and non-fatal so that a failure on the analytics path does not break token issuance or login.

#### Scenario: A user-initiated login emits `account.login` exactly once

- **WHEN** a user completes an interactive (fresh) authentication and Zitadel stores the `session.user.checked` event, invoking the backend webhook via the `event` execution
- **THEN** the backend SHALL resolve the Zitadel user (from `payload.userID`) to the platform `UserId` (via the existing user lookup)
- **AND** the backend SHALL emit exactly one `account.login` event with `distinct_id` set to that `UserId`
- **AND** the event SHALL NOT carry the Zitadel `sub`, the user's email, or any other PII in its properties

#### Scenario: A token refresh does NOT emit `account.login`

- **WHEN** the backend mints an access token via a silent `refresh_token` grant (no fresh interactive authentication)
- **THEN** the backend SHALL NOT emit an `account.login` event
- **AND** the login count in analytics SHALL reflect user-initiated logins only, excluding refreshes

#### Scenario: Signup is represented by `user.created`, not a duplicate event

- **WHEN** a new user record is created at signup
- **THEN** the backend SHALL emit `user.created` as the signup signal
- **AND** the backend SHALL NOT emit a separate `account.signup.completed` event for the same signup

#### Scenario: Analytics failure on the login path does not break login

- **WHEN** the analytics publish (NATS) on the login `event`-execution webhook path fails
- **THEN** the webhook handler SHALL log the failure and continue
- **AND** login SHALL succeed unaffected by the analytics-path failure (the `event` execution is fire-and-forget; its return never reaches the auth flow)
