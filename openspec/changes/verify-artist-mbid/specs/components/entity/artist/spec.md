## MODIFIED Requirements

### Requirement: A new artist starts without images
A new Artist SHALL get a fresh unique id and SHALL start with no fanart, no fanart_sync_time, no official_site_check_time and activity_ended false. Its listening_mbid SHALL be the MBID the listening service returned for it, and its mbid_status SHALL be Unverified unless it is created with its MBID already verified or found ambiguous.

#### Scenario: New artist
- **WHEN** an artist is created from a name and an MBID
- **THEN** it has a fresh id, that name, that MBID as its mbid and its listening_mbid, mbid_status Unverified, no fanart, no fanart_sync_time, no official_site_check_time and activity_ended false

#### Scenario: Two new artists
- **WHEN** two artists are created from the same name and MBID
- **THEN** their ids differ

#### Scenario: New artist created verified
- **WHEN** an artist is created from a name, listening MBID A, MBID B and mbid_status Verified
- **THEN** its listening_mbid is A, its mbid is B and its mbid_status is Verified

### Requirement: One MBID names one artist
An MBID SHALL be the mbid or the listening_mbid of at most one Artist; one Artist may hold the same MBID as both. An Artist whose mbid was corrected keeps its listening_mbid, so the listening service's results still find the same Artist, with the same id.

#### Scenario: Corrected artist keeps its identity
- **WHEN** an artist with listening_mbid A has its mbid corrected from A to B
- **THEN** looking it up by A or by B finds the same artist, with the same id and followers

#### Scenario: One owner per MBID
- **WHEN** MBID A is the listening_mbid of one artist
- **THEN** no other artist has A as its mbid or its listening_mbid

## ADDED Requirements

### Requirement: Only a verified artist whose activity has not ended is offered
An Artist SHALL be offered to fans (in name search, charts and similar artists) only when its mbid_status is Verified and its activity_ended is false.

#### Scenario: Verified and active
- **WHEN** an artist's mbid_status is Verified and activity_ended is false
- **THEN** it is offered

#### Scenario: Not verified
- **WHEN** an artist's mbid_status is Unverified or Ambiguous
- **THEN** it is not offered, whatever its activity_ended

#### Scenario: Activity ended
- **WHEN** an artist's mbid_status is Verified and activity_ended is true
- **THEN** it is not offered
