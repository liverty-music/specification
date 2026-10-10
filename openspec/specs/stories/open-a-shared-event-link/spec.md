# stories/open-a-shared-event-link Specification

## Purpose
A fan who taps an event link that an artist shared, or a new-concert notification, lands on that event's public page whether or not they have an account, can follow the artist there, and when they sign up to buy, comes back to the same event.

## Requirements

### Requirement: A shared link shows the event to anyone

After an Organizer publishes a PUBLIC Series with ConcertAuthoringUseCase.Publish, the link `/events/<id>` of each of its Events SHALL show that event's Event page, with the Concert ConcertUseCase.Get returns and the Series' dates ConcertUseCase.ListBySeries returns, to a guest who has never used the app and to a signed-in fan who does not follow the performers; the link's preview card SHALL show the event's title, date, venue and cover image.

#### Scenario: Guest from a social post

- **WHEN** an Organizer publishes a PUBLIC single-day Series for an Artist, and a guest opens `/events/<id>` of its Event
- **THEN** the guest sees the event's title, performers, date and venue, and the link's preview carries the same title, date and venue

#### Scenario: Unlisted series

- **WHEN** an Organizer publishes an UNLISTED Series, and a guest opens `/events/<id>` of its Event
- **THEN** the guest sees the "event not found" view

### Requirement: Following from a shared link

A guest SHALL be able to follow a performer on the Event page, and after signing up from that page SHALL find the performer followed on their account and be back on the same Event page.

#### Scenario: Guest follows, then signs up

- **WHEN** a guest follows the performer on `/events/<id>`, starts sign-up there and completes it
- **THEN** the app shows `/events/<id>` signed in, the performer is among the fan's followed Artists, and no post-signup dialog is shown

### Requirement: Notification leads to the event page

A follower notified of a first-party concert by PushNotificationUseCase.NotifyNewConcerts SHALL reach that concert's Event page by tapping the notification.

#### Scenario: Follower taps the notification

- **WHEN** an Organizer publishes a PUBLIC Series for an Artist that a fan follows and the fan taps the resulting notification
- **THEN** the app opens `/events/<id>` of the Series' earliest Event

### Requirement: Cancelled event stays explained

After an Organizer cancels a published PUBLIC Series with ConcertAuthoringUseCase.Cancel, the links of its Events SHALL still open their Event pages, showing that the concert is 中止 (cancelled) and selling nothing.

#### Scenario: Link opened after cancellation

- **WHEN** a guest opens `/events/<id>` after the Organizer cancelled the Series
- **THEN** the guest sees the event with the 中止 banner and no sale
