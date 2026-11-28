# Spec Delta

## Purpose

Counts the Admissions of one Event, the record of whether anyone entered it.

## ADDED Requirements

### Requirement: Admissions of an event counted

CountByEvent SHALL return how many Admissions the given Event has. It SHALL return 0 when it has none or no Event has the id.

#### Scenario: Concert attended
- **WHEN** 120 Tickets of an Event were admitted
- **THEN** CountByEvent returns 120

#### Scenario: Nobody entered
- **WHEN** no Ticket of the Event was admitted
- **THEN** CountByEvent returns 0
