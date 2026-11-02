# Create

## Purpose

PushSubscriptionUseCase.Create registers the fan's current browser to receive push messages, or refreshes it if that browser is already registered, and returns the stored subscription.

## Requirements

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
