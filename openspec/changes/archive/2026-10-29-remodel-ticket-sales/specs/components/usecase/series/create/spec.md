# Spec Delta

## ADDED Requirements

### Requirement: Each event's per-account limit

Create SHALL take an optional per-account limit for each event and store it on the Event, with 4 when none is given. It SHALL fail with InvalidArgument, storing nothing, when a given limit breaks the Event's per-account limit rule.

#### Scenario: No limit given
- **WHEN** a draft is created with an event without a per-account limit
- **THEN** the Event's per-account limit is 4

#### Scenario: Limit of 2
- **WHEN** a draft is created with an event whose per-account limit is 2
- **THEN** the Event's per-account limit is 2

#### Scenario: Limit above one admission code
- **WHEN** an event's per-account limit is 11
- **THEN** Create fails with InvalidArgument and nothing is stored
