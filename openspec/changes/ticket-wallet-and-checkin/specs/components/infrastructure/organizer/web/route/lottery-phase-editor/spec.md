# Spec Delta

## ADDED Requirements

### Requirement: An event goes on sale only with its start time

When the event has no start time, the lottery phase editor SHALL say that the start time must be set in the concert editor before the event can go on sale, link to the concert editor, and SHALL not save the phase. An event without an open time SHALL go on sale as usual.

#### Scenario: Start time not set

- **WHEN** an operator opens the lottery phase editor for a published event with no start time
- **THEN** the screen says the start time must be set first, links to the concert editor, and saving is not offered
