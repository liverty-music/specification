# Spec Delta

## Purpose

UpsertDiscovered stores a sale found by discovery as a discovered TicketSale. It updates the known discovered sale with the same series, method and start date in Japan time, or creates a new one, and reports whether the sale was inserted, updated or skipped, together with its id.

## ADDED Requirements

### Requirement: A sale without a known start is skipped

UpsertDiscovered SHALL store nothing for a discovered sale whose start time is unknown, and SHALL return Skipped with no id and no error.

#### Scenario: Unknown start
- **WHEN** UpsertDiscovered receives a discovered sale with no start time
- **THEN** nothing is stored and UpsertDiscovered returns Skipped without an error

### Requirement: UpsertDiscovered never removes a sale

UpsertDiscovered SHALL only create or update sales; a sale SHALL never be removed because a later discovery did not include it.

#### Scenario: Sale no longer discovered
- **WHEN** a series has a stored discovered sale and a later discovery for the series returns no sales
- **THEN** the stored sale remains unchanged

### Requirement: UpsertDiscovered rejects a sale without a valid series

UpsertDiscovered SHALL fail with InvalidArgument when the discovered sale names no series or breaks the TicketSale rules for a discovered sale. It SHALL fail with FailedPrecondition when the named series does not exist or has an Organizer.

#### Scenario: No series
- **WHEN** UpsertDiscovered receives a discovered sale without a series
- **THEN** it fails with InvalidArgument and stores nothing

#### Scenario: Unknown series
- **WHEN** UpsertDiscovered receives a discovered sale for a series that does not exist
- **THEN** it fails with FailedPrecondition and stores nothing

#### Scenario: Series of an Organizer
- **WHEN** UpsertDiscovered receives a discovered sale for a series that an Organizer owns
- **THEN** it fails with FailedPrecondition and stores nothing

#### Scenario: Lottery without a close
- **WHEN** UpsertDiscovered receives a discovered Lottery sale without an end time
- **THEN** it fails with InvalidArgument and stores nothing

### Requirement: Same series, method and start date is the same discovered sale

UpsertDiscovered SHALL treat a discovered sale as the known discovered sale that has the same series and method and a start time on the same calendar day in Japan time (Asia/Tokyo). On a match it SHALL replace the start time, end time and lottery result time with the discovered values. It SHALL keep the id, series, method and discovered time, and return Updated with the existing id. Without a match it SHALL create a new discovered sale with a new id and the current time as discovered time, and return Inserted with the new id. A discovered value that is absent SHALL clear the previously stored value.

#### Scenario: Re-discovery with a corrected time
- **WHEN** a lottery stored as opening on 5 October 16:00 is discovered again as opening on 5 October 18:00
- **THEN** UpsertDiscovered updates that sale to open at 18:00 and returns Updated with its id
- **AND** no second sale is created

#### Scenario: Re-discovery with more detail
- **WHEN** a stored lottery is discovered again with the same series and start date and a newly announced lottery result time
- **THEN** UpsertDiscovered updates that sale with the lottery result time and returns Updated

#### Scenario: Different start dates stay separate
- **WHEN** a series has a stored lottery opening on 5 October and a lottery opening on 10 November is discovered
- **THEN** UpsertDiscovered creates a new sale and returns Inserted with the new id

#### Scenario: Different methods on one day stay separate
- **WHEN** a series has a stored lottery opening on 5 October and a first-come sale opening on 5 October is discovered
- **THEN** UpsertDiscovered creates a new sale and returns Inserted

#### Scenario: Omitted value clears the stored one
- **WHEN** a stored lottery has a lottery result time and is discovered again on the same start date without one
- **THEN** UpsertDiscovered updates the sale and its lottery result time becomes empty
