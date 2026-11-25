## MODIFIED Requirements

### Requirement: Admin area format

A Venue's admin area SHALL be present and SHALL be the code of a first-level Area: an ISO 3166-2 subdivision code such as JP-13, or the ISO 3166-1 code of a country or territory that is its own first-level Area, such as HK. A free-text name, a well-formed code that is no Area, the code of a lower-level or withdrawn Area, and the code of a region SHALL be invalid.

#### Scenario: Valid admin area
- **WHEN** the admin area is JP-13
- **THEN** it is valid

#### Scenario: Territory without subdivisions
- **WHEN** the admin area is HK
- **THEN** it is valid

#### Scenario: Free-text admin area is invalid
- **WHEN** the admin area is "東京都"
- **THEN** it is invalid

#### Scenario: Well-formed code that is no Area
- **WHEN** the admin area is JP-99
- **THEN** it is invalid

#### Scenario: Lower-level code
- **WHEN** the admin area is FR-33, whose parent is FR-NAQ
- **THEN** it is invalid

#### Scenario: Withdrawn code
- **WHEN** the admin area is FR-75, which was replaced by FR-IDF
- **THEN** it is invalid

#### Scenario: Region code
- **WHEN** the admin area is JP-KANTO
- **THEN** it is invalid

#### Scenario: Missing admin area
- **WHEN** a Venue has no admin area
- **THEN** it is invalid

### Requirement: Listed venue name normalization

A listed venue name SHALL be normalized by folding full-width and half-width forms to one form, collapsing runs of whitespace to a single space and trimming the ends, removing a leading "〈city〉公演 ＠" prefix, and then removing a leading "〈prefecture〉・" prefix where the prefecture is one of Japan's 47 prefectures, with or without its 都/道/府/県 suffix. A name that is blank after normalization SHALL be treated as missing. A name that only says the venue is not yet announced SHALL normalize to an empty name, and so is also treated as missing: compared ignoring whitespace, punctuation and Latin letter case, it is one of "TBA", "TBD", "to be announced", "coming soon", "stay tuned", "未定", "後日発表", "private" or "private event", or it contains "某所" (an undisclosed place, as in "横浜某所"). "private" and "private event" are the listing's own word for a show at a place it does not disclose to the public. Normalizing an already-normalized name SHALL leave it unchanged. This is the only normalization of a venue name: every comparison of venue names (an Event's listed venue name, a ConcertCandidate's, and the events Concert.Search returns) starts from it.

#### Scenario: Prefecture prefix removed
- **WHEN** the listed venue name is "大阪・フェスティバルホール"
- **THEN** the normalized name is "フェスティバルホール"

#### Scenario: Performance-city prefix removed
- **WHEN** the listed venue name is "大阪公演 ＠フェスティバルホール"
- **THEN** the normalized name is "フェスティバルホール"

#### Scenario: Middle dot after a non-prefecture word is kept
- **WHEN** the listed venue name is "東京文化会館・大ホール"
- **THEN** the normalized name is "東京文化会館・大ホール"

#### Scenario: Whitespace-only name is missing
- **WHEN** the listed venue name is "　 "
- **THEN** the normalized name is empty and the name is treated as missing

#### Scenario: Venue not yet announced is missing
- **WHEN** the listed venue name is "TBA", "-STAY TUNED-", "未定", "横浜某所", "PRIVATE" or "Private Event"
- **THEN** the normalized name is empty and the name is treated as missing

#### Scenario: A real name containing a marker word is kept
- **WHEN** the listed venue name is "TBA Hall Osaka"
- **THEN** the normalized name is "TBA Hall Osaka"

#### Scenario: Already normalized name is unchanged
- **WHEN** the listed venue name is "日本武道館"
- **THEN** the normalized name is "日本武道館"

### Requirement: Current date at a venue

The current date at a Venue SHALL be the calendar day that the given instant falls on in the Venue's own time zone. Wherever an operation compares an Event's local date with the current date, today or a date given as an instant, it SHALL use the current date at that Event's Venue, never the calendar day of the clock of the server or the database.

#### Scenario: Early morning counts as the new day
- **WHEN** the instant is 2026-11-10 23:30 UTC and the Venue's time zone is Asia/Tokyo, where it is 2026-11-11 08:30
- **THEN** the current date at the Venue is 2026-11-11, and an Event there dated 2026-11-10 is in the past

#### Scenario: Event day still today
- **WHEN** the instant is 2026-11-11 14:59 UTC and the Venue's time zone is Asia/Tokyo, where it is 2026-11-11 23:59
- **THEN** the current date at the Venue is 2026-11-11, and an Event there dated 2026-11-11 is not in the past

#### Scenario: Venue behind UTC
- **WHEN** the instant is 2026-11-11 07:00 UTC and the Venue's time zone is America/Los_Angeles, where it is 2026-11-10 23:00
- **THEN** the current date at the Venue is 2026-11-10, and an Event there dated 2026-11-10 is not in the past

## ADDED Requirements

### Requirement: Time zone of a venue

A Venue SHALL have a time zone, an IANA time zone name. When the Venue's Area has a time zone, the Venue's time zone SHALL equal it; otherwise it SHALL be one of the time zones of the Area's country. A Venue without a time zone, or with any other time zone, SHALL be invalid.

#### Scenario: Zone of the area's country
- **WHEN** the admin area is KR-11 and the time zone is Asia/Seoul
- **THEN** the Venue is valid

#### Scenario: Zone of a territory
- **WHEN** the admin area is HK and the time zone is Asia/Hong_Kong
- **THEN** the Venue is valid

#### Scenario: Zone of another country
- **WHEN** the admin area is JP-13 and the time zone is Asia/Seoul
- **THEN** the Venue is invalid

#### Scenario: Zone other than the Area's own
- **WHEN** the admin area is US-CA, whose time zone is America/Los_Angeles, and the Venue's time zone is America/New_York
- **THEN** the Venue is invalid

#### Scenario: Area without a time zone of its own
- **WHEN** the admin area is US-TX, which has no time zone of its own, and the Venue's time zone is America/Chicago or America/Denver
- **THEN** the Venue is valid

#### Scenario: Missing time zone
- **WHEN** a Venue has admin area JP-13 and no time zone
- **THEN** the Venue is invalid

### Requirement: Name is the listed or member-saved name

A Venue's name SHALL be the name its source listed (its listed venue name) or the name a member of an Organizer saved for it. A name read from the map catalog SHALL become a Venue's name only when a member saved it. A Venue made without a resolved place SHALL have no place id and no coordinates.

#### Scenario: Discovered venue with a resolved place
- **WHEN** a Venue is made for listed name "Zepp Haneda(TOKYO)" and the map catalog names its place "Zepp Haneda (TOKYO)"
- **THEN** the Venue's name is "Zepp Haneda(TOKYO)"

#### Scenario: Unresolved venue
- **WHEN** a Venue is made for listed name "ライブハウスX" with no resolved place
- **THEN** its name is "ライブハウスX" and it has no place id and no coordinates

#### Scenario: Name a member saved
- **WHEN** a member picks a place the map catalog names "Gocheok Sky Dome", changes the name to "高尺スカイドーム" and saves
- **THEN** the Venue's name is "高尺スカイドーム"

### Requirement: Coordinates at most 30 days old

A Venue's coordinates SHALL carry their fetch time, the moment they were read from the map catalog; a Venue SHALL have both or neither. Coordinates SHALL be expired at an instant when their fetch time is more than 30 days before it.

#### Scenario: Recent coordinates
- **WHEN** a Venue's coordinates were fetched at 2026-11-01 04:00 UTC and the instant is 2026-11-24 04:00 UTC
- **THEN** the coordinates are not expired

#### Scenario: Coordinates older than 30 days
- **WHEN** a Venue's coordinates were fetched at 2026-10-20 04:00 UTC and the instant is 2026-11-24 04:00 UTC
- **THEN** the coordinates are expired

#### Scenario: Coordinates without a fetch time
- **WHEN** a Venue has coordinates and no fetch time
- **THEN** the Venue is invalid

## REMOVED Requirements

### Requirement: Canonical name falls back to the listed name

**Reason**: A Venue's name is no longer the map catalog's canonical name when a place was resolved; it is always the listed name or the name a member saved.
**Migration**: "Name is the listed or member-saved name" states the rule, including the unresolved case. Existing Venues with a place id and a listed name take the listed name in this change's data migration.
