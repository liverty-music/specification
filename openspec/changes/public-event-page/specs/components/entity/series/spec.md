# Spec Delta

## ADDED Requirements

### Requirement: Which series' events have an event page

The Events of a Series SHALL have an event page exactly when the Series is first-party, its visibility is PUBLIC, and its publish state is PUBLISHED or CANCELLED. A discovered Series, a DRAFT Series and an UNLISTED Series SHALL have no event page. Unlike public visibility, a CANCELLED Series keeps its event page, so a shared link still explains that the concert is 中止 (cancelled).

#### Scenario: Published public series

- **WHEN** a first-party Series is PUBLISHED with visibility PUBLIC
- **THEN** its Events have an event page

#### Scenario: Cancelled public series

- **WHEN** a first-party Series with visibility PUBLIC is CANCELLED
- **THEN** its Events have an event page, while the Series is not publicly visible

#### Scenario: Unlisted series

- **WHEN** a first-party Series is PUBLISHED with visibility UNLISTED
- **THEN** its Events have no event page

#### Scenario: Draft series

- **WHEN** a first-party Series is DRAFT
- **THEN** its Events have no event page

#### Scenario: Discovered series

- **WHEN** a Series has no organizer
- **THEN** its Events have no event page
