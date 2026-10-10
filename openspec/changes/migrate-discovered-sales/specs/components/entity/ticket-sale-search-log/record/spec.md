# Spec Delta

## Purpose

Record stores that the given series were searched for published ticket sales at a given time, replacing any earlier searched time of those series.

## ADDED Requirements

### Requirement: Record sets the searched time of every given series

Record SHALL set the searched time of each given series to the given time, creating the series' log when it has none and replacing the earlier searched time otherwise. Either every given series is recorded or none is. An empty input SHALL record nothing without an error.

#### Scenario: Series searched again
- **WHEN** series A was last searched on 1 September and Record is called for series A at 1 October
- **THEN** series A's searched time becomes 1 October

#### Scenario: Series searched for the first time
- **WHEN** Record is called for a series that has no log
- **THEN** a log is created for it with the given time

### Requirement: Record rejects an unknown series

Record SHALL fail with FailedPrecondition and record nothing when any given series does not exist.

#### Scenario: Unknown series
- **WHEN** Record is called for two series and one of them does not exist
- **THEN** it fails with FailedPrecondition and neither series is recorded
