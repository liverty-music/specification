# List Pending

## Purpose

Concerts discovered by the search pipeline are staged for human review before
they become fan-visible. Discovery resolves the venue and writes a `pending`
staged concert instead of publishing directly; a developer approves (publishing
the concert and notifying followers) or rejects (dropping it and appending to an
analysis-only log). This gates AI-sourced data quality while keeping rejection
non-permanent and re-discovery idempotent.

## Requirements

### Requirement: Admin-scoped moderation RPCs

The system SHALL expose a `ConcertModerationService` whose RPCs are authorized only for the admin
org, consistent with the admin console authentication boundary. The service SHALL provide
operations to list pending concerts, approve a pending concert, and reject a pending concert with
a reason.

#### Scenario: Admin lists pending concerts

- **WHEN** an authenticated admin-org caller invokes `ListPendingConcerts`
- **THEN** the response SHALL contain each pending concert's staged id, performing artist, title,
  local date, start time, open time, raw `listed_venue_name`, resolved venue (name, admin_area,
  place id), source URL, and discovered-time timestamp

#### Scenario: Non-admin caller is denied

- **WHEN** a caller outside the admin org invokes any `ConcertModerationService` RPC
- **THEN** the call SHALL be rejected with a permission error and SHALL NOT mutate state

#### Scenario: Approve and reject act on the identified staged concert

- **WHEN** an admin invokes `ApproveConcert` or `RejectConcert` with a staged concert id
- **THEN** the system SHALL apply the corresponding approval or rejection behavior to that staged
  concert
