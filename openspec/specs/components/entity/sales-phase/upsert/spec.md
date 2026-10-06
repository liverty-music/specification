# SalesPhase.Upsert

## Purpose

Upsert stores a discovered sales phase. It updates the known phase that has the same series, method and apply start date, or creates a new phase when there is none. It reports whether the phase was inserted (newly created), updated or skipped, together with the phase's id.

## Requirements

### Requirement: A phase without a known start is skipped

Upsert SHALL store nothing for a discovered phase whose apply start time is unknown, and SHALL return Skipped with no id and no error.

#### Scenario: Unknown start

- **WHEN** Upsert receives a discovered phase with no apply start time
- **THEN** nothing is stored and Upsert returns Skipped without an error

### Requirement: Upsert never removes a phase

Upsert SHALL only create or update phases; a phase SHALL never be removed because a later discovery did not include it.

#### Scenario: Phase no longer discovered

- **WHEN** a series has a stored phase and a later discovery for the series returns no phases
- **THEN** the stored phase remains unchanged

### Requirement: Upsert rejects a phase without a valid series

Upsert SHALL fail with InvalidArgument when the discovered phase names no series, and with FailedPrecondition when the named series does not exist.

#### Scenario: No series

- **WHEN** Upsert receives a discovered phase without a series
- **THEN** it fails with InvalidArgument and stores nothing

#### Scenario: Unknown series

- **WHEN** Upsert receives a discovered phase for a series that does not exist
- **THEN** it fails with FailedPrecondition and stores nothing

### Requirement: Same series, method and apply start date is the same sales phase

Upsert SHALL treat a discovered phase as the known phase that has the same series and method, and an apply start time on the same calendar day in Japan time (Asia/Tokyo). On a match it SHALL replace the apply start time, apply end time and lottery result time with the discovered values. It SHALL keep the id, series, method and discovered time, and return Updated with the existing id. Without a match it SHALL create a new phase with a new id and the current time as discovered time, and return Inserted with the new id. A discovered value that is absent SHALL clear the previously stored value.

#### Scenario: Re-discovery with a corrected time

- **WHEN** a lottery stored as opening on 5 October 16:00 is discovered again as opening on 5 October 18:00
- **THEN** Upsert updates that phase to open at 18:00 and returns Updated with its id
- **AND** no second phase is created

#### Scenario: Re-discovery with more detail

- **WHEN** a stored lottery is discovered again with the same series and start date and a newly announced lottery result time
- **THEN** Upsert updates that phase with the lottery result time and returns Updated

#### Scenario: Different start dates stay separate

- **WHEN** a series has a stored lottery opening on 5 October and a lottery opening on 10 November is discovered
- **THEN** Upsert creates a new phase and returns Inserted with the new id

#### Scenario: Different methods on one day stay separate

- **WHEN** a series has a stored lottery opening on 5 October and a first-come sale opening on 5 October is discovered
- **THEN** Upsert creates a new phase and returns Inserted

#### Scenario: Omitted value clears the stored one

- **WHEN** a stored lottery has a lottery result time and is discovered again on the same start date without one
- **THEN** Upsert updates the phase and its lottery result time becomes empty
