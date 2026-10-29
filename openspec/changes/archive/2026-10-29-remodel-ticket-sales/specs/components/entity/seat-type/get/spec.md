# Spec Delta

## Purpose

Reads one SeatType by its id, with its Series, name and price, so a usecase can check who owns it and what one ticket of it costs.

## ADDED Requirements

### Requirement: Get a seat type

Get SHALL return the SeatType with the given id, with its Series, name and price. It SHALL fail with NotFound when no SeatType has the id.

#### Scenario: Seat type found
- **WHEN** a SeatType S席 priced 8000 yen exists and Get is called with its id
- **THEN** it is returned with its Series, the name S席 and the price 8000 yen

#### Scenario: Unknown seat type
- **WHEN** no SeatType has the id
- **THEN** Get fails with NotFound
