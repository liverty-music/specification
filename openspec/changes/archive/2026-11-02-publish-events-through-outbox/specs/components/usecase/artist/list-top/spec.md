## REMOVED Requirements

### Requirement: ListTop announces newly registered artists
**Reason**: Artist.Create announces each artist it registers together with the registration, and only an artist it registered (components/entity/artist/create), so ArtistUseCase.ListTop no longer announces.
**Migration**: ArtistUseCase.ResolveCanonicalName and ArtistUseCase.SyncArtistImage receive the creation from that announcement. A failure to announce now fails Artist.Create, so ListTop fails with Unavailable and registers none of the new artists; an artist that was already registered is no longer announced again.
