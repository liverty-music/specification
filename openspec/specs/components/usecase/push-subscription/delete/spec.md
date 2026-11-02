# Delete

## Purpose

PushSubscriptionUseCase.Delete stops push messages to one of the fan's browsers by removing that browser's subscription through PushSubscription.Delete, which announces the removal; the fan's other browsers keep theirs.

## Requirements

### Requirement: Delete removes the browser

Delete SHALL remove the fan's PushSubscription for the push address through PushSubscription.Delete and succeed, also when nothing was registered. When PushSubscription.Delete fails, Delete SHALL fail with that error.

#### Scenario: Fan disables push on one browser

- **WHEN** a fan with two registered browsers removes one
- **THEN** that PushSubscription is removed and the other remains

#### Scenario: Browser not registered

- **WHEN** the fan has no PushSubscription with that push address
- **THEN** Delete succeeds and nothing is removed

#### Scenario: Removal fails

- **WHEN** PushSubscription.Delete fails with Unavailable
- **THEN** Delete fails with Unavailable and the PushSubscription remains
