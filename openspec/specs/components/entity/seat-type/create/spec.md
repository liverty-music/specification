# components/entity/seat-type/create Specification

## Purpose
Stores a new SeatType of a first-party Series, with its name and price, so the Series' events can be stocked with it.

## Requirements

### Requirement: Store a seat type

Create SHALL store a SeatType with the given Series, name and price and return it. It SHALL fail with InvalidArgument when the SeatType breaks the SeatType rules, with FailedPrecondition when the Series does not exist or is not first-party, and with AlreadyExists when the Series already has a SeatType with the same name, storing nothing.

#### Scenario: Seat type stored
- **WHEN** Create is called for a first-party Series with S席 at 8000 yen
- **THEN** the SeatType is stored and returned

#### Scenario: Same name twice
- **WHEN** the Series already has a SeatType named S席
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Discovered series
- **WHEN** the Series has no Organizer
- **THEN** Create fails with FailedPrecondition and stores nothing

#### Scenario: Invalid price
- **WHEN** the price is 0 yen
- **THEN** Create fails with InvalidArgument and stores nothing
