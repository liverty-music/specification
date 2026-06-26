## ADDED Requirements

### Requirement: Account authentication events are emitted server-side

The system SHALL emit account authentication analytics events from the backend, attributed to the platform-internal `UserId` (UUID), not the Zitadel `sub` claim.

`account.login` SHALL be emitted **once per user-initiated login** and SHALL NOT be emitted on a token refresh (a silent `refresh_token` grant is not a login). The login signal SHALL be derived from a backend source that is login-specific — preferably one that structurally cannot fire on a token refresh (e.g. a Zitadel login-specific session-created Action). A token-issuance webhook (e.g. `pre_access_token`) MAY be used as the source ONLY where its payload is verified to expose a reliable discriminator that separates fresh interactive authentication from a `refresh_token` grant. The choice of source SHALL be a build-time decision grounded in verified payload capability, NOT a per-request runtime guess; the login metric SHALL never be inflated by refreshes.

Account signup SHALL be represented by the existing `user.created` event. The system SHALL NOT emit a separate `account.signup.completed` event, because signup occurs at the same instant as `user.created`; emitting both would double-count signups.

The webhook handler on the login path SHALL NOT call the PostHog SDK directly. It SHALL publish a domain event (NATS subject `ACCOUNT.login`) that the `analytics-consumer` forwards to PostHog, and the publish SHALL be non-blocking and non-fatal so that a failure on the analytics path does not break token issuance or login.

#### Scenario: A user-initiated login emits `account.login` exactly once

- **WHEN** a user completes an interactive (fresh) authentication and the backend mints the resulting access token
- **THEN** the backend SHALL resolve the Zitadel `sub` to the platform `UserId` (via the existing user lookup)
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

- **WHEN** the analytics publish (NATS) on the fresh-authentication path fails
- **THEN** the webhook handler SHALL log the failure and continue
- **AND** token issuance / login SHALL succeed unaffected by the analytics-path failure
