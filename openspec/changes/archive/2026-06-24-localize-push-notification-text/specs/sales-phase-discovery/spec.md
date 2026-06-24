## MODIFIED Requirements

### Requirement: Event-Driven Announcement on New Phase

The system SHALL push an announcement when a newly discovered sales phase is persisted, reusing the existing discovery→event→push pipeline. This announcement is event-driven and distinct from the time-based reminders. The announcement SHALL be built per recipient and localized to the recipient's `preferred_language` (default `en`), consistent with the `sales-reminders` Notification Content requirement.

#### Scenario: New phase announced

- **WHEN** the discovery job persists a sales phase that did not previously exist
- **THEN** it SHALL publish a sales-phase-discovered event
- **AND** a consumer SHALL push an announcement to the followers of the performers of the phase's covered events, applying the existing hype-level filter

#### Scenario: Re-discovered phase is not re-announced

- **WHEN** the discovery job re-encounters an already-known phase (only updating its fields)
- **THEN** it SHALL NOT publish a new announcement for that phase

#### Scenario: Announcement copy localized per recipient

- **WHEN** the announcement is built for a recipient
- **THEN** its `title` and `body` SHALL be rendered in the recipient's `preferred_language`
- **AND** when the recipient has no `preferred_language` set, the copy SHALL default to `en`
