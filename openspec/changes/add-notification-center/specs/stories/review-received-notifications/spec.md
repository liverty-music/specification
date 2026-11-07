## Purpose

A fan sees every notification sent to them in one place, including those whose push never reached a browser, and knows which ones they have not read yet.

```mermaid
usecase-beta
direction LR
actor Fan("fan")
systemBoundary "Liverty Music"
  Goal("Review received notifications")
  Deliver("NotificationUseCase.Deliver")
  List("NotificationUseCase.List")
  MarkRead("NotificationUseCase.MarkRead")
end
Fan --> Goal
Goal ..> : include Deliver
Goal ..> : include List
Goal ..> : include MarkRead
```

## ADDED Requirements

### Requirement: Every notification sent to a fan is in the notification center

Every notification NotificationUseCase.Deliver records for a fan SHALL appear in the fan's notification center (NotificationUseCase.List), whether or not a browser accepted its push, rendered in the fan's current language, until 50 newer notifications push it out of the list or a record its subject names is deleted.

#### Scenario: Fan without push
- **WHEN** a fan who never allowed push notifications applied for a lottery and lost
- **THEN** the fan's notification center lists a [<artist>] 抽選結果のお知らせ notification (in Japanese)

#### Scenario: Fan with push
- **WHEN** a fan receives a concert_cancelled push on their phone and dismisses it
- **THEN** the notification center still lists it

### Requirement: The unread count follows what the fan has opened

The bell in the header SHALL count the fan's unread notifications. A notification SHALL become read when the fan taps it in the notification center or opens its push (NotificationUseCase.MarkRead), and SHALL stay unread otherwise, including when its push is dismissed.

#### Scenario: Three arrive at once
- **WHEN** three notifications are sent to a fan at once and the fan opens one push
- **THEN** the bell shows 2 and the notification center marks the other two unread

#### Scenario: Read in the center
- **WHEN** the fan then taps one of the two unread items in the notification center
- **THEN** the bell shows 1
