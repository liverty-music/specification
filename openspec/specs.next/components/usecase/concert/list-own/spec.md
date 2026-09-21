# List Own

## Purpose

Lets a vetted organizer author and publish first-party concert event pages
for the artists it represents, as informational pages that supersede
scraped data and take those artists out of the discovery pipeline.

## Requirements

### Requirement: Organizer lists and edits its own concerts

The system SHALL let an organizer operator list the concerts its organizer
owns (both `DRAFT` and `PUBLISHED`) and edit them. A `DRAFT` is fully
editable. A `PUBLISHED` concert MAY be edited for corrections (e.g. time,
venue, description) and MAY be **cancelled**; a cancelled concert SHALL stop
appearing to fans and SHALL be marked cancelled rather than silently
deleted. Cancellation SHALL emit a cancellation signal (`CONCERT.cancelled`)
so downstream consumers and fan caches drop it. `CANCELLED` is **terminal**:
to run the concert again the organizer authors a new concert (no
un-cancel/re-publish of a cancelled one).

#### Scenario: Organizer sees its own drafts and published concerts

- **WHEN** an organizer operator lists concerts
- **THEN** the system SHALL return only concerts owned by that organizer,
  including drafts

#### Scenario: Correcting a published concert

- **WHEN** the owning organizer edits a published concert's time or venue
- **THEN** the change SHALL be reflected on the public page without
  re-emitting a new-concert notification

#### Scenario: Cancelling a published concert

- **WHEN** the owning organizer cancels a published concert
- **THEN** the concert SHALL be marked cancelled and SHALL stop appearing in
  discovery and follower lists
- **AND** the system SHALL emit `CONCERT.cancelled` so consumers/caches drop
  it

#### Scenario: Cancelled is terminal

- **WHEN** an organizer wants to run a cancelled concert again
- **THEN** the system SHALL require authoring a new concert (a `CANCELLED`
  concert SHALL NOT be re-published)
