# Spec Delta

## Purpose

ListBySeries returns every stored TicketSale of one series, so a caller can tell whether the series already has a sale that is not yet over.

## ADDED Requirements

### Requirement: Returns every sale of the series

ListBySeries SHALL return every stored TicketSale of the given series, whatever its times, ordered by start time, earliest first. It SHALL return an empty list without an error for a series with no sale or a series that does not exist.

#### Scenario: Series with two sales
- **WHEN** a series has a lottery opening on 5 October and another opening on 10 November
- **THEN** ListBySeries returns both, the 5 October lottery first

#### Scenario: Series with no sale
- **WHEN** a series has no stored sale
- **THEN** ListBySeries returns an empty list without an error

### Requirement: A series is required

ListBySeries SHALL fail with InvalidArgument when no series is given.

#### Scenario: No series given
- **WHEN** ListBySeries is called without a series
- **THEN** it fails with InvalidArgument
