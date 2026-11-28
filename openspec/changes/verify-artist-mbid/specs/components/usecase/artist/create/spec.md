## MODIFIED Requirements

### Requirement: Create registers the artist under the catalog's canonical name
ArtistUseCase.Create SHALL take an artist with a name and an MBID, look the MBID up with Artist.GetArtist and, when the catalog's name differs from the given name, register the artist with the catalog's name and MBID; otherwise with the given name. When the lookup fails, Create SHALL register the artist with the given name and SHALL NOT fail. The artist is registered with Artist.Create with the MBID as both its listening MBID and its MBID and mbid_status Unverified, like any artist found through the listening service, so its announcement runs ArtistUseCase.VerifyMBID, which checks the MBID against its namesakes and adopts the catalog's activity status; Create returns the artist that Artist.Create returns for it, which is the already registered artist when the MBID is known.

#### Scenario: Catalog has a different name
- **WHEN** Create is called with the name "the band" and an MBID whose catalog name is "The Band"
- **THEN** the artist is registered and returned with the name "The Band" and mbid_status Unverified

#### Scenario: Catalog lookup fails
- **WHEN** Create is called and Artist.GetArtist fails with Unavailable
- **THEN** the artist is registered and returned with the given name

#### Scenario: MBID already registered
- **WHEN** Create is called with an MBID that is already registered
- **THEN** the already registered artist is returned unchanged, whatever its mbid_status, and no second artist is registered
