# Spec Delta

## Purpose

Lists the Scanners issued for one event, in the order of their numbers.

## ADDED Requirements

### Requirement: Scanners of an event

ListByEvent SHALL return every Scanner of the given event, Revoked ones included, in order of their number, and SHALL return an empty list when the event has none.

#### Scenario: Event with scanners

- **WHEN** the event has Scanners 1 (InUse) and 2 (Revoked)
- **THEN** both are returned, 1 first

#### Scenario: Event without scanners

- **WHEN** the event has no Scanner
- **THEN** an empty list is returned
