# Spec Delta

## Purpose

Stores a new Scanner for an event, numbered after the event's earlier Scanners.

## ADDED Requirements

### Requirement: Create stores a new numbered scanner

Create SHALL store a new Unused Scanner for the given event with the next number of that event and return it with its link token. Choosing the number and storing the Scanner SHALL be one indivisible step, so that Scanners created for the same event at the same time get different numbers.

#### Scenario: New scanner stored

- **WHEN** a Scanner is created for an event whose Scanners are 1 and 2
- **THEN** an Unused Scanner 3 is stored and returned with its link token

#### Scenario: Two scanners created at once

- **WHEN** two Scanners are created for an event without Scanners at the same time
- **THEN** one is stored as 1 and the other as 2
