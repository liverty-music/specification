## MODIFIED Requirements

### Requirement: CorrectMBID gives the artist the right person's identity
ArtistUseCase.CorrectMBID SHALL take an artist id and an MBID, read the artist, look the MBID up with Artist.GetArtist, set the artist's mbid to the MBID the catalog returned for it (the canonical MBID, which differs from the given one when the catalog redirects a merged MBID) with Artist.UpdateMBID, which marks the artist Verified and keeps its listening_mbid, and then adopt the catalog's name and activity status as Refresh does. It SHALL return the corrected artist. It SHALL look the MBID up before changing anything, so an MBID the catalog does not know stores nothing. It is how an admin resolves an Ambiguous artist, whatever the artist's mbid_status.

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
- **THEN** the artist keeps its details, becomes Verified, and the catalog's name and activity status are adopted again
