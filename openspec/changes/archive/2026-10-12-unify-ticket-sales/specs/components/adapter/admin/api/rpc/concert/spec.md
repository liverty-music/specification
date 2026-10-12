# Spec Delta

## ADDED Requirements

### Requirement: Only admins list and delete concerts

List and Delete SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied. Both checks come before any usecase runs, so a rejected call changes nothing.

#### Scenario: Admin lists concerts

- **WHEN** a signed-in admin calls List
- **THEN** the concerts are returned with their series and artists

#### Scenario: Non-admin deletes

- **WHEN** a signed-in caller without the admin role calls Delete
- **THEN** the call fails with PermissionDenied and the Concert is unchanged

### Requirement: Delete names an event

Delete SHALL fail with InvalidArgument when no event id is given.

#### Scenario: Delete without an event

- **WHEN** an admin calls Delete without an event id
- **THEN** it fails with InvalidArgument and nothing is deleted

## REMOVED Requirements

### Requirement: Only admins reach the admin concert calls
**Reason**: The review calls act on a ConcertCandidate, not a Concert, so `ListPending`, `Approve` and `Reject` move from the admin ConcertService to the admin ConcertCandidateService (`List`, `Approve`, `Reject`) under the RPC naming rule. The admin ConcertService keeps List and Delete.
**Migration**: The role gate for List and Delete continues in "Only admins list and delete concerts" above; the gate for the review calls, with the scenarios "Admin lists pending concerts" and "Non-admin approves", continues in `components/adapter/admin/api/rpc/concert-candidate`.

### Requirement: Reviews carry the reviewer
**Reason**: Approve and Reject move from the admin ConcertService to the admin ConcertCandidateService under the RPC naming rule.
**Migration**: The behavior continues unchanged in `components/adapter/admin/api/rpc/concert-candidate`; the admin console calls `ConcertCandidateService.Approve` and `ConcertCandidateService.Reject`.

### Requirement: Admin concert requests are validated at the boundary
**Reason**: The Approve and Reject checks move with those calls to the admin ConcertCandidateService.
**Migration**: The Approve and Reject checks continue in `components/adapter/admin/api/rpc/concert-candidate`; the Delete check continues in "Delete names an event" above.
