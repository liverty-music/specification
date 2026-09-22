# Create Draft

## Purpose

Lets a vetted organizer author and publish first-party concert event pages
for the artists it represents, as informational pages that supersede
scraped data and take those artists out of the discovery pipeline.

## Requirements

### Requirement: Organizer authors a concert as a draft

The system SHALL let an authenticated organizer operator create a concert —
a `Series` (title, type, `description`, an optional image exposed as a `media`
object — see "Organizer uploads an image") with one or
more `Event`s (venue, local date, open/start time) and an artist lineup —
scoped to artists the organizer represents. Times are recorded at the
**`Event` (performance) level**; a multi-showtime day (e.g. 昼の部/夜の部)
is modeled as multiple `Event`s under one `Series`. A newly created concert
SHALL be `DRAFT` and SHALL NOT appear in any public list or notification
until published. Creation SHALL validate that a title and each event's date
are present, that open time (when given) is not after start time, and that
the date is not in the past.

#### Scenario: Create a draft concert for a represented artist

- **WHEN** an organizer operator creates a concert naming an artist the
  organizer represents
- **THEN** the system SHALL persist it as `DRAFT` owned by that organizer
- **AND** the concert SHALL NOT appear in discovery, follower lists, or
  notifications

#### Scenario: Multi-showtime day is multiple events

- **WHEN** an organizer authors two showtimes on the same date at the same
  venue
- **THEN** the system SHALL persist two `Event`s (distinct start times)
  under one `Series`

#### Scenario: Cannot author for an unrepresented artist

- **WHEN** an organizer operator creates a concert naming an artist the
  organizer does not represent
- **THEN** the system SHALL reject it with a permission-denied error

#### Scenario: Venue is resolved to the shared venue entity

- **WHEN** a concert is authored with a venue name/address
- **THEN** the system SHALL resolve it to an existing `Venue` (or create
  one) via the shared Places get-or-create path, not a free-text duplicate
