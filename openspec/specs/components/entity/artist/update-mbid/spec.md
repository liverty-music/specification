# components/entity/artist/update-mbid Specification

## Purpose
Replaces the MBID of a registered artist whose MBID names a namesake, keeps the replaced MBID so a later search still finds the artist, and clears what was read from the namesake.

## Requirements

### Requirement: UpdateMBID replaces the MBID and remembers the old one
UpdateMBID SHALL set the MBID of the artist with the given id to the given MBID and add the replaced MBID to the artist's other_mbids, without repeating one and without keeping the new MBID among them. It SHALL fail with NotFound when no artist has the id, with InvalidArgument when the MBID is not a UUID of 36 characters, and with AlreadyExists, changing nothing, when another artist has the MBID as its MBID or among its other_mbids. Given the artist's own MBID, it SHALL succeed and change nothing. It SHALL announce nothing.

#### Scenario: New MBID
- **WHEN** UpdateMBID is called for an artist with MBID A and other_mbids empty, with MBID B
- **THEN** the artist's MBID is B and its other_mbids is A

#### Scenario: Second correction
- **WHEN** the artist's MBID is B and its other_mbids is A, and UpdateMBID is called with C
- **THEN** its MBID is C and its other_mbids is A and B

#### Scenario: Back to an earlier MBID
- **WHEN** the artist's MBID is B and its other_mbids is A, and UpdateMBID is called with A
- **THEN** its MBID is A and its other_mbids is B

#### Scenario: Own MBID
- **WHEN** UpdateMBID is called with the artist's current MBID
- **THEN** it succeeds and nothing changes, including the images, the official site and activity_ended

#### Scenario: MBID of another artist
- **WHEN** another artist has the given MBID as its MBID or among its other_mbids
- **THEN** UpdateMBID fails with AlreadyExists and the artist keeps its MBID and other_mbids

#### Scenario: Unknown artist
- **WHEN** UpdateMBID is called with an id no artist has
- **THEN** it fails with NotFound

#### Scenario: Malformed MBID
- **WHEN** the given MBID is not 36 characters long
- **THEN** it fails with InvalidArgument and nothing changes

### Requirement: UpdateMBID clears what came from the replaced MBID
When UpdateMBID changes the MBID, it SHALL in the same change remove the artist's images (fanart) and fanart_sync_time, remove its official_site_check_time, set activity_ended to false, and remove its official site, so that none of them still describes the person of the replaced MBID.

#### Scenario: Namesake's details removed
- **WHEN** an artist with images, an official site, an official_site_check_time and activity_ended true has its MBID replaced
- **THEN** it has no images, no fanart_sync_time, no official site and no official_site_check_time, and activity_ended is false

### Requirement: UpdateMBID cannot race with a registration
UpdateMBID and Artist.Create SHALL not run their MBID checks at the same time: while one is running, the other waits. After UpdateMBID has replaced an MBID, a Create of the replaced MBID SHALL return the corrected artist and register nothing.

#### Scenario: Registered at the same time
- **WHEN** UpdateMBID replaces MBID A of an artist while Create is called with an artist of MBID A
- **THEN** one registered artist, the corrected one, holds MBID A as an other MBID, and no artist is registered with MBID A
