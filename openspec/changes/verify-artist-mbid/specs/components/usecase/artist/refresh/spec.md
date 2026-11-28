## REMOVED Requirements

### Requirement: Refresh runs when an artist is newly registered
**Reason**: A newly registered artist is read from the catalog by ArtistUseCase.VerifyMBID, which checks its MBID against namesakes before adopting the catalog's name and activity status; running Refresh as well would read the same MBID twice.
**Migration**: The artist-created announcement runs ArtistUseCase.VerifyMBID (components/usecase/artist/verify-mbid). The daily run of Refresh is unchanged.
