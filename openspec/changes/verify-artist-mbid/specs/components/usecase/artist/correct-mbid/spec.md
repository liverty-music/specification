## MODIFIED Requirements

### Requirement: CorrectMBID gives the artist the right person's identity
ArtistUseCase.CorrectMBID SHALL take an artist id and an MBID, read the artist, look the MBID up with Artist.GetArtist, and store with one Artist.UpdateMBID the MBID the catalog returned for it (the canonical MBID, which differs from the given one when the catalog redirects a merged MBID) with the catalog's name (when not empty; otherwise the current name) and activity status; UpdateMBID marks the artist Verified and keeps its listening_mbid. It SHALL return the corrected artist. It SHALL look the MBID up before changing anything, so an MBID the catalog does not know stores nothing. It is how an admin resolves an Ambiguous artist, whatever the artist's mbid_status.

#### Scenario: Namesake corrected
- **WHEN** an Ambiguous artist registered with a namesake's MBID is corrected with the MBID of the right person
- **THEN** the artist has the new mbid, the catalog's name and activity status, mbid_status Verified and its listening_mbid unchanged, and it keeps its id

#### Scenario: Redirected MBID
- **WHEN** the catalog answers the given MBID with another, canonical MBID
- **THEN** the artist's mbid becomes the canonical one, and another artist having the canonical MBID fails the correction with AlreadyExists

#### Scenario: Catalog does not know the MBID
- **WHEN** Artist.GetArtist fails with NotFound for the given MBID
- **THEN** CorrectMBID fails with NotFound and the artist is unchanged

#### Scenario: Same MBID again
- **WHEN** CorrectMBID is called for an Ambiguous artist with its current mbid
- **THEN** the artist keeps its images and official site, becomes Verified, and the catalog's name and activity status are adopted again

## REMOVED Requirements

### Requirement: CorrectMBID reports failures
**Reason**: CorrectMBID now reads everything from the catalog before it stores anything, so a failure can no longer leave a stored MBID without the catalog's name and activity status; the requirement below replaces it.
**Migration**: See "CorrectMBID fails without a partial change".

## ADDED Requirements

### Requirement: CorrectMBID fails without a partial change
ArtistUseCase.CorrectMBID SHALL fail with InvalidArgument for an MBID that is not 36 characters, with NotFound when no artist has the id, with AlreadyExists when another artist has the MBID, and with the error of Artist.GetArtist or Artist.UpdateMBID, leaving the artist unchanged in every case.

#### Scenario: Malformed MBID
- **WHEN** the MBID is not 36 characters long
- **THEN** CorrectMBID fails with InvalidArgument and looks nothing up

#### Scenario: Unknown artist
- **WHEN** no artist has the id
- **THEN** CorrectMBID fails with NotFound

#### Scenario: MBID of another artist
- **WHEN** another artist has the MBID
- **THEN** CorrectMBID fails with AlreadyExists and the artist is unchanged

#### Scenario: Catalog unavailable
- **WHEN** Artist.GetArtist fails with Unavailable
- **THEN** CorrectMBID fails with Unavailable and the artist is unchanged
