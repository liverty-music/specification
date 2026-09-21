# Delete

## Purpose

Defines the backend `PushNotificationService` capability that registers, retrieves, and removes a browser's Web Push subscription on a per-`(user_id, endpoint)` basis. The service models subscriptions as type-safe `PushSubscription` entities, enforces strict per-browser scoping (no bulk-per-user mutation in the externally triggered surface), and supports a client-side self-healing flow that recovers from the "browser has subscription but backend does not" divergence without prompting the user.

## Requirements

### Requirement: Delete RPC removes only the specified browser's subscription

The system SHALL expose `PushNotificationService.Delete` to remove the push subscription uniquely identified by `(user_id, endpoint)`. The operation SHALL be idempotent.

#### Scenario: Successful deletion

- **WHEN** an authenticated client calls `Delete` with its own `user_id` and the `PushEndpoint` of one of its registered browsers
- **THEN** the backend SHALL remove exactly that row
- **AND** other rows belonging to the same user (other browsers) SHALL be left untouched

#### Scenario: Idempotent deletion

- **WHEN** `Delete` is called with a `(user_id, endpoint)` pair that does not match any row
- **THEN** the service SHALL return a successful empty response

#### Scenario: Caller attempts to delete another user's subscription

- **WHEN** `Delete` is called with a `user_id` that differs from the userID extracted from the authenticated session
- **THEN** the service SHALL return `PERMISSION_DENIED`
- **AND** no rows SHALL be deleted

#### Scenario: Unauthenticated request

- **WHEN** `Delete` is called without a valid user session
- **THEN** the service SHALL return `UNAUTHENTICATED`
