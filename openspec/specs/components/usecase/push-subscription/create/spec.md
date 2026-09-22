# Create

## Purpose

Defines the backend `PushNotificationService` capability that registers, retrieves, and removes a browser's Web Push subscription on a per-`(user_id, endpoint)` basis. The service models subscriptions as type-safe `PushSubscription` entities, enforces strict per-browser scoping (no bulk-per-user mutation in the externally triggered surface), and supports a client-side self-healing flow that recovers from the "browser has subscription but backend does not" divergence without prompting the user.

## Requirements

### Requirement: Create RPC registers the calling browser's subscription

The system SHALL expose `PushNotificationService.Create` to register a browser push subscription for the authenticated user. The operation SHALL be an UPSERT keyed by `endpoint`.

#### Scenario: Successful registration

- **WHEN** an authenticated client calls `Create` with a valid `PushEndpoint` and `PushKeys`
- **THEN** the backend SHALL persist a `push_subscriptions` row associating the user with that endpoint
- **AND** if a row with the same endpoint already exists, the keys SHALL be updated (UPSERT)
- **AND** the response SHALL return the resulting `PushSubscription` entity

#### Scenario: Unauthenticated request

- **WHEN** `Create` is called without a valid user session
- **THEN** the service SHALL return `UNAUTHENTICATED`

#### Scenario: Invalid request payload

- **WHEN** `Create` is called with a missing or malformed `PushEndpoint` or `PushKeys`
- **THEN** the service SHALL return `INVALID_ARGUMENT`
