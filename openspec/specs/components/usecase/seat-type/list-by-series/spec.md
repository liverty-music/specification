# components/usecase/seat-type/list-by-series Specification

## Purpose
SeatTypeUseCase.ListBySeries shows an Organizer the seat types of one of its Series, so a member can stock an event with them.

## Requirements

### Requirement: A member of the owning Organizer lists a Series' seat types

ListBySeries SHALL take the caller's Organizer and a Series. It SHALL read the Series with Series.GetAuthored and fail with PermissionDenied, without revealing whether it exists, when it does not exist or is owned by another Organizer. It SHALL return the Series' SeatTypes from SeatType.ListBySeries, and an empty list when it has none.

#### Scenario: Two seat types
- **WHEN** a member lists a Series with S席 and A席
- **THEN** both are returned with their names and prices

#### Scenario: No seat type yet
- **WHEN** a member lists a Series without a SeatType
- **THEN** an empty list is returned

#### Scenario: Another Organizer's series
- **WHEN** a member lists the seat types of a Series owned by another Organizer
- **THEN** ListBySeries fails with PermissionDenied
