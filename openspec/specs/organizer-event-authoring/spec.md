# organizer-event-authoring Specification

## Purpose

Lets a vetted organizer author and publish first-party concert event pages
for the artists it represents, as informational pages that supersede
scraped data and take those artists out of the discovery pipeline.

## Requirements

### Requirement: Organizer authors a concert as a draft

The system SHALL let an authenticated organizer operator create a concert —
a `Series` (title, type, `description`, optional `cover_image`) with one or
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

### Requirement: Publish makes a concert live, first-party, and notifies once

The system SHALL let the owning organizer publish a `DRAFT` concert. On
publish a `PUBLIC` concert becomes `PUBLISHED` and the system SHALL emit
**one `CONCERT.created` per series**, carrying the ids of the events being
published (consistent with the series-grouped publish-once model), which
drives the existing follower notification. `DRAFT` and `UNLISTED` concerts
SHALL NOT emit `CONCERT.created`. A concert first published as `UNLISTED`
and later changed to `PUBLIC` SHALL emit `CONCERT.created` at that **first
transition to `PUBLIC`**, idempotently — never more than once for the same
events (subsequent visibility toggles do not re-notify). Only the owning
organizer may publish.

#### Scenario: Unlisted later made public notifies exactly once

- **WHEN** an `UNLISTED` published concert is changed to `PUBLIC`
- **THEN** the system SHALL emit `CONCERT.created` once at that transition
- **AND** SHALL NOT emit it again for the same events on any later toggle

#### Scenario: Public publish notifies once per series

- **WHEN** the owning organizer publishes a `PUBLIC` series with one or more
  events
- **THEN** the series SHALL become `PUBLISHED` and emit exactly one
  `CONCERT.created` carrying those events' ids

#### Scenario: Adding a new event to a published series notifies once for it

- **WHEN** the owning organizer publishes an additional event under an
  already-`PUBLISHED` series
- **THEN** the system SHALL emit one `CONCERT.created` for the series
  carrying only the new event id(s), and SHALL NOT re-announce the
  previously-published events

#### Scenario: Unlisted or draft never notifies

- **WHEN** a concert is saved as `DRAFT` or published as `UNLISTED`
- **THEN** the system SHALL NOT emit `CONCERT.created` and followers SHALL
  NOT be notified

#### Scenario: Only the owning organizer may publish

- **WHEN** an operator of a different organizer attempts to publish the
  concert
- **THEN** the system SHALL reject it with a permission-denied error

### Requirement: First-party publish supersedes scraped data without harm

Organizer-authored events insert under the organizer's own `series_id`
(resolved via the shared series-resolution path), converging on the event
natural key `(venue, local_date, start)`. On publishing a `PUBLIC` concert
whose slot matches existing data, the first-party record SHALL become
authoritative:

- A matching pending `staged_concert` SHALL be dropped.
- A matching **already-published discovered event** SHALL be **claimed** —
  the event is re-pointed to the organizer's series and marked
  organizer-owned, keeping its event id so user references (e.g. ticket
  journeys) are preserved; `CONCERT.created` SHALL NOT be re-emitted for an
  event that was already announced.
- A matching **suppressed** slot SHALL NOT be silently resurrected;
  publishing into a suppressed slot SHALL require an explicit, logged
  organizer action.
- A slot already owned by a **different organizer's** first-party series
  SHALL be treated as a conflict routed to admin reconciliation, NOT an
  automatic ownership overwrite.

#### Scenario: Supersede a pending staged concert

- **WHEN** publish matches a `staged_concert` at the same slot
- **THEN** the staged row SHALL be dropped and the first-party concert
  published

#### Scenario: Claim an already-published discovered event

- **WHEN** publish matches an already-published discovered event at the same
  slot
- **THEN** the system SHALL re-point that event to the organizer's series,
  keep its id, mark it organizer-owned, and SHALL NOT re-emit
  `CONCERT.created`

#### Scenario: Suppressed slot is not silently resurrected

- **WHEN** publish targets a slot in the suppression set
- **THEN** the system SHALL NOT auto-publish it and SHALL require an explicit
  organizer action to proceed

#### Scenario: Cross-organizer slot is a conflict, not a takeover

- **WHEN** publish matches a slot already owned by a different organizer's
  first-party series
- **THEN** the system SHALL route it to admin reconciliation and SHALL NOT
  reassign ownership automatically

### Requirement: Represented artists are excluded from scraping

While an artist is associated with an organizer, the system SHALL exclude
that artist from concert-search scraping (first-party is authoritative). The
exclusion SHALL be keyed on the **Organizer↔Artist association**, not on the
existence of a published concert: associating an artist starts the
exclusion, and disassociating it (or deactivating the organizer) resumes
scraping.

#### Scenario: Associated artist is excluded from discovery scraping

- **WHEN** the discovery pipeline runs for an artist associated with an
  active organizer
- **THEN** the system SHALL skip scraping that artist's concerts

#### Scenario: Disassociation resumes scraping

- **WHEN** an artist is disassociated from its organizer (or the organizer
  is deactivated)
- **THEN** the system SHALL resume scraping that artist's concerts

### Requirement: Visibility controls where a published concert appears

A published concert SHALL have a visibility of `PUBLIC` or `UNLISTED`.
`PUBLIC` concerts appear in normal discovery and follower lists. `UNLISTED`
concerts SHALL be excluded from discovery, follower lists, and notifications,
and SHALL carry a regenerable signed token (the owning organizer can
regenerate it). The fan-facing read path that resolves that token to view an
`UNLISTED` concert (a public `GetUnlisted` RPC + route) is a follow-up and is
NOT part of this change's MVP.

#### Scenario: Public concert appears in discovery

- **WHEN** a `PUBLIC` concert is published
- **THEN** it SHALL appear in discovery and to followers per existing rules

#### Scenario: Unlisted concert is excluded from fan-facing surfaces

- **WHEN** an `UNLISTED` concert is published
- **THEN** it SHALL NOT appear in discovery, lists, or notifications
- **AND** its signed token SHALL be stored and regenerable by the owning
  organizer (the token-resolving public read path ships in a follow-up)

### Requirement: Organizer uploads a cover image

The system SHALL let the organizer attach a single cover image to a concert,
stored in object storage and served via a stable URL, validating image type
and size server-side. A concert MAY be published without a cover image.

#### Scenario: Cover image is stored and served

- **WHEN** an organizer uploads a valid cover image for a draft concert
- **THEN** the system SHALL store it and serve it via a stable URL on the
  concert

#### Scenario: Invalid image is rejected

- **WHEN** an organizer uploads a file exceeding the size limit or of an
  unsupported type
- **THEN** the system SHALL reject it with an invalid-argument error
