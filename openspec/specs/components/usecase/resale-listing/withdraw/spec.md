# components/usecase/resale-listing/withdraw Specification

## Purpose
ResaleListingUseCase.Withdraw lets a fan take back a ticket they listed for resale, as long as no other fan is buying it.

## Requirements

### Requirement: Withdraw the fan's own open listing

Withdraw SHALL take the calling fan, a ResaleListing and the current time. It SHALL read the listing with ResaleListing.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or its user is not the fan. It SHALL then call ResaleListing.Withdraw, return a failure unchanged, and return the listing as read again with ResaleListing.Get.

#### Scenario: Fan can attend after all
- **WHEN** a fan withdraws their open listing
- **THEN** the listing is returned Withdrawn and the Ticket is no longer for sale

#### Scenario: Already sold
- **WHEN** the fan withdraws a listing that is Sold
- **THEN** Withdraw fails with FailedPrecondition

#### Scenario: Someone else's listing
- **WHEN** a fan withdraws a listing of another User
- **THEN** Withdraw fails with PermissionDenied
