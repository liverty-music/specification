# Event.IsEventPublished

## Purpose

Tells whether an Event exists and belongs to a first-party Series that is PUBLISHED, which is what a lottery sale on the Event requires.

## Requirements

### Requirement: Published only when the series is PUBLISHED

IsEventPublished SHALL report true when the Event's Series is a first-party Series in the PUBLISHED state, and false when the Series is DRAFT or CANCELLED or is a discovered Series, which has no publish state. It SHALL fail with NotFound when no Event has the id, and with InvalidArgument when no id is given.

#### Scenario: Published organizer concert

- **WHEN** the Event belongs to a PUBLISHED first-party Series
- **THEN** it reports true

#### Scenario: Draft series

- **WHEN** the Event belongs to a DRAFT Series
- **THEN** it reports false

#### Scenario: Discovered concert

- **WHEN** the Event belongs to a Series found by discovery
- **THEN** it reports false

#### Scenario: Unknown event

- **WHEN** no Event has the id
- **THEN** it fails with NotFound
