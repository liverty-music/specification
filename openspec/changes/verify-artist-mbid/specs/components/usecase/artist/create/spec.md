## MODIFIED Requirements

### Requirement: Create registers the artist under the catalog's canonical name
ArtistUseCase.Create SHALL take an artist with a name and an MBID, look the MBID up with Artist.GetArtist and, when the catalog's name differs from the given name, register the artist with the catalog's name and MBID; otherwise with the given name. When the lookup fails, Create SHALL register the artist with the given name and activity_ended false and SHALL NOT fail. The artist is registered with Artist.Create with the MBID as both its listening MBID and its MBID, mbid_status Verified, since the caller names the MBID rather than the listening service, and the activity status the lookup returned. Create returns the artist that Artist.Create returns for it, which is the already registered artist when the MBID is known.

#### Scenario: Catalog has a different name
- **WHEN** Create is called with the name "the band" and an MBID whose catalog name is "The Band"
- **THEN** the artist is registered and returned with the name "The Band" and mbid_status Verified

#### Scenario: Catalog lookup fails
- **WHEN** Create is called and Artist.GetArtist fails with Unavailable
- **THEN** the artist is registered and returned with the given name, mbid_status Verified and activity_ended false

#### Scenario: Ended artist registered
- **WHEN** Create is called with an MBID whose catalog activity has ended
- **THEN** the artist is registered with activity_ended true

#### Scenario: Test artist
- **WHEN** Create is called with the name "E2E Test Artist" and a generated MBID the catalog does not know
- **THEN** the artist is registered with that name, mbid_status Verified and activity_ended false, and its announcement verifies nothing

#### Scenario: MBID already registered
- **WHEN** Create is called with an MBID that is already registered
- **THEN** the already registered artist is returned unchanged, whatever its mbid_status, and no second artist is registered
