## RENAMED Requirements

- FROM: `### Requirement: UpdateMBID replaces the MBID and remembers the old one`
- TO: `### Requirement: UpdateMBID replaces the MBID and marks it verified`

## MODIFIED Requirements

### Requirement: UpdateMBID replaces the MBID and marks it verified
UpdateMBID SHALL set the mbid of the artist with the given id to the given MBID and its mbid_status to Verified, and SHALL keep its listening_mbid. It SHALL fail with NotFound when no artist has the id, with InvalidArgument when the MBID is not a UUID of 36 characters, and with AlreadyExists, changing nothing, when another artist has the MBID as its mbid or its listening_mbid. Given the artist's own mbid, it SHALL set mbid_status to Verified and change nothing else. It SHALL announce nothing.

#### Scenario: New MBID
- **WHEN** UpdateMBID is called for an Unverified artist with mbid A and listening_mbid A, with MBID B
- **THEN** the artist's mbid is B, its listening_mbid is A and its mbid_status is Verified

#### Scenario: Second correction
- **WHEN** the artist's mbid is B and its listening_mbid is A, and UpdateMBID is called with C
- **THEN** its mbid is C and its listening_mbid is A

#### Scenario: Back to an earlier MBID
- **WHEN** the artist's mbid is B and its listening_mbid is A, and UpdateMBID is called with A
- **THEN** its mbid is A and its listening_mbid is A

#### Scenario: Own MBID
- **WHEN** UpdateMBID is called for an Ambiguous artist with its current mbid
- **THEN** its mbid_status becomes Verified and nothing else changes, including the images, the official site and activity_ended

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
