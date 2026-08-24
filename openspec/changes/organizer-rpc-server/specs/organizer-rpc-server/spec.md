## Purpose

The organizer-facing API surface: a dedicated Connect server at
`api.organizer.{base}` serving `OrganizerService.Get` and
`OrganizerService.ListArtists`, isolated from the fan and admin servers,
with org-scoped role-claim authorization so an operator can read only their own
Organizer and the artists it represents.

## ADDED Requirements

### Requirement: Dedicated organizer Connect server isolated by audience

The system SHALL serve the organizer-facing `OrganizerService` on a
dedicated Connect server at `api.organizer.{base-domain}` with its own CORS
allowlist (only the `organizer.{base-domain}` origin), TLS cert, Cloud DNS,
and health check. The fan and admin servers SHALL NOT serve organizer
services, and this server SHALL NOT serve fan or admin services.

#### Scenario: Organizer server is reachable and isolated

- **WHEN** the organizer console calls `api.organizer.{base-domain}`
- **THEN** the request SHALL be served by the dedicated organizer server
- **AND** the same organizer service SHALL NOT be reachable on the fan
  or admin API hosts

#### Scenario: CORS admits only the organizer origin

- **WHEN** a browser request to the organizer API originates from the
  `organizer.{base-domain}` origin
- **THEN** CORS SHALL permit it
- **AND** requests from other origins SHALL be rejected by CORS

### Requirement: OrganizerService.Get returns the caller's own organizer

The system SHALL expose a bare-verb `Get` returning the caller's own
Organizer's identity (id, name). The request SHALL carry an `OrganizerId` that
MUST resolve to the caller's own Organizer — the Organizer whose
`zitadel_org_id` equals the Zitadel org the token is scoped to; any other
`OrganizerId` SHALL be rejected. The roster of represented artists is returned
by a separate `ListArtists` RPC, not embedded in the `Get` response —
consistent with the admin `OrganizerService` and the fan `UserService.Get`.

#### Scenario: Operator reads their own organizer

- **WHEN** an operator calls `Get` with the `OrganizerId` of their own
  Organizer
- **THEN** the system SHALL return that Organizer's id and name

#### Scenario: Operator cannot read a different organizer

- **WHEN** an operator calls `Get` with an `OrganizerId` that does not resolve
  to their own Organizer
- **THEN** the system SHALL reject it with a permission-denied error

### Requirement: OrganizerService.ListArtists returns the caller's roster

The system SHALL expose a bare-verb `ListArtists` returning the artists the
caller's own Organizer represents. The request SHALL carry an `OrganizerId`
that MUST resolve to the caller's own Organizer (as defined for `Get`); any
other `OrganizerId` SHALL be rejected. The response SHALL be empty when the
Organizer represents no artists. The artists SHALL be returned in a stable
order, ascending by artist id — a UUID v7, so effectively artist-creation order
— giving a deterministic, unique ordering a later pagination phase can page
over. (This orders by when the artist was created, not when it was added to the
roster; a roster-add ordinal is a future concern.)

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

### Requirement: Org-scoped authorization from the role claim

The system SHALL authorize organizer requests from the token. It SHALL
validate the JWT, require the organizer-console project id in the token `aud`,
and read the roles claim (`role → { orgId → domain }`, where each `orgId` is a
Zitadel org id). The caller's Zitadel org SHALL be the org id that appears
BOTH in the session's login-scope scope (`urn:zitadel:iam:org:id:<orgId>`) AND
as an `orgId` under which the operator holds a role. A request SHALL be
authorized only when the requested `OrganizerId` resolves (via `zitadel_org_id`)
to that same Zitadel org and that Organizer is active; holding any role for the
org is sufficient (the top role is `owner`; no specific role is required in
this phase).

All authorization failures SHALL return `PERMISSION_DENIED`, SHALL NOT execute
handler business logic, and SHALL NOT reveal whether the requested Organizer
exists or is active. An absent or invalid token SHALL return `UNAUTHENTICATED`.
A missing or malformed `OrganizerId` SHALL return `INVALID_ARGUMENT` via
protovalidate.

#### Scenario: Missing or empty roles claim is denied

- **WHEN** a request's token carries no role for the caller's Zitadel org
- **THEN** the system SHALL reject it with `PERMISSION_DENIED`

#### Scenario: Token audience without the project id is denied

- **WHEN** a request's token `aud` does not include the organizer-console
  project id
- **THEN** the system SHALL reject it with `PERMISSION_DENIED`

#### Scenario: Login-scope org and role-claim org must agree

- **WHEN** the login-scope org id and the `orgId` under which the operator
  holds a role are not the same Zitadel org
- **THEN** the system SHALL reject it with `PERMISSION_DENIED`

#### Scenario: Deactivated organizer is denied

- **WHEN** the Organizer resolved for the caller's Zitadel org is deactivated
- **THEN** the system SHALL reject the request with `PERMISSION_DENIED`
- **AND** the response SHALL NOT reveal that the Organizer is deactivated

#### Scenario: Caller's Zitadel org has no linked Organizer

- **WHEN** no active Organizer has a `zitadel_org_id` matching the caller's
  Zitadel org (e.g. the link is not yet established)
- **THEN** the system SHALL reject the request with `PERMISSION_DENIED`
- **AND** the response SHALL NOT reveal whether an Organizer exists

#### Scenario: Missing or malformed OrganizerId is rejected

- **WHEN** a request omits `OrganizerId` or supplies a malformed value
- **THEN** the system SHALL reject it with `INVALID_ARGUMENT` via protovalidate

#### Scenario: Unauthenticated request is rejected

- **WHEN** a request has no valid token
- **THEN** the system SHALL reject it with `UNAUTHENTICATED`
