# Spec Delta

## REMOVED Requirements

### Requirement: ListArtists lists only the caller's own roster
**Reason**: A read of Artists belongs to ArtistService under the RPC naming rule, and the caller's own Organizer comes from the sign-in, so the request no longer names an Organizer (design D15). `OrganizerService.ListArtists(organizer_id)` becomes the organizer `ArtistService.List()`.
**Migration**: The behavior continues in `components/adapter/organizer/api/rpc/artist`; the organizer console calls `ArtistService.List()` with no OrganizerId.
