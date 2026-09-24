# Delete

## Purpose

PushNotificationUseCase.Delete stops push messages to one of the fan's browsers by removing that browser's subscription, and announces it; the fan's other browsers keep theirs.

## Requirements

### Requirement: Delete removes the browser and announces it

Delete SHALL remove the fan's PushSubscription for the push address through PushSubscription.Delete and then announce that the fan unsubscribed, carrying only the browser's device family, also when nothing was registered. A failure to remove SHALL fail Delete and announce nothing; a failure to announce SHALL NOT fail Delete.

#### Scenario: Fan disables push on one browser

- **WHEN** a fan with two registered browsers removes one
- **THEN** that PushSubscription is removed, the other remains, and the unsubscription is announced

#### Scenario: Browser not registered

- **WHEN** the fan has no PushSubscription with that push address
- **THEN** Delete succeeds and the unsubscription is still announced

#### Scenario: Announcement fails

- **WHEN** the PushSubscription is removed but announcing fails
- **THEN** Delete still succeeds
