# Spec Delta

## ADDED Requirements

### Requirement: Published only when the event is PUBLISHED

IsEventPublished SHALL report true when the Event's own publish state is PUBLISHED, and false when the Event is DRAFT or CANCELLED or belongs to a discovered Series, which gives it no publish state. The publish state of the Event's other dates SHALL play no part. It SHALL fail with NotFound when no Event has the id, and with InvalidArgument when no id is given.

#### Scenario: Published organizer event

- **WHEN** the Event is PUBLISHED
- **THEN** it reports true

#### Scenario: Draft date of a published series

- **WHEN** the Event is DRAFT and another Event of its Series is PUBLISHED
- **THEN** it reports false

#### Scenario: Cancelled date of a published series

- **WHEN** the Event is CANCELLED and another Event of its Series is PUBLISHED
- **THEN** it reports false

#### Scenario: Discovered event

- **WHEN** the Event belongs to a Series found by discovery
- **THEN** it reports false

#### Scenario: Unknown event id

- **WHEN** no Event has the id
- **THEN** it fails with NotFound

## REMOVED Requirements

### Requirement: Published only when the series is PUBLISHED

**Reason**: The Series no longer has a stored publish state; each Event has its own.
**Migration**: Replaced by "Published only when the event is PUBLISHED" above. Callers (lottery and ticket sales, reception links) keep calling IsEventPublished and now get the answer for the one Event.
