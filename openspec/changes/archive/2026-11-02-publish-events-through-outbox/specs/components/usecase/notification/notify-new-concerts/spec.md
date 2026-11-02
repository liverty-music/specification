## MODIFIED Requirements

### Requirement: Triggered by concerts added for an artist

NotifyNewConcerts SHALL run for each announcement of new concerts for an artist (Concert.Create, Series.PublishEvents), with the artist and the concerts the announcement carries; an admin can also give it the same input directly. It SHALL read the artist (Artist.Get) and use its current name, and read the concerts (Concert.ListByIDs). When the artist cannot be read, NotifyNewConcerts SHALL fail with that error and send nothing. Only the given concerts SHALL be considered; the artist's other upcoming concerts never count.

#### Scenario: Two concerts added for an artist with ten upcoming

- **WHEN** 2 concerts are added for an artist that already has 10 upcoming concerts, and a follower's hype level is Away
- **THEN** that follower's message counts 2

#### Scenario: Unknown artist

- **WHEN** the artist does not exist
- **THEN** NotifyNewConcerts fails with NotFound and nothing is sent

### Requirement: One new_concerts notification requested per matched follower

For each matched follower, NotifyNewConcerts SHALL start NotificationUseCase.Deliver with one notification of type new_concerts carrying that follower's message, named after the follower and what NotifyNewConcerts runs for: the announcement of the new concerts, or one direct call by an admin. A repeated delivery of the same announcement SHALL start nothing new for a follower already started; each direct call notifies again. Deliver records and delivers each notification on its own; a follower whose Notification cannot be recorded, or whose delivery fails, SHALL NOT affect the other followers or fail NotifyNewConcerts. The story stories/get-notified-of-new-concerts covers the whole flow from the added concerts to the fan's browsers. When a follower's notification cannot be started, NotifyNewConcerts SHALL stop and fail so the announcement is processed again; the followers already started are not started again. When the followers cannot be read, NotifyNewConcerts SHALL fail and start nothing. When the call is cancelled, no further follower's notification SHALL be started.

#### Scenario: Every matched follower is requested

- **WHEN** three followers are matched
- **THEN** one new_concerts notification is started for each of the three, carrying that follower's message

#### Scenario: Request fails for one follower

- **WHEN** the notification for the second of three matched followers cannot be started
- **THEN** the third follower's notification is not started and NotifyNewConcerts fails so the announcement is processed again, without notifying the first follower again

#### Scenario: Same concerts notified twice

- **WHEN** NotifyNewConcerts runs twice for the same announcement of the same concerts and matches the same follower
- **THEN** the follower is notified once

#### Scenario: Admin sends again

- **WHEN** an admin gives NotifyNewConcerts an artist and concerts that were already announced
- **THEN** each matched follower is notified again, and the new message replaces the earlier one on the follower's devices
