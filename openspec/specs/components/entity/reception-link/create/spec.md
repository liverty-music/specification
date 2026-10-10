# components/entity/reception-link/create Specification

## Purpose
Stores a new ReceptionLink for an event.

## Requirements

### Requirement: Create stores a new numbered link

Create SHALL store a new Unused ReceptionLink for the given event with the next number of that event and return it with its token. Choosing the number and storing the link SHALL be one indivisible step, so that links created for the same event at the same time get different numbers.

#### Scenario: New link stored

- **WHEN** a link is created for an event whose links are 1 and 2
- **THEN** an Unused link 3 is stored and returned with its token

#### Scenario: Two links created at once

- **WHEN** two links are created for an event without links at the same time
- **THEN** one is stored as 1 and the other as 2
