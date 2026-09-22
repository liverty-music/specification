# Approved Concerts

## Purpose

TBD - created by archiving change admin-console-concert-management. Update Purpose after archive.

## Requirements

### Requirement: Admin console presents approved concerts grouped by artist and series

The admin console SHALL present the published concerts returned by `List` grouped
first by performing artist and then by series, computed client-side from the flat
`List` result. Each series SHALL be a collapsed disclosure that expands to its
individual events; the collapsed view SHALL summarise the series (event count and
date range) so the catalog stays scannable without expanding every series. Each
expanded event SHALL show its local date, start time, open time, and venue, with a
per-event manual delete control. Event columns SHALL align across all series and
artists. Triggering delete SHALL open a modal confirmation; the `Delete` RPC SHALL
be issued only after the operator confirms.

#### Scenario: Concerts shown grouped by artist then series

- **WHEN** an operator opens the approved-concerts screen
- **THEN** the published concerts SHALL be displayed grouped by performing artist
- **AND** within each artist they SHALL be grouped into collapsible series
- **AND** each collapsed series SHALL show its event count and date range

#### Scenario: Expanding a series reveals its events

- **WHEN** an operator expands a series
- **THEN** its individual events SHALL be listed with local date, start time, open
  time, and venue
- **AND** each event SHALL expose a manual delete control

#### Scenario: Delete requires confirmation in a modal dialog

- **WHEN** an operator activates an event's delete control
- **THEN** a modal confirmation dialog SHALL open identifying the target concert
- **AND** the dialog's confirm control SHALL receive initial focus so it can be
  confirmed with the Enter key, and dismissed (without deleting) with Escape
- **AND** the `Delete` RPC SHALL be issued only after the operator confirms
