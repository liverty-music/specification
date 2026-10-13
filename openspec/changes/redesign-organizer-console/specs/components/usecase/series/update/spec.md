# Spec Delta

## MODIFIED Requirements

### Requirement: Same validation as a new draft

Update SHALL reject unrepresented performers with PermissionDenied and invalid input with InvalidArgument exactly as Create does, except that the date of a PUBLISHED or CANCELLED Event is not checked against the current day. Each new or DRAFT event SHALL give the place id of a picked place, failing with InvalidArgument and changing nothing without one, and its Venue SHALL be found or created from that place as Create does. The venue given for a PUBLISHED or CANCELLED Event SHALL NOT be read: that Event keeps its Venue, so a date published before venues were picked from the map catalog can still be corrected.

#### Scenario: Doors after start
- **WHEN** an updated event opens after it starts
- **THEN** Update fails with InvalidArgument

#### Scenario: Correcting a past published date
- **WHEN** a PUBLISHED Event dated yesterday is given unchanged with a new open time
- **THEN** Update does not fail for the date

#### Scenario: Published date without a place id
- **WHEN** the owner corrects the title of a Series whose PUBLISHED Event's Venue has no place id, giving that Event without a place id
- **THEN** the title is changed and the Event keeps its Venue

#### Scenario: New date without a place id
- **WHEN** the owner adds an event without an id and without a place id
- **THEN** Update fails with InvalidArgument and nothing changes

### Requirement: Corrections keep what publish fixed

Update SHALL read the Series with its Events (Series.GetAuthored) and fail with FailedPrecondition, changing nothing, when:
- a PUBLISHED or CANCELLED Event of the Series is not given, because a published date is cancelled, not removed;
- a given PUBLISHED Event's date differs from the Event's;
- a given CANCELLED Event differs from the Event in any value other than its venue;
- the Series has a PUBLISHED or CANCELLED Event and the given type, source page or visibility differ from the Series';
- a given PUBLISHED Event's start time differs from the Event's and TicketSale.ListByEvent returns at least one sale for the Event.

#### Scenario: Published date moved
- **WHEN** the owner gives a PUBLISHED Event with another date
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Published venue changed
- **WHEN** the owner gives a PUBLISHED Event with the place id of another venue
- **THEN** the Event keeps its Venue

#### Scenario: Published date left out
- **WHEN** the owner updates a Series and leaves out one of its PUBLISHED Events
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Visibility changed after publish
- **WHEN** the owner changes a Series with a PUBLISHED Event from PUBLIC to UNLISTED
- **THEN** Update fails with FailedPrecondition

#### Scenario: Start time on sale
- **WHEN** the owner changes the start time of a PUBLISHED Event that a TicketSale offers
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Start time before any sale
- **WHEN** the owner sets the start time of a PUBLISHED Event that no TicketSale offers
- **THEN** the start time is set
