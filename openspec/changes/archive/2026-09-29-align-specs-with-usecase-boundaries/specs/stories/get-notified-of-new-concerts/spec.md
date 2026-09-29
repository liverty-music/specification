# Spec Delta

## MODIFIED Requirements

### Requirement: New concerts reach matched followers' browsers and are recorded

When concerts are added for an artist, PushNotificationUseCase.NotifyNewConcerts SHALL choose the followers whose hype level matches the new concerts, build each one's message and request one new_concerts notification per chosen follower, and NotificationUseCase.Deliver SHALL record each requested notification as a Notification and push its message to every browser that follower has registered. Each follower's Notification SHALL end Delivered when at least one of their browsers' push services accepts the message, and Failed otherwise.

#### Scenario: Away follower with one browser

- **WHEN** a concert is added for an artist that a fan follows at Away, and the fan has one registered browser whose push service accepts the message
- **THEN** that browser receives one message titled with the artist's name that counts 1 new concert and links to the concert
- **AND** the fan has one new_concerts Notification that is Delivered

#### Scenario: Matched follower without a browser

- **WHEN** a concert is added for an artist that a fan follows at Away, and the fan has no registered browser
- **THEN** the fan has one new_concerts Notification that is Failed with the reason "no active push subscription"

#### Scenario: Watch follower

- **WHEN** a concert is added for an artist that a fan follows at Watch
- **THEN** the fan's browsers receive nothing and no Notification is recorded for the fan

#### Scenario: Browser gone

- **WHEN** the push service of a matched fan's only browser reports it gone
- **THEN** the fan's Notification is Failed and that browser's PushSubscription is removed
