## REMOVED Requirements

### Requirement: ListSimilar announces newly registered artists
**Reason**: Artist.Create announces each artist it registers together with the registration, and only an artist it registered (components/entity/artist/create), so ArtistUseCase.ListSimilar no longer announces.
**Migration**: ArtistUseCase.ResolveCanonicalName and ArtistUseCase.SyncArtistImage receive the creation from that announcement. A failure to announce now fails Artist.Create, so ListSimilar fails with Unavailable and registers none of the new artists; an artist that was already registered is no longer announced again.
