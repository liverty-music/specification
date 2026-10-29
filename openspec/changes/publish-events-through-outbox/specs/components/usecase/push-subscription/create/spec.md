## REMOVED Requirements

### Requirement: Create registers the browser and announces it
**Reason**: PushSubscription.Create announces a new or changed PushSubscription together with the change (components/entity/push-subscription/create), so the usecase no longer announces, and registering a browser again with the same keys is no longer announced.
**Migration**: Replaced by "Create registers the browser". Product analytics receives the "subscribed" signal, with the device family derived from the push address, from PushSubscription.Create's announcement. A failure to announce now fails Create and stores nothing.

## ADDED Requirements

### Requirement: Create registers the browser

Create SHALL store the fan's browser through PushSubscription.Create with the given push address and keys, and return the stored PushSubscription. When PushSubscription.Create fails, Create SHALL fail with that error.

#### Scenario: Fan enables push on a new browser

- **WHEN** a fan registers a browser that is not registered
- **THEN** the PushSubscription is stored and returned

#### Scenario: Fan re-registers the same browser

- **WHEN** a fan registers a browser that is already registered
- **THEN** Create returns the PushSubscription with its existing id

#### Scenario: Storing fails

- **WHEN** PushSubscription.Create fails with Unavailable
- **THEN** Create fails with Unavailable and nothing is stored
