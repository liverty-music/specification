## MODIFIED Requirements

### Requirement: A new or changed subscription is announced with the change

When Create stores a new PushSubscription, or changes the keys or the owner of an existing one, it SHALL announce the PushSubscription as subscribed (PushSubscription.Subscribed), carrying it after the change, together with the change: both are stored or neither is. When Create changes nothing, it SHALL announce nothing. When the announcement cannot be recorded, Create SHALL fail with Unavailable and store nothing.

#### Scenario: New browser announced

- **WHEN** Create runs with an endpoint that is not registered
- **THEN** one subscription is announced, carrying the new PushSubscription

#### Scenario: Browser moves to another fan

- **WHEN** Create runs for fan B with an endpoint registered by fan A
- **THEN** one subscription is announced, carrying the PushSubscription owned by fan B

#### Scenario: Same browser, same keys

- **WHEN** Create runs with an endpoint already registered by the same fan with the same keys
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** Create runs with an endpoint that is not registered and the announcement cannot be recorded
- **THEN** Create fails with Unavailable and no PushSubscription is stored
