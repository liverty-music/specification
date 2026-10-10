# Spec Delta

## Purpose

ListBySeries returns the ticket sale search logs of the given series, so discovery can tell which series were searched recently.

## ADDED Requirements

### Requirement: Returns the logs that exist

ListBySeries SHALL return the log of each given series that has one, and SHALL return nothing for a series that was never searched. The result has no particular order. An empty input SHALL return an empty result.

#### Scenario: One searched, one never searched
- **WHEN** ListBySeries is called with series A, last searched on 1 October, and series B, never searched
- **THEN** it returns only the log of series A, with searched time 1 October

#### Scenario: No series given
- **WHEN** ListBySeries is called with no series
- **THEN** it returns an empty result without an error
