# components/entity/reception-link/list-by-event Specification

## Purpose
Lists the ReceptionLinks issued for one event.

## Requirements

### Requirement: Links of an event

ListByEvent SHALL return every ReceptionLink of the given event, Revoked ones included, in order of their number, and SHALL return an empty list when the event has none.

#### Scenario: Event with links

- **WHEN** the event has links 1 (InUse) and 2 (Revoked)
- **THEN** both are returned, 1 first

#### Scenario: Event without links

- **WHEN** the event has no link
- **THEN** an empty list is returned
