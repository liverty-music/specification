## MODIFIED Requirements

### Requirement: UpsertDiscovered rejects a sale without a valid series or name

UpsertDiscovered SHALL fail with InvalidArgument when the discovered sale names no series, has no name, has no time zone, or breaks the TicketSale rules for a discovered sale. It SHALL fail with FailedPrecondition when the named series does not exist or has an Organizer.

#### Scenario: No series
- **WHEN** UpsertDiscovered receives a discovered sale without a series
- **THEN** it fails with InvalidArgument and stores nothing

#### Scenario: No name
- **WHEN** UpsertDiscovered receives a discovered sale without a name
- **THEN** it fails with InvalidArgument and stores nothing

#### Scenario: No time zone
- **WHEN** UpsertDiscovered receives a discovered sale opening on 1 November 12:00 without a time zone
- **THEN** it fails with InvalidArgument and stores nothing

#### Scenario: Unknown series
- **WHEN** UpsertDiscovered receives a discovered sale for a series that does not exist
- **THEN** it fails with FailedPrecondition and stores nothing

#### Scenario: Series of an Organizer
- **WHEN** UpsertDiscovered receives a discovered sale for a series that an Organizer owns
- **THEN** it fails with FailedPrecondition and stores nothing

### Requirement: Same series, method and start date is one discovered sale

UpsertDiscovered SHALL treat a discovered sale as the known discovered sale that has the same series and method and a start time on the same calendar day, each sale's start date being the date of its local start date-time in its own time zone. On a match it SHALL replace the name, time zone, start time and end time with the discovered values, and SHALL replace the result date only when the discovered sale has one, so a stored result date is never removed by a discovery that did not read it; a stored result date that falls before the calendar day of the new end time, in the sale's time zone, SHALL be cleared, because a corrected end time made it impossible. It SHALL keep the id, series, method and find time, and return Updated with the existing id. Without a match it SHALL create a new discovered sale, with the result date when the discovered sale has one, a new id and the current time as find time, and return Inserted with the new id.

#### Scenario: Re-discovery with a corrected time
- **WHEN** a lottery stored as opening on 5 October 16:00 Asia/Tokyo is discovered again as opening on 5 October 18:00 Asia/Tokyo
- **THEN** UpsertDiscovered updates that sale to open at 18:00 and returns Updated with its id
- **AND** no second sale is created

#### Scenario: Late-evening sale abroad keeps its date
- **WHEN** a lottery stored as opening on 1 November 23:30 Asia/Taipei, which is 2 November in Japan time, is discovered again as opening on 1 November 22:30 Asia/Taipei, which is 1 November in Japan time
- **THEN** UpsertDiscovered updates that sale to open at 22:30 and returns Updated with its id
- **AND** no second sale is created

#### Scenario: Re-discovery with a new name
- **WHEN** a stored lottery named 先行抽選 is discovered again on the same start date named オフィシャル先行
- **THEN** UpsertDiscovered updates the sale's name to オフィシャル先行 and returns Updated

#### Scenario: Re-discovery adds a result date
- **WHEN** a stored lottery has no result date and is discovered again on the same start date with the result date 3 November
- **THEN** UpsertDiscovered stores the result date 3 November and returns Updated

#### Scenario: Re-discovery without a result date keeps the stored one
- **WHEN** a stored lottery has the result date 3 November and is discovered again on the same start date without a result date
- **THEN** the sale keeps the result date 3 November

#### Scenario: A later end time clears an impossible result date
- **WHEN** a stored lottery ends on 20 October with the result date 22 October and is discovered again on the same start date ending on 25 October, without a result date
- **THEN** the sale ends on 25 October and has no result date

#### Scenario: New lottery with a result date
- **WHEN** a lottery that matches no stored sale is discovered with the result date 3 November
- **THEN** UpsertDiscovered creates the sale with the result date 3 November and returns Inserted

#### Scenario: Different start dates stay separate
- **WHEN** a series has a stored lottery opening on 5 October and a lottery opening on 10 November is discovered
- **THEN** UpsertDiscovered creates a new sale and returns Inserted with the new id

#### Scenario: Different methods on one day stay separate
- **WHEN** a series has a stored lottery opening on 5 October and a first-come sale opening on 5 October is discovered
- **THEN** UpsertDiscovered creates a new sale and returns Inserted
