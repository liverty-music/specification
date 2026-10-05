# Spec Delta

## ADDED Requirements

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

## REMOVED Requirements

### Requirement: Same series and same apply start time is the same sales phase

**Reason**: An exact start-time match created a second phase when a re-discovery read the time a few hours off. It also referred to the removed channel, sequence, provider name and url.
**Migration**: Replaced by "Same series, method and apply start date is the same sales phase". Stored phases are deleted by this change's migration, so no existing pair has to be merged.
