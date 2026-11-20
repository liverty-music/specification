# Spec Delta

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
- **THEN** the link is `/timetable?concert=<id of the 2026-09-03 concert>`

#### Scenario: Same day, earlier start

- **WHEN** a follower's matched concerts are both on 2026-09-03, at 18:00 and 19:30
- **THEN** the link points to the 18:00 concert

#### Scenario: Home follower links to their in-area concert

- **WHEN** concerts are added in JP-40 on 2026-09-01 and in JP-13 on 2026-09-05, and a follower's hype level is Home with home area JP-13
- **THEN** that follower's link points to the JP-13 concert

#### Scenario: First-party concert links to its concert page

- **WHEN** the earliest matched concert belongs to a Series published by an Organizer
- **THEN** the link is `/concerts/<id of that concert>`
