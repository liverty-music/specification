# Publish

## Purpose

Lets a vetted organizer author and publish first-party concert event pages
for the artists it represents, as informational pages that supersede
scraped data and take those artists out of the discovery pipeline.

## Requirements

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

### Requirement: Publish enforces the complete required-field set

Publish SHALL be the **final server-side gate** on a concert going live: the
system SHALL validate the complete required-field set at publish time and
reject an incomplete concert regardless of how the draft reached its current
state (author, edit, or partial data). Creation validates a subset for an
early-feedback draft, but a draft MAY still be missing later-required data;
publish SHALL re-validate the whole set so no `PUBLISHED` concert is ever
surfaced with a missing required field. The required set is:

- a non-empty **title**;
- **at least one performing artist**;
- **at least one event**, and **every** event SHALL have a **non-empty venue**
  and a **valid local date**.

`description` and `media` remain **optional** and SHALL NOT block publish. On a
failed check the concert SHALL remain `DRAFT` (the state is unchanged, no
`CONCERT.created` is emitted) and the system SHALL reject the request with a
failed-precondition error naming the missing requirement. This gate is
independent of ownership and slot-conflict checks (those still apply).

#### Scenario: Publish rejects a concert missing a required field

- **WHEN** the owning organizer publishes a `DRAFT` concert that has no
  performing artist, or an event with no venue, or is otherwise missing a
  required field
- **THEN** the system SHALL reject the publish with a failed-precondition error
  naming the missing requirement, the concert SHALL remain `DRAFT`, and no
  `CONCERT.created` SHALL be emitted

#### Scenario: Publish succeeds when the required set is complete

- **WHEN** the owning organizer publishes a `DRAFT` concert with a title, at
  least one performer, and at least one event that has a venue and a valid date
- **THEN** the system SHALL publish it (subject to the ownership and
  slot-conflict rules), even when `description` and `media` are absent

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
