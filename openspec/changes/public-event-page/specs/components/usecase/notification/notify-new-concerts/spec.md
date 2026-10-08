# Spec Delta

## MODIFIED Requirements

### Requirement: The message names the artist, counts the concerts in the fan's language and links to the earliest

For each matched follower, NotifyNewConcerts SHALL build one message: the title is the artist's name; the body counts the matched concerts in the follower's preferred language, "1 new concert found" or "N new concerts found" in English and "新しいライブがN件見つかりました" in Japanese, with English for any other or no language; the link is `/events/<id>` of the earliest matched concert when that concert's Series is first-party, and `/concerts/<id>` of the earliest matched concert otherwise; the tag is one per artist, so a later message about the same artist replaces the earlier one on the device. The earliest concert is the earliest of the set as Concert defines it. The title, link and tag do not depend on the language.

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

#### Scenario: First-party concert links to its event page

- **WHEN** the earliest matched concert belongs to a Series published by an Organizer
- **THEN** the link is `/events/<id of that concert>`
