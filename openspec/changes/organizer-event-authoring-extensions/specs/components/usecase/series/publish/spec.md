## ADDED Requirements

### Requirement: Scheduled publish

The system SHALL let an organizer schedule a draft to publish at a future
time; the concert SHALL become `PUBLISHED` (and emit `CONCERT.created`) at
that time, not before.

#### Scenario: Draft publishes at the scheduled time

- **WHEN** an organizer schedules a draft to publish at a future time
- **THEN** the concert SHALL remain `DRAFT` until that time and publish
  automatically when it arrives
