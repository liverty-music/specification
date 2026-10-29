## ADDED Requirements

### Requirement: New concerts of a public series are announced with the publish

When PublishEvents makes at least one Event PUBLISHED in place and the Series' visibility is PUBLIC, it SHALL announce the new concerts once for each performing Artist of those Events: one announcement per Artist, carrying the Concerts made PUBLISHED in place by this call at which that Artist performs, together with the publish: both are stored or neither is. Claimed Events, Events published before, and every Event of an UNLISTED Series SHALL NOT be announced. When PublishEvents fails it SHALL announce nothing. When an announcement cannot be recorded, PublishEvents SHALL fail with Unavailable and every given Event SHALL stay DRAFT.

#### Scenario: Two performers

- **WHEN** PublishEvents makes one Event of a PUBLIC Series with two performers PUBLISHED
- **THEN** two announcements are made, one per performer, each carrying that Concert

#### Scenario: Additional date announced alone

- **WHEN** a PUBLIC Series has three PUBLISHED Events and PublishEvents makes a fourth PUBLISHED
- **THEN** each announcement carries only the fourth Concert

#### Scenario: Only claimed events

- **WHEN** every given DRAFT Event claims an Event of a discovered Series
- **THEN** nothing is announced

#### Scenario: Unlisted series

- **WHEN** PublishEvents makes an Event of an UNLISTED Series PUBLISHED
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** PublishEvents would make an Event of a PUBLIC Series PUBLISHED and the announcement cannot be recorded
- **THEN** PublishEvents fails with Unavailable and every given Event stays DRAFT
