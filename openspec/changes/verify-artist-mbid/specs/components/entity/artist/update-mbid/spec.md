## RENAMED Requirements

- FROM: `### Requirement: UpdateMBID replaces the MBID and remembers the old one`
- TO: `### Requirement: UpdateMBID replaces the MBID and marks it verified`

## MODIFIED Requirements

### Requirement: UpdateMBID clears what came from the replaced MBID
When UpdateMBID changes the MBID, it SHALL in the same change remove the artist's images (fanart) and fanart_sync_time, remove its official_site_check_time and remove its official site, so that none of them still describes the person of the replaced MBID; activity_ended takes the given status.

#### Scenario: Namesake's details removed
- **WHEN** an artist with images, an official site, an official_site_check_time and activity_ended true has its MBID replaced, with activity status false given
- **THEN** it has no images, no fanart_sync_time, no official site and no official_site_check_time, and activity_ended is false

### Requirement: UpdateMBID replaces the MBID and marks it verified
UpdateMBID SHALL take an artist id, an MBID and the music catalog's name and activity status for that MBID, and set, in one change, the artist's mbid to the MBID, its name to the given name, its activity_ended to the given status and its mbid_status to Verified, keeping its listening_mbid. All of them are stored or none. It SHALL fail with NotFound when no artist has the id, with InvalidArgument when the MBID is not a UUID of 36 characters, and with AlreadyExists, changing nothing, when another artist has the MBID as its mbid or its listening_mbid. Given the artist's own mbid, it SHALL set the name, activity_ended and mbid_status and clear nothing. It SHALL announce nothing.

#### Scenario: New MBID
- **WHEN** UpdateMBID is called for an Unverified artist with mbid A and listening_mbid A, with MBID B
- **THEN** the artist's mbid is B, its listening_mbid is A, its name and activity_ended are the given ones, and its mbid_status is Verified

#### Scenario: Second correction
- **WHEN** the artist's mbid is B and its listening_mbid is A, and UpdateMBID is called with C
- **THEN** its mbid is C and its listening_mbid is A

#### Scenario: Back to an earlier MBID
- **WHEN** the artist's mbid is B and its listening_mbid is A, and UpdateMBID is called with A
- **THEN** its mbid is A and its listening_mbid is A

#### Scenario: Own MBID
- **WHEN** UpdateMBID is called for an Ambiguous artist with its current mbid
- **THEN** its mbid_status becomes Verified, its name and activity_ended are the given ones, and its images and official site are kept

#### Scenario: MBID of another artist
- **WHEN** another artist has the given MBID as its mbid or its listening_mbid
- **THEN** UpdateMBID fails with AlreadyExists and the artist keeps its mbid and mbid_status

#### Scenario: Unknown artist
- **WHEN** UpdateMBID is called with an id no artist has
- **THEN** it fails with NotFound

#### Scenario: Malformed MBID
- **WHEN** the given MBID is not 36 characters long
- **THEN** it fails with InvalidArgument and nothing changes

### Requirement: UpdateMBID cannot race with a registration
UpdateMBID and Artist.Create SHALL not run their MBID checks at the same time: while one is running, the other waits. After UpdateMBID has given an artist an mbid, a Create of that MBID or of the artist's listening_mbid SHALL return that artist and register nothing.

#### Scenario: Registered at the same time
- **WHEN** UpdateMBID changes the mbid of an artist with listening_mbid A while Create is called with an artist of MBID A
- **THEN** Create returns the corrected artist and no artist is registered with MBID A
