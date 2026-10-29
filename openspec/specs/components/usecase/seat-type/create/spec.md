# components/usecase/seat-type/create Specification

## Purpose
SeatTypeUseCase.Create lets an Organizer add a seat type (席種), with its name and price, to one of its Series, so that its events can stock tickets of it.

## Requirements

### Requirement: Only the owner adds a seat type

Create SHALL take the caller's Organizer, a Series, a name and a price. It SHALL read the Series with Series.GetAuthored and fail with PermissionDenied, without revealing whether it exists, when it does not exist or is owned by another Organizer. It SHALL fail with InvalidArgument, storing nothing, when the name or price breaks the SeatType rules. It SHALL then store the SeatType with SeatType.Create and return it; SeatType.Create fails with AlreadyExists when the Series already has a SeatType of that name, and its failures are returned unchanged.

#### Scenario: Owner adds S席
- **WHEN** the owner adds S席 at 8000 yen to their Series
- **THEN** the SeatType is stored and returned

#### Scenario: Another Organizer's series
- **WHEN** a member adds a seat type to a Series owned by another Organizer
- **THEN** Create fails with PermissionDenied and nothing is stored

#### Scenario: Same name twice
- **WHEN** the Series already has S席 and the owner adds S席 at 9000 yen
- **THEN** Create fails with AlreadyExists and nothing is stored

#### Scenario: Price out of range
- **WHEN** the price is 0 yen
- **THEN** Create fails with InvalidArgument and nothing is stored
