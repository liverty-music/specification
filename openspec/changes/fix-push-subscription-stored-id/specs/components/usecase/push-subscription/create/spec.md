# Spec Delta

## MODIFIED Requirements

### Requirement: Create registers the browser and announces it

Create SHALL store the fan's browser through PushSubscription.Create with the given push address and keys, and return the stored PushSubscription. After storing, it SHALL announce that the fan subscribed, carrying only the browser's device family, never its push address. A failure to store SHALL fail Create and announce nothing; a failure to announce SHALL NOT fail Create.

#### Scenario: Fan enables push on a new browser

- **WHEN** a fan registers a browser that is not registered
- **THEN** the PushSubscription is stored and returned, and the subscription is announced with its device family

#### Scenario: Fan re-registers the same browser

- **WHEN** a fan registers a browser that is already registered
- **THEN** Create returns the PushSubscription with its existing id

#### Scenario: Announcement fails

- **WHEN** the PushSubscription is stored but announcing fails
- **THEN** Create still succeeds
