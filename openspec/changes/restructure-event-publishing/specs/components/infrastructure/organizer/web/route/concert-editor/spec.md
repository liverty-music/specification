# Spec Delta

## ADDED Requirements

### Requirement: A published concert is corrected, not rewritten

The editor SHALL show each event's publish state. For a PUBLISHED event it SHALL show the venue and date as fixed and offer no way to remove the event; a CANCELLED event SHALL be shown as 中止 (cancelled) and not be editable. Once the concert has a PUBLISHED or CANCELLED event, the type, source page, visibility and performers SHALL be shown as fixed. An event the operator adds to a published concert SHALL be saved as a draft and shown as such until it is published. When a save is refused because tickets for an event are already on sale and its start time was changed, the editor SHALL say that the start time is fixed once tickets are on sale.

#### Scenario: Published event's venue is fixed
- **WHEN** an operator edits a concert with a PUBLISHED event
- **THEN** that event's venue and date are shown as fixed and the event has no remove control

#### Scenario: Additional date saved as a draft
- **WHEN** an operator adds a date to a published concert and saves
- **THEN** the save succeeds and the new date is shown as a draft

#### Scenario: Start time already on sale
- **WHEN** an operator changes the start time of an event whose tickets are on sale and saves
- **THEN** the editor says the start time is fixed once tickets are on sale, and nothing is saved
