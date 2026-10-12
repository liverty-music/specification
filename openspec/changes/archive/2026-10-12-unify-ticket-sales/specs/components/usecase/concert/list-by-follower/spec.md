# Spec Delta

## REMOVED Requirements

### Requirement: Followed artists' concerts
**Reason**: No RPC or job calls the ungrouped ConcertUseCase.ListByFollower; `ConcertService.ListFollowed` runs ConcertUseCase.ListFollowed, which returns the same Concerts in proximity groups (design D17, unused surface removed).
**Migration**: Use ConcertUseCase.ListFollowed (`components/usecase/concert/list-followed`). The entity operation Concert.ListByFollower stays.
