# Admin Concert RPC

## Purpose

The admin-facing concert service boundary: who may list and delete concerts from the admin console. Reviewing concert candidates is the admin ConcertCandidateService boundary (`components/adapter/admin/api/rpc/concert-candidate`).

## Requirements

### Requirement: Listed concerts come with their series and artists once

List SHALL return, together with the Concerts, every Series and every Artist those Concerts refer to, once each; a Concert carries only the id of its Series (through its Event) and the ids of its Artists. Every returned Series SHALL carry the same fields as on the fan concert service, and its share token SHALL never be returned.

#### Scenario: Two approved concerts of one series

- **WHEN** an admin lists the concerts and two of them belong to the same Series and share an Artist
- **THEN** the response carries that Series once and that Artist once, and both Concerts refer to them by id

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
