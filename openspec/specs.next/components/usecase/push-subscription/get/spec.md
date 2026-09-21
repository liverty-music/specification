# Get

## Purpose

Defines the backend `PushNotificationService` capability that registers, retrieves, and removes a browser's Web Push subscription on a per-`(user_id, endpoint)` basis. The service models subscriptions as type-safe `PushSubscription` entities, enforces strict per-browser scoping (no bulk-per-user mutation in the externally triggered surface), and supports a client-side self-healing flow that recovers from the "browser has subscription but backend does not" divergence without prompting the user.

## Requirements

### Requirement: Get RPC returns the subscription for a specific browser

The system SHALL expose `PushNotificationService.Get` to retrieve the push subscription uniquely identified by the pair `(user_id, endpoint)`.

#### Scenario: Successful retrieval

- **WHEN** an authenticated client calls `Get` with its own `user_id` and a `PushEndpoint` that matches an existing row for that user
- **THEN** the service SHALL return the matching `PushSubscription` entity

#### Scenario: Subscription not found

- **WHEN** `Get` is called with a `user_id` / `endpoint` pair that does not match any row
- **THEN** the service SHALL return `NOT_FOUND`
- **AND** the response SHALL NOT carry an empty `PushSubscription` placeholder

#### Scenario: Caller attempts to query another user's subscription

- **WHEN** `Get` is called with a `user_id` that differs from the userID extracted from the authenticated session
- **THEN** the service SHALL return `PERMISSION_DENIED`
- **AND** the service SHALL NOT leak whether a subscription exists for that user/endpoint

#### Scenario: Unauthenticated request

- **WHEN** `Get` is called without a valid user session
- **THEN** the service SHALL return `UNAUTHENTICATED`
