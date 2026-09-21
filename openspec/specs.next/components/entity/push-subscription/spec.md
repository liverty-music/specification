# Push Subscription

## Purpose

Defines the backend `PushNotificationService` capability that registers, retrieves, and removes a browser's Web Push subscription on a per-`(user_id, endpoint)` basis. The service models subscriptions as type-safe `PushSubscription` entities, enforces strict per-browser scoping (no bulk-per-user mutation in the externally triggered surface), and supports a client-side self-healing flow that recovers from the "browser has subscription but backend does not" divergence without prompting the user.

## Requirements

### Requirement: PushSubscription entity model

The system SHALL represent a browser Web Push subscription as a `PushSubscription` entity in `liverty_music.entity.v1`, composed of type-safe wrapper messages rather than inline primitive fields.

#### Scenario: PushSubscription aggregate shape

- **WHEN** a `PushSubscription` entity is serialized
- **THEN** it SHALL carry `id` (`PushSubscriptionId`, UUID wrapper), `user_id` (`UserId`), `endpoint` (`PushEndpoint`), and `keys` (`PushKeys`)
- **AND** `PushSubscriptionId.value` SHALL be a UUID string validated by `protovalidate` `string.uuid`
- **AND** `PushEndpoint.value` SHALL be validated as a URI with `max_len = 2048`
- **AND** `PushKeys` SHALL carry `p256dh` (Base64url, `min_len = 1`, `max_len = 256`) and `auth` (Base64url, `min_len = 1`, `max_len = 64`)

#### Scenario: No inline primitive subscription fields in request messages

- **WHEN** any RPC in `PushNotificationService` accepts or returns push subscription materials
- **THEN** the materials SHALL be expressed via `PushEndpoint`, `PushKeys`, or `PushSubscription` entity messages
- **AND** raw `string endpoint`, `string p256dh`, or `string auth` fields SHALL NOT appear directly in request or response messages
