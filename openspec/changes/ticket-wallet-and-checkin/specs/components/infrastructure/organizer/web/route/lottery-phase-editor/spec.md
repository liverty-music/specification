# Spec Delta

## ADDED Requirements

### Requirement: An event goes on sale only with its times

When the event has no open time or no start time, the lottery phase editor SHALL say that both must be set in the concert editor before the event can go on sale, link to the concert editor, and SHALL not save the phase.

#### Scenario: Start time not set

- **WHEN** an operator opens the lottery phase editor for a published event with an open time and no start time
- **THEN** the screen says the open and start times must be set first, links to the concert editor, and saving is not offered
