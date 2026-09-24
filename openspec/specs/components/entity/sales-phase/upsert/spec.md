# SalesPhase.Upsert

## Purpose

Upsert stores a discovered sales phase: it updates the known phase of the same series with the same apply start time, or creates a new phase when there is none. It reports whether the phase was inserted (newly created), updated or skipped, together with the phase's id.

## Requirements

### Requirement: Same series and same apply start time is the same sales phase

Upsert SHALL treat a discovered phase as the known phase of its series whose apply start time is the same instant, whatever its method, channel, sequence, provider name, other milestones or url. On a match it SHALL replace those descriptive attributes with the discovered values, keep the id, series, apply start time and discovered time, and return Updated with the existing id. Without a match it SHALL create a new phase with a new id and the current time as discovered time, and return Inserted with the new id. A discovered value that is absent SHALL clear the previously stored value.

#### Scenario: Re-discovery with more detail

- **WHEN** a phase already stored for a series is discovered again with the same apply start time and a newly announced apply end time
- **THEN** Upsert updates that phase with the apply end time and returns Updated with its id
- **AND** no second phase is created

#### Scenario: Reclassification does not duplicate

- **WHEN** a phase stored with channel `UNSPECIFIED` and sequence 0 is discovered again as channel `FAN_CLUB`, sequence 1, with the same apply start time
- **THEN** Upsert updates that phase in place and returns Updated

#### Scenario: Different start times stay separate

- **WHEN** a series has a stored fan-club presale and a general on-sale is discovered with a different apply start time
- **THEN** Upsert creates a new phase and returns Inserted with the new id

#### Scenario: Omitted value clears the stored one

- **WHEN** a stored phase has a url and is discovered again with the same apply start time and no url
- **THEN** Upsert updates the phase and its url becomes empty

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
