# Spec Delta

## REMOVED Requirements

### Requirement: ResolveCanonicalName adopts the catalog's name
**Reason**: Merged into ArtistUseCase.Refresh, which adopts the catalog's name and also records whether the artist's activity has ended from the same catalog lookup.
**Migration**: The requirement "Refresh adopts the catalog's name and activity status" in components/usecase/artist/refresh carries the same name rule and scenarios.

### Requirement: ResolveCanonicalName reports failures
**Reason**: Merged into ArtistUseCase.Refresh.
**Migration**: See "Refresh reports failures" in components/usecase/artist/refresh. A catalog NotFound now succeeds without a change instead of failing, since retrying it cannot succeed.

### Requirement: ResolveCanonicalName runs when an artist is newly registered
**Reason**: Merged into ArtistUseCase.Refresh.
**Migration**: See "Refresh runs when an artist is newly registered" in components/usecase/artist/refresh, with the same retry count.
