## MODIFIED Requirements

### Requirement: Create registers each push address once

Create SHALL store a PushSubscription for the fan with the given endpoint and keys. When a PushSubscription with the same endpoint already exists, Create SHALL update it in place instead of adding a second one: its keys are replaced, its owner becomes the given fan, and its id is kept. When that PushSubscription already belongs to the given fan and has the given keys, Create SHALL change nothing. Create SHALL return the stored PushSubscription, carrying the id it is stored under.

#### Scenario: New browser

- **WHEN** Create runs with an endpoint that is not registered
- **THEN** a PushSubscription with a new id is stored and returned

#### Scenario: Same browser registers again

- **WHEN** Create runs with an endpoint that is already registered by the same fan, with new keys
- **THEN** the existing PushSubscription's keys are replaced and it is returned with its existing id

#### Scenario: Same browser, same keys

- **WHEN** Create runs with an endpoint already registered by the same fan with the same keys
- **THEN** nothing changes and the PushSubscription is returned with its existing id

#### Scenario: Browser moves to another fan

- **WHEN** Create runs for fan B with an endpoint registered by fan A
- **THEN** the PushSubscription now belongs to fan B and fan A no longer has it

## ADDED Requirements

### Requirement: A new or changed subscription is announced with the change

When Create stores a new PushSubscription, or changes the keys or the owner of an existing one, it SHALL announce the PushSubscription as subscribed, carrying it after the change, together with the change: both are stored or neither is. When Create changes nothing, it SHALL announce nothing. When the announcement cannot be recorded, Create SHALL fail with Unavailable and store nothing.

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
