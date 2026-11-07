## MODIFIED Requirements

### Requirement: The message names the artist, counts the concerts in the fan's language and links to the earliest

For each matched follower, the requested notification's subject SHALL be the artist and the follower's matched concerts, so the message the Notification entity renders from it is titled with that artist, counts the matched concerts and links to the earliest of them. The earliest concert is the earliest of the set as Concert defines it.

#### Scenario: Japanese

- **WHEN** a follower whose language is `ja` is matched with 3 concerts of Vaundy
- **THEN** the title reads [Vaundy] 新着ライブ発表!! and the body starts with 新しいライブが3件見つかりました

#### Scenario: One concert in English

- **WHEN** a follower whose language is `en` is matched with 1 concert
- **THEN** the body starts with "1 new concert found"

#### Scenario: Several concerts in English

- **WHEN** a follower whose language is `en` is matched with 3 concerts
- **THEN** the body starts with "3 new concerts found"

#### Scenario: Unsupported or missing language

- **WHEN** a follower's preferred language has no copy, such as `fr`
- **THEN** the message is in English

#### Scenario: Link to the earliest matched concert

- **WHEN** a follower's matched concerts are on 2026-09-10 and 2026-09-03
- **THEN** the link is `/concerts/<id of the 2026-09-03 concert>`

#### Scenario: Same day, earlier start

- **WHEN** a follower's matched concerts are both on 2026-09-03, at 18:00 and 19:30
- **THEN** the link points to the 18:00 concert

#### Scenario: Home follower links to their in-area concert

- **WHEN** concerts are added in JP-40 on 2026-09-01 and in JP-13 on 2026-09-05, and a follower's hype level is Home with home area JP-13
- **THEN** that follower's link points to the JP-13 concert

#### Scenario: First-party concert links to its event page

- **WHEN** the earliest matched concert belongs to a Series published by an Organizer
- **THEN** the link is `/events/<id of that concert>`

### Requirement: One new_concerts notification requested per matched follower

For each matched follower, NotifyNewConcerts SHALL start NotificationUseCase.Deliver with one notification of type new_concerts whose subject is the artist and that follower's matched concerts, named after the follower and what NotifyNewConcerts runs for: the announcement of the new concerts, or one direct call by an admin. A repeated delivery of the same announcement SHALL start nothing new for a follower already started; each direct call notifies again. Deliver records and delivers each notification on its own; a follower whose Notification cannot be recorded, or whose delivery fails, SHALL NOT affect the other followers or fail NotifyNewConcerts. The story stories/get-notified-of-new-concerts covers the whole flow from the added concerts to the fan's browsers. When a follower's notification cannot be started, NotifyNewConcerts SHALL stop and fail so the announcement is processed again; the followers already started are not started again. When the followers cannot be read, NotifyNewConcerts SHALL fail and start nothing. When the call is cancelled, no further follower's notification SHALL be started.

#### Scenario: Every matched follower is requested

- **WHEN** three followers are matched
- **THEN** one new_concerts notification is started for each of the three, naming the artist and that follower's matched concerts

#### Scenario: Request fails for one follower

- **WHEN** the notification for the second of three matched followers cannot be started
- **THEN** the third follower's notification is not started and NotifyNewConcerts fails so the announcement is processed again, without notifying the first follower again

#### Scenario: Same concerts notified twice

- **WHEN** NotifyNewConcerts runs twice for the same announcement of the same concerts and matches the same follower
- **THEN** the follower is notified once

#### Scenario: Admin sends again

- **WHEN** an admin gives NotifyNewConcerts an artist and concerts that were already announced
- **THEN** each matched follower is notified again, and the new message replaces the earlier one on the follower's devices
