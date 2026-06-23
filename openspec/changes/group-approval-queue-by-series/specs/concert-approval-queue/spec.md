## MODIFIED Requirements

### Requirement: Admin console approval-queue UI

The admin console SHALL provide a reviewer screen that lists pending concerts grouped
first by performing artist and then by series title, and offers per-concert approve and
reject (with reason) actions. The screen SHALL live in the bundle-isolated `admin/` app
and SHALL consume the admin `ConcertService`. Grouping SHALL be computed client-side
from the flat `ListPending` result using the `PendingConcert.performer.name` and
`PendingConcert.title` fields as grouping keys (artist and series proxy respectively).

Each series group SHALL be presented as a collapsible disclosure. The collapsed summary
SHALL show the series title, the count of pending concerts in the group, and the count
of concerts with an unresolved venue. Individual concert rows within an expanded group
SHALL retain the full set of reviewable fields (local date, start time, listed venue
name, resolved venue, source URL, discovered timestamp) and their per-row approve and
reject controls. The Artist and Title columns SHALL NOT be repeated inside the group
table; they are conveyed by the group headers.

#### Scenario: Reviewer sees pending concerts grouped by artist and series

- **WHEN** an authenticated developer opens the approval-queue screen
- **THEN** the pending concerts SHALL be displayed grouped first by performing artist
- **AND** within each artist they SHALL be grouped into collapsible series using the
  concert title as the series proxy
- **AND** each collapsed series summary SHALL show the series title, the number of
  pending concerts in the group, and the number with an unresolved venue

#### Scenario: Expanding a series reveals per-concert review rows

- **WHEN** the developer expands a series group
- **THEN** each pending concert in that series SHALL be listed showing local date,
  start time, listed venue name, resolved venue (or unresolved indicator), source
  URL, and discovered timestamp
- **AND** each row SHALL expose Approve and Reject controls

#### Scenario: Reviewer approves an item

- **WHEN** the developer approves a pending concert
- **THEN** the UI SHALL call `Approve` and remove the row from its series group on success
- **AND** if the series group becomes empty it SHALL be removed from the UI

#### Scenario: Reviewer rejects an item with a reason

- **WHEN** the developer rejects a pending concert and provides a reason
- **THEN** the UI SHALL call `Reject` with that reason and remove the row from its
  series group on success
- **AND** if the series group becomes empty it SHALL be removed from the UI
