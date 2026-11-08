# Get notified of new concerts

## Purpose

A fan who follows an artist gets one push message on each of their registered browsers when concerts matching their hype level are added for that artist, and every such message is kept as a Notification the fan finds in the notification center.

```mermaid
usecase-beta
direction LR
actor Fan("fan")
systemBoundary "Liverty Music"
  Goal("Get notified of new concerts")
  NotificationUseCaseNotifyNewConcerts("NotificationUseCase.NotifyNewConcerts")
  NotificationUseCaseDeliver("NotificationUseCase.Deliver")
end
Fan --> Goal
Goal ..> : include NotificationUseCaseNotifyNewConcerts
Goal ..> : include NotificationUseCaseDeliver
```

## Requirements

### Requirement: New concerts reach matched followers' browsers and are recorded

When concerts are added for an artist, NotificationUseCase.NotifyNewConcerts SHALL choose the followers whose hype level matches the new concerts and request one new_concerts notification per chosen follower, naming the artist and that follower's matched concerts, and NotificationUseCase.Deliver SHALL record each requested notification as a Notification and push its message to every browser that follower has registered. The Notification SHALL be recorded whether or not a browser accepts the message, so it is listed in the fan's notification center.

#### Scenario: Away follower with one browser

- **WHEN** a concert of Vaundy is added, a fan follows Vaundy at Away, and the fan has one registered browser whose push service accepts the message
- **THEN** that browser receives one message titled [Vaundy] 新着ライブ発表!! (in Japanese) that counts 1 new concert and links to the concert
- **AND** the fan has one new_concerts Notification

#### Scenario: Matched follower without a browser

- **WHEN** a concert is added for an artist that a fan follows at Away, and the fan has no registered browser
- **THEN** the fan has one new_concerts Notification, listed in the notification center

#### Scenario: Watch follower

- **WHEN** a concert is added for an artist that a fan follows at Watch
- **THEN** the fan's browsers receive nothing and no Notification is recorded for the fan

#### Scenario: Browser gone

- **WHEN** the push service of a matched fan's only browser reports it gone
- **THEN** the fan's Notification is still recorded and that browser's PushSubscription is removed

### Requirement: Every way a concert is added reaches followers the same way

Concerts added by the daily discovery, by an admin approving a held concert, and by an Organizer publishing a PUBLIC concert SHALL reach matched followers alike: one message per artist for the concerts added together. Concerts of an UNLISTED concert SHALL reach nobody.

#### Scenario: Organizer publishes a co-headlined concert

- **WHEN** an Organizer publishes a PUBLIC concert performed by two artists, and a fan follows both at Away
- **THEN** the fan receives two messages, each titled with one of the two artists' names in brackets

#### Scenario: Unlisted concert

- **WHEN** an Organizer publishes an UNLISTED concert of an artist a fan follows at Away
- **THEN** the fan receives nothing about it

#### Scenario: Tour found by discovery

- **WHEN** the daily discovery adds three concerts of one tour for an artist a fan follows at Away
- **THEN** the fan receives one message that counts 3 new concerts
