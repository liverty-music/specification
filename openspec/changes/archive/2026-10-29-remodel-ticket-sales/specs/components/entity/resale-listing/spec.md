# Spec Delta

## ADDED Requirements

### Requirement: Withdrawable while open

A ResaleListing SHALL be withdrawable at a time when it is open at that time.

#### Scenario: Open listing
- **WHEN** a Listed listing is checked before its deadline
- **THEN** it is withdrawable

#### Scenario: Expired listing
- **WHEN** a Listed listing is checked at its deadline
- **THEN** it is not withdrawable

## REMOVED Requirements

### Requirement: Free to hold

**Reason**: A Checkout no longer holds listings; official resale purchases become a lottery in the change resell-tickets-by-lottery, which states how a listing is allocated and until when it can be withdrawn.
**Migration**: See "Withdrawable while open"; resale Checkouts are deleted with the rest of the Organizer sales' data (design "Migration Plan").
