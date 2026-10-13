# Spec Delta

## ADDED Requirements

### Requirement: Publish state is derived from the events

A first-party Series SHALL have no publish state of its own. Its publish state SHALL be derived from its Events: PUBLISHED when at least one Event is PUBLISHED; CANCELLED when no Event is PUBLISHED and at least one is CANCELLED; DRAFT when every Event is DRAFT. A discovered Series SHALL have no publish state.

#### Scenario: Published tour with a draft date
- **WHEN** a first-party Series has two PUBLISHED Events and one DRAFT Event
- **THEN** its publish state is PUBLISHED

#### Scenario: One date cancelled
- **WHEN** a first-party Series has one PUBLISHED Event and one CANCELLED Event
- **THEN** its publish state is PUBLISHED

#### Scenario: Every published date cancelled
- **WHEN** a first-party Series has two CANCELLED Events and one DRAFT Event
- **THEN** its publish state is CANCELLED

#### Scenario: Only drafts
- **WHEN** every Event of a first-party Series is DRAFT
- **THEN** its publish state is DRAFT

#### Scenario: Discovered series has no publish state
- **WHEN** a Series has no organizer
- **THEN** it has no publish state

### Requirement: What can change after publish

While every Event of a first-party Series is DRAFT, all of its authored attributes and its performers SHALL be changeable. Once the Series has a PUBLISHED or CANCELLED Event, its title, description, cover image and performers SHALL remain changeable, and its type, source page and visibility SHALL NOT change.

#### Scenario: Title corrected after publish
- **WHEN** a Series has a PUBLISHED Event
- **THEN** its title, description, cover image and performers can change

#### Scenario: Visibility fixed after publish
- **WHEN** a Series has a PUBLISHED Event
- **THEN** its type, source page and visibility cannot change

#### Scenario: Draft series is fully editable
- **WHEN** every Event of a Series is DRAFT
- **THEN** its type, visibility and performers can change

## MODIFIED Requirements

### Requirement: Which series' events have an event page

An Event of a Series SHALL have an event page exactly when the Series is first-party, its visibility is PUBLIC, and the Event is PUBLISHED or CANCELLED. A Series SHALL have an event page when at least one of its Events has one. An Event of a discovered Series, a DRAFT Event and an Event of an UNLISTED Series SHALL have no event page. Unlike public visibility, a CANCELLED Event keeps its event page, so a shared link still explains that the concert is 中止 (cancelled).

#### Scenario: Published public series

- **WHEN** an Event of a first-party Series with visibility PUBLIC is PUBLISHED
- **THEN** the Event has an event page

#### Scenario: Cancelled public series

- **WHEN** an Event of a first-party Series with visibility PUBLIC is CANCELLED
- **THEN** the Event has an event page, while it is not publicly visible

#### Scenario: Unlisted series

- **WHEN** an Event of a first-party Series with visibility UNLISTED is PUBLISHED
- **THEN** the Event has no event page

#### Scenario: Draft series

- **WHEN** an Event of a first-party Series is DRAFT, even while another Event of the Series is PUBLISHED
- **THEN** the DRAFT Event has no event page

#### Scenario: Discovered series

- **WHEN** a Series has no organizer
- **THEN** its Events have no event page

## REMOVED Requirements

### Requirement: Public visibility

**Reason**: Visibility is decided per Event, because one date of a Series can be a draft or cancelled while the others are published.
**Migration**: Moved to the Event spec, requirement "Public visibility". The Concert's fan visibility now follows the Event.

### Requirement: A draft series has no catalog events

**Reason**: Drafts are no longer a separate kind of performance; a draft is an Event in the DRAFT state.
**Migration**: The Event spec's identity requirement states that a DRAFT Event holds no slot and claims no discovered Event; the Concert spec states that a DRAFT Event is not a Concert.

### Requirement: Cancelled is terminal

**Reason**: The Series no longer has a stored publish state; cancellation happens per Event.
**Migration**: The Event spec's "Publish state of an event" makes CANCELLED terminal for an Event. A Series whose Events are all cancelled has the derived state CANCELLED.
