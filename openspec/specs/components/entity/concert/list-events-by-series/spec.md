# Concert.ListEventsBySeries

## Purpose

Lists the Events belonging to a Series, in date order, so a caller can resolve which of its Events to link to without hydrating the full Concert DTO.

## Requirements

### Requirement: Events of a series in date order

ListEventsBySeries SHALL return every Event whose Series matches the given series id, each with its id, local date and start time, ordered by local date ascending and, for equal dates, by start time ascending with an absent start time ordered last. Given a series with no Event it SHALL return an empty list without error.

#### Scenario: Two events, one after the other

- **WHEN** a series has an Event on 2026-06-01 and one on 2026-06-15
- **THEN** the 2026-06-01 Event is returned before the 2026-06-15 Event

#### Scenario: Series with no event

- **WHEN** a series has no Event
- **THEN** an empty list is returned
