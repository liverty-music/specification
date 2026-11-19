# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Searched time is not in the future`
- TO: `### Requirement: Search time is not in the future`

## MODIFIED Requirements

### Requirement: Search time is not in the future

A ticket sale search's search time SHALL NOT be after the current time.

#### Scenario: Future search time
- **WHEN** a ticket sale search carries a search time one hour from now
- **THEN** the ticket sale search is invalid
