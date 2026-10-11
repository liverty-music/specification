# Spec Delta

## REMOVED Requirements

### Requirement: Only the caller's own roster is listed
**Reason**: The organizer `ArtistService.List` request names no Organizer (RPC naming rule, design D11 and D15), so there is no named Organizer to compare with the caller's, and both the admin and the organizer artist calls read a roster through one usecase method (design D17).
**Migration**: The organizer `ArtistService.List` passes the caller's own Organizer, as OrganizerUseCase.ResolveCaller returned it, to ArtistUseCase.ListByOrganizer (`components/usecase/artist/list-by-organizer`); see `components/adapter/organizer/api/rpc/artist`.
