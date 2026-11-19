# Spec Delta

## MODIFIED Requirements

### Requirement: A shared link shows the event to anyone

After an Organizer publishes a PUBLIC Series with SeriesUseCase.Publish, the link `/concerts/<id>` of each of its Events SHALL show that event's Concert page, with the Concert ConcertUseCase.Get returns and the Series' dates ConcertUseCase.ListBySeries returns, to a guest who has never used the app and to a signed-in fan who does not follow the performers; the link's preview card SHALL show the event's title, date, venue and cover image.

#### Scenario: Guest from a social post

- **WHEN** an Organizer publishes a PUBLIC single-day Series for an Artist, and a guest opens `/concerts/<id>` of its Event
- **THEN** the guest sees the event's title, performers, date and venue, and the link's preview carries the same title, date and venue

#### Scenario: Unlisted series

- **WHEN** an Organizer publishes an UNLISTED Series, and a guest opens `/concerts/<id>` of its Event
- **THEN** the guest sees the "event not found" view

### Requirement: Following from a shared link

A guest SHALL be able to follow a performer on the Concert page, and after signing up from that page SHALL find the performer followed on their account and be back on the same Concert page.

#### Scenario: Guest follows, then signs up

- **WHEN** a guest follows the performer on `/concerts/<id>`, starts sign-up there and completes it
- **THEN** the app shows `/concerts/<id>` signed in, the performer is among the fan's followed Artists, and no post-signup dialog is shown

### Requirement: Notification leads to the concert page

A follower notified of a first-party concert by NotificationUseCase.NotifyNewConcerts SHALL reach that concert's Concert page by tapping the notification.

#### Scenario: Follower taps the notification

- **WHEN** an Organizer publishes a PUBLIC Series for an Artist that a fan follows and the fan taps the resulting notification
- **THEN** the app opens `/concerts/<id>` of the Series' earliest Event

### Requirement: Cancelled event stays explained

After an Organizer cancels a published PUBLIC Series with SeriesUseCase.Cancel, the links of its Events SHALL still open their Concert pages, showing that the concert is 中止 (cancelled) and selling nothing.

#### Scenario: Link opened after cancellation

- **WHEN** a guest opens `/concerts/<id>` after the Organizer cancelled the Series
- **THEN** the guest sees the event with the 中止 banner and no sale
