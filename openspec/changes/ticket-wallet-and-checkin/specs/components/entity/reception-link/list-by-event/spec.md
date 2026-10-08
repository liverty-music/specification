# Spec Delta

## Purpose

Lists the ReceptionLinks issued for one event.

## ADDED Requirements

### Requirement: Links of an event

ListByEvent SHALL return every ReceptionLink of the given event, Revoked ones included, in the order they were created, and SHALL return an empty list when the event has none.

#### Scenario: Event with links

- **WHEN** the event has links `受付A` (InUse) and `受付B` (Revoked)
- **THEN** both are returned, `受付A` first

#### Scenario: Event without links

- **WHEN** the event has no link
- **THEN** an empty list is returned
