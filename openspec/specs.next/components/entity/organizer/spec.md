# Organizer

## Purpose

The organizer-facing API surface: a dedicated Connect server at
`api.organizer.{base}` serving `OrganizerService.Get` and
`OrganizerService.ListArtists`, isolated from the fan and admin servers,
with org-scoped role-claim authorization so an operator can read only their own
Organizer and the artists it represents.

## Requirements

### Requirement: Org-scoped authorization from the role claim

The system SHALL authorize organizer requests from the token. It SHALL
validate the JWT, require the organizer-console project id in the token `aud`,
and read the roles claim (`role → { orgId → domain }`, where each `orgId` is a
Zitadel org id). The caller's Zitadel org SHALL be the org id that appears BOTH
in the session's login-scope scope (`urn:zitadel:iam:org:id:<orgId>`) — of
which exactly one SHALL be present — AND as an `orgId` under which the operator
holds a role; the two SHALL agree. Holding any role for that org is sufficient
(the top role is `owner`; no specific role is required in this phase). The
system SHALL resolve the caller's Organizer via the `zitadel_org_id` link to
that Zitadel org; for `ListArtists`, the supplied `OrganizerId` MUST equal that
resolved Organizer.

A request against an `active` resolved Organizer SHALL be served. If the
caller's own resolved Organizer is `deactivated`, the system SHALL reject with
`FAILED_PRECONDITION` and MAY state that it is deactivated — this is the
caller's own org, so its state is not concealed. All other authorization
failures — no role for the org, `aud` without the project id, login-scope and
role-claim orgs disagreeing, zero or multiple login-scope orgs, a supplied
`OrganizerId` resolving to a different org, or no Organizer linked to the
caller's Zitadel org — SHALL return `PERMISSION_DENIED`, SHALL NOT execute
handler business logic, and SHALL NOT reveal whether such an Organizer exists.
An absent or invalid token SHALL return `UNAUTHENTICATED`. A missing or
malformed `OrganizerId` on `ListArtists` SHALL return `INVALID_ARGUMENT` via
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

#### Scenario: Absent or ambiguous login-scope org is denied

- **WHEN** the token carries no `urn:zitadel:iam:org:id:<orgId>` scope, or more
  than one
- **THEN** the system SHALL reject it with `PERMISSION_DENIED`

#### Scenario: Deactivated own organizer returns a precondition failure

- **WHEN** the Organizer resolved for the caller's Zitadel org is deactivated
- **THEN** the system SHALL reject the request with `FAILED_PRECONDITION`
- **AND** the response MAY state that the Organizer is deactivated (it is the
  caller's own org, so the state is not concealed)

#### Scenario: Caller's Zitadel org has no linked Organizer

- **WHEN** no Organizer has a `zitadel_org_id` matching the caller's Zitadel
  org (e.g. the link is not yet established)
- **THEN** the system SHALL reject the request with `PERMISSION_DENIED`
- **AND** the response SHALL NOT reveal whether an Organizer exists

#### Scenario: Missing or malformed OrganizerId on ListArtists is rejected

- **WHEN** a `ListArtists` request omits `OrganizerId` or supplies a malformed
  value
- **THEN** the system SHALL reject it with `INVALID_ARGUMENT` via protovalidate

#### Scenario: Unauthenticated request is rejected

- **WHEN** a request has no valid token
- **THEN** the system SHALL reject it with `UNAUTHENTICATED`
