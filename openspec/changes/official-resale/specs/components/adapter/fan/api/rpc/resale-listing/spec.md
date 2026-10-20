## Purpose

The fan-facing resale listing service boundary (`ResaleListingService`): listing a ticket, withdrawing a listing and reading one's listings is for the signed-in fan, who is always the caller.

## ADDED Requirements

### Requirement: Listing calls are for the signed-in fan

Create, Withdraw and List SHALL require a signed-in caller and fail with Unauthenticated otherwise. They SHALL resolve the caller to their stored User with User.GetByProviderUserID, failing with NotFound when the caller has no stored account, and pass that User to ResaleListingUseCase.Create, ResaleListingUseCase.Withdraw and ResaleListingUseCase.List respectively; the request never names a user. Errors from the usecase SHALL be returned unchanged.

#### Scenario: Fan lists a ticket
- **WHEN** a signed-in fan calls Create for one of their Tickets
- **THEN** ResaleListingUseCase.Create runs for that fan and the listing is returned

#### Scenario: Guest calls
- **WHEN** a caller who is not signed in calls Create
- **THEN** the call fails with Unauthenticated and nothing is listed

### Requirement: Requests are validated before any usecase runs

Before any usecase runs, the boundary SHALL fail with InvalidArgument when Create's Ticket or Withdraw's ResaleListing is missing or malformed.

#### Scenario: Missing ticket
- **WHEN** Create is called without a Ticket
- **THEN** it fails with InvalidArgument and nothing is listed

### Requirement: A returned listing shows only the fan's own side

A ResaleListing returned by the fan boundary SHALL carry its id, Ticket, price, resale fee, refund amount, status (Listed, Sold, Withdrawn, Cancelled or Expired), create time, deadline, sold time and refund time. It SHALL NOT carry the Checkout that holds it or anything about the fan who bought it.

#### Scenario: Sold listing
- **WHEN** List returns a Sold listing
- **THEN** it carries its price, fee, refund amount, sold time and refund time, and nothing about the fan who bought it
