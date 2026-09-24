# Notify New Concerts

## Purpose

PushNotificationUseCase.NotifyNewConcerts tells each follower of an artist about concerts just added for that artist, when the follower's hype level matches at least one of them, with a message in the fan's language that counts the matching concerts and links to the earliest one.

## Requirements

### Requirement: Triggered by concerts added for an artist

NotifyNewConcerts SHALL run when concerts are added for an artist, once per artist, with the artist and the ids of the concerts just added for it; the same input can also be given to it directly. It SHALL read the artist (Artist.Get) and use its current name, and read the concerts (Concert.ListByIDs). When the artist cannot be read, NotifyNewConcerts SHALL fail with that error and send nothing. Only the given concerts SHALL be considered; the artist's other upcoming concerts never count.

#### Scenario: Two concerts added for an artist with ten upcoming

- **WHEN** 2 concerts are added for an artist that already has 10 upcoming concerts, and a follower's hype level is Away
- **THEN** that follower's message counts 2

#### Scenario: Unknown artist

- **WHEN** the artist does not exist
- **THEN** NotifyNewConcerts fails with NotFound and nothing is sent

### Requirement: Every given concert must feature the artist

Before notifying anyone, NotifyNewConcerts SHALL check that every given concert exists and has the artist among its performers. When a concert does not exist, or its performers do not include the artist, NotifyNewConcerts SHALL fail with InvalidArgument and notify nobody. A concert with no performers at all SHALL be left out instead of failing the batch; when every concert is left out, nothing is sent and NotifyNewConcerts succeeds.

#### Scenario: Concert of another artist

- **WHEN** one of the given concerts does not feature the artist
- **THEN** NotifyNewConcerts fails with InvalidArgument and nobody is notified

#### Scenario: Unknown concert

- **WHEN** one of the given concert ids matches no concert
- **THEN** NotifyNewConcerts fails with InvalidArgument and nobody is notified

#### Scenario: Concert without performers

- **WHEN** one of three given concerts has no performers
- **THEN** it is left out and followers are notified about the other two

### Requirement: Each follower is matched against the new concerts

NotifyNewConcerts SHALL read the artist's followers (Follow.ListFollowers) and, for each, take the concerts that the follower's hype level matches among the new concerts, given the follower's home. A follower whose matched set is empty SHALL NOT be notified. The message count and the link SHALL come from the follower's matched set only. When the artist has no followers, or no follower matches, nothing is sent and NotifyNewConcerts succeeds.

Known defect: liverty-music/backend#469

#### Scenario: Home follower and a new concert elsewhere

- **WHEN** a concert is added in JP-40, the artist has an older upcoming concert in JP-13, and a follower's hype level is Home with home area JP-13
- **THEN** that follower is not notified

#### Scenario: Nearby follower and a distant new concert

- **WHEN** a concert is added 300 km from a Nearby follower's home centre, and the artist has an older upcoming concert 50 km from it
- **THEN** that follower is not notified

#### Scenario: Nearby follower and a new concert in range

- **WHEN** a concert is added 150 km from a Nearby follower's home centre, outside the follower's home area
- **THEN** that follower is notified about 1 concert

#### Scenario: Home follower counts only in-area concerts

- **WHEN** 3 concerts are added, 1 in JP-13 and 2 in JP-40, and a follower's hype level is Home with home area JP-13
- **THEN** that follower is notified and the message counts 1

#### Scenario: Watch follower

- **WHEN** a follower's hype level is Watch
- **THEN** that follower is not notified

#### Scenario: Nobody follows the artist

- **WHEN** the artist has no followers
- **THEN** nothing is sent and NotifyNewConcerts succeeds

### Requirement: The message names the artist, counts the concerts in the fan's language and links to the earliest

For each matched follower, NotifyNewConcerts SHALL build one message: the title is the artist's name; the body counts the matched concerts in the follower's preferred language, "1 new concert found" or "N new concerts found" in English and "新しいライブがN件見つかりました" in Japanese, with English for any other or no language; the link is `/concerts/<id>` of the earliest matched concert; the tag is one per artist, so a later message about the same artist replaces the earlier one on the device. The earliest concert is the one with the earliest date, then the earliest start time, a known start time before an unknown one, then the lowest id. The title, link and tag do not depend on the language.

#### Scenario: One concert in English

- **WHEN** a follower whose language is English is matched with 1 concert
- **THEN** the body reads "1 new concert found"

#### Scenario: Several concerts in English

- **WHEN** a follower whose language is English is matched with 3 concerts
- **THEN** the body reads "3 new concerts found"

#### Scenario: Japanese

- **WHEN** a follower whose language is Japanese is matched with 2 concerts
- **THEN** the body reads "新しいライブが2件見つかりました"

#### Scenario: Unsupported or missing language

- **WHEN** a follower has no preferred language, or one with no copy
- **THEN** the body is in English

#### Scenario: Link to the earliest matched concert

- **WHEN** a follower's matched concerts are on 2026-09-10 and 2026-09-03
- **THEN** the link is `/concerts/<id of the 2026-09-03 concert>`

#### Scenario: Same day, earlier start

- **WHEN** a follower's matched concerts are both on 2026-09-03, at 18:00 and 19:30
- **THEN** the link points to the 18:00 concert

#### Scenario: Home follower links to their in-area concert

- **WHEN** concerts are added in JP-40 on 2026-09-01 and in JP-13 on 2026-09-05, and a follower's hype level is Home with home area JP-13
- **THEN** that follower's link points to the JP-13 concert

### Requirement: Delivery is delegated per follower

For each matched follower, NotifyNewConcerts SHALL hand the message to notification delivery as one Notification of type new_concerts for that fan; recording, sending and the delivery outcome belong to NotificationUseCase.Notify. A failed delivery to a follower SHALL NOT fail NotifyNewConcerts. When a follower's Notification cannot be recorded, NotifyNewConcerts SHALL stop and fail so the trigger is retried; followers notified before the failure may then be notified again, and the per-artist tag replaces the repeated message on their devices. When the followers cannot be read, NotifyNewConcerts SHALL fail and send nothing. When the request is cancelled, no further follower SHALL be notified.

#### Scenario: One follower's browser rejects the push

- **WHEN** one matched follower's delivery fails
- **THEN** the other matched followers are still notified and NotifyNewConcerts succeeds

#### Scenario: Recording fails for one follower

- **WHEN** the Notification for the second of three matched followers cannot be recorded
- **THEN** the third follower is not notified and NotifyNewConcerts fails so the trigger is retried
