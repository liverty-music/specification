# List

## Purpose

TBD - created by archiving change admin-console-concert-management. Update Purpose after archive.

## Requirements

### Requirement: Admin lists every published concert

The admin `ConcertService` SHALL provide a `List` operation that returns every
published concert, with no follower, proximity, or personalization filtering, so an
operator can review the full published catalog. Each returned concert SHALL carry
the identifiers required for follow-up actions (the published event id, the
performing artist, and human-readable date/venue/title fields). `List` SHALL NOT
return concerts that are still pending review (those are returned by `ListPending`).

#### Scenario: List returns all published concerts

- **WHEN** an admin calls `List`
- **THEN** every published concert SHALL be returned regardless of any follow or
  proximity relationship
- **AND** each entry SHALL include its published event id and performing artist

#### Scenario: Pending concerts are excluded from List

- **WHEN** concerts exist in both the published catalog and the pending review queue
- **THEN** `List` SHALL return only the published concerts
- **AND** the pending concerts SHALL be returned only by `ListPending`
