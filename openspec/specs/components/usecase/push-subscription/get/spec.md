# Get

## Purpose

PushNotificationUseCase.Get tells the fan's browser whether it is still registered for push, by returning the fan's PushSubscription for that browser's push address.

## Requirements

### Requirement: Get returns the fan's subscription for the browser

Get SHALL return the PushSubscription that PushSubscription.Get finds for the fan and the push address, and fail with NotFound when there is none.

#### Scenario: Browser registered

- **WHEN** the fan's browser is registered
- **THEN** Get returns its PushSubscription

#### Scenario: Browser not registered

- **WHEN** the fan has no PushSubscription with that push address
- **THEN** Get fails with NotFound
