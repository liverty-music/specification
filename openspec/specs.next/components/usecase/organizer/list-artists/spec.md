# List Artists

## Purpose

The organizer-facing API surface: a dedicated Connect server at
`api.organizer.{base}` serving `OrganizerService.Get` and
`OrganizerService.ListArtists`, isolated from the fan and admin servers,
with org-scoped role-claim authorization so an operator can read only their own
Organizer and the artists it represents.

## Requirements

### Requirement: OrganizerService.ListArtists returns the caller's roster

The system SHALL expose a bare-verb `ListArtists` returning the artists the
caller's own Organizer represents. The request SHALL carry an `OrganizerId`
that MUST resolve to the caller's own Organizer (as defined for `Get`); any
other `OrganizerId` SHALL be rejected. The response SHALL be empty when the
Organizer represents no artists. The artists SHALL be returned in a stable
order, ascending by artist id — a UUID v7, so effectively artist-creation order
— giving a deterministic, unique ordering a later pagination phase can page
over. (This orders by when the artist was created, not when it was added to the
roster; a roster-add ordinal is a future concern.) The roster is unbounded on
the wire; pagination is deferred to a later phase, acceptable because an
Organizer's roster is admin-curated and small.

#### Scenario: Operator lists their own roster

- **WHEN** an operator calls `ListArtists` with the `OrganizerId` of their own
  Organizer
- **THEN** the system SHALL return the artists that Organizer represents,
  ascending by artist id
- **AND** the list SHALL be empty when it represents none

#### Scenario: Roster order is stable across calls

- **WHEN** an operator calls `ListArtists` twice with no change to the roster
- **THEN** the system SHALL return the artists in the same order both times

#### Scenario: Operator cannot list a different organizer's roster

- **WHEN** an operator calls `ListArtists` with an `OrganizerId` that does not
  resolve to their own Organizer
- **THEN** the system SHALL reject it with a permission-denied error
