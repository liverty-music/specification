# Admin Concert RPC

## Purpose

The admin-facing concert service boundary: who may list, review and delete concerts from the admin console, and what the boundary passes to ConcertUseCase for a review.

## Requirements

### Requirement: Only admins reach the admin concert calls

List, ListPending, Approve, Reject and Delete SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied. Both checks come before any usecase runs, so a rejected call changes nothing.

#### Scenario: Admin lists pending concerts

- **WHEN** a signed-in admin calls ListPending
- **THEN** ConcertUseCase.ListPending runs and the pending concerts are returned

#### Scenario: Non-admin approves

- **WHEN** a signed-in caller without the admin role calls Approve
- **THEN** the call fails with PermissionDenied and the StagedConcert is unchanged

### Requirement: Reviews carry the reviewer

Approve SHALL pass the StagedConcert id, the requested resolution — keep the existing Event, adopt the staged one, or none — and the caller's identity as reviewer to ConcertUseCase.Approve, and SHALL return the duplicate conflict the usecase reports, if any. Reject SHALL pass the StagedConcert id, the reason and the caller's identity as reviewer to ConcertUseCase.Reject.

#### Scenario: Approve without a resolution

- **WHEN** an admin approves a StagedConcert that collides with an existing Event without giving a resolution
- **THEN** the response carries the duplicate conflict and nothing is published

#### Scenario: Reject records the reviewer

- **WHEN** an admin rejects a StagedConcert with a reason
- **THEN** the rejection is recorded with that reason and that admin as reviewer

### Requirement: Admin concert requests are validated at the boundary

Approve and Reject SHALL fail with InvalidArgument when no StagedConcert id is given; Reject SHALL fail with InvalidArgument when the reason is empty; Delete SHALL fail with InvalidArgument when no event id is given.

#### Scenario: Reject without a reason

- **WHEN** an admin calls Reject with an empty reason
- **THEN** it fails with InvalidArgument and nothing is rejected
