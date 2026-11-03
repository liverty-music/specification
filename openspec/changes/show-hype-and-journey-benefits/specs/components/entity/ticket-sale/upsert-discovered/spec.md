## MODIFIED Requirements

### Requirement: Same series, method and start date is one discovered sale

UpsertDiscovered SHALL treat a discovered sale as the known discovered sale that has the same series and method and a start time on the same calendar day in Japan time (Asia/Tokyo). On a match it SHALL replace the name, start time and end time with the discovered values, and SHALL replace the result date only when the discovered sale has one, so a stored result date is never removed by a discovery that did not read it; a stored result date that falls before the calendar day, in Japan time, of the new end time SHALL be cleared, because a corrected end time made it impossible. It SHALL keep the id, series, method and discovered time, and return Updated with the existing id. Without a match it SHALL create a new discovered sale, with the result date when the discovered sale has one, a new id and the current time as discovered time, and return Inserted with the new id.

#### Scenario: Re-discovery with a corrected time
- **WHEN** a lottery stored as opening on 5 October 16:00 is discovered again as opening on 5 October 18:00
- **THEN** UpsertDiscovered updates that sale to open at 18:00 and returns Updated with its id
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
