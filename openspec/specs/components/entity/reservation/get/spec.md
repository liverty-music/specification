# components/entity/reservation/get Specification

## Purpose
Reads one Reservation by its id, whatever its status.

## Requirements

### Requirement: Get returns the reservation

Get SHALL return the Reservation with the given id, whatever its status, and SHALL fail with NotFound when no Reservation has the id.

#### Scenario: Completed checkout

- **WHEN** a Completed Reservation is read
- **THEN** it is returned with status Completed

#### Scenario: Unknown reservation

- **WHEN** no Reservation has the id
- **THEN** Get fails with NotFound
