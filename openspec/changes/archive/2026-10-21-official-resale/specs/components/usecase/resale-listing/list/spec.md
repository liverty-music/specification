## Purpose

ResaleListingUseCase.List tells a fan what they listed for resale, where each listing stands and how much is refunded.

## ADDED Requirements

### Requirement: The fan's listings with their deadline

List SHALL take the calling fan and the current time and return the fan's listings from ResaleListing.ListByUser, each with its resale fee, its refund amount and its deadline, read from its Ticket's event with Event.Get. A Listed listing that is expired at the current time SHALL be returned Expired. It SHALL return an empty list when the fan has no listing.

#### Scenario: Listing on sale
- **WHEN** a fan with one open listing priced 5000 yen reads their listings
- **THEN** it is returned Listed with the fee 500 yen, the refund amount 4500 yen and its deadline

#### Scenario: Listing that did not sell
- **WHEN** the fan reads a Listed listing after its deadline
- **THEN** it is returned Expired

#### Scenario: Sold and refunded
- **WHEN** the fan reads a Sold listing whose refund was recorded
- **THEN** it is returned Sold with its sold time and refund time
