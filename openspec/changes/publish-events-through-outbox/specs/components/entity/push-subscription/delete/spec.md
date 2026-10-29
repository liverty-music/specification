## ADDED Requirements

### Requirement: A removed subscription is announced with the change

When Delete removes a PushSubscription, it SHALL announce the PushSubscription as unsubscribed, carrying it as it was, together with the removal: both are stored or neither is. When Delete removes nothing, it SHALL announce nothing. When the announcement cannot be recorded, Delete SHALL fail with Unavailable and the PushSubscription SHALL remain.

#### Scenario: Registered browser removed

- **WHEN** Delete removes one of the fan's PushSubscriptions
- **THEN** one unsubscription is announced, carrying that PushSubscription

#### Scenario: Not registered

- **WHEN** no PushSubscription of the fan has the endpoint
- **THEN** Delete succeeds and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** Delete would remove a PushSubscription and the announcement cannot be recorded
- **THEN** Delete fails with Unavailable and the PushSubscription remains
