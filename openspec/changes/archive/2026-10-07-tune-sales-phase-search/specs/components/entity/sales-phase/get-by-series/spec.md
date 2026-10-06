# Spec Delta

## Purpose

GetBySeries returns every stored sales phase of one series, so a caller can tell whether the series already has a phase whose application has not ended.

## ADDED Requirements

### Requirement: Returns every phase of the series

GetBySeries SHALL return every stored sales phase of the given series, whatever its milestones, ordered by apply start time, earliest first. It SHALL return an empty list without an error for a series with no phase or a series that does not exist.

#### Scenario: Series with two phases

- **WHEN** a series has a lottery opening on 5 October and another opening on 10 November
- **THEN** GetBySeries returns both, the 5 October lottery first

#### Scenario: Series with no phase

- **WHEN** a series has no stored phase
- **THEN** GetBySeries returns an empty list without an error

### Requirement: A series is required

GetBySeries SHALL fail with InvalidArgument when no series is given.

#### Scenario: No series given

- **WHEN** GetBySeries is called without a series
- **THEN** it fails with InvalidArgument
