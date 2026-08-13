## Purpose

The organizer-facing API surface: a dedicated Connect server at
`api.organizer.{base}` serving `OrganizerService.Get`, isolated from the
consumer and admin servers, with org-scoped role-claim authorization so an
operator can read only their own Organizer.

## ADDED Requirements

### Requirement: Dedicated organizer Connect server isolated by audience

The system SHALL serve the organizer-facing `OrganizerService` on a
dedicated Connect server at `api.organizer.{base-domain}` with its own CORS
allowlist (only the `organizer.{base-domain}` origin), TLS cert, Cloud DNS,
and health check. The consumer and admin servers SHALL NOT serve organizer
services, and this server SHALL NOT serve consumer or admin services.

#### Scenario: Organizer server is reachable and isolated

- **WHEN** the organizer console calls `api.organizer.{base-domain}`
- **THEN** the request SHALL be served by the dedicated organizer server
- **AND** the same organizer service SHALL NOT be reachable on the consumer
  or admin API hosts

#### Scenario: CORS admits only the organizer origin

- **WHEN** a browser request to the organizer API originates from the
  `organizer.{base-domain}` origin
- **THEN** CORS SHALL permit it
- **AND** requests from other origins SHALL be rejected by CORS

### Requirement: OrganizerService.Get returns the caller's own organizer

The system SHALL expose a bare-verb `Get` returning the authenticated
Organizer's identity (id, name) and associated artists. The request SHALL
carry an `OrganizerId` that MUST equal the tenant derived from the token; a
mismatch SHALL be rejected.

#### Scenario: Operator reads their own organizer

- **WHEN** an operator calls `Get` with their own OrganizerId
- **THEN** the system SHALL return that Organizer's id, name, and associated
  artists

#### Scenario: Operator cannot read a different organizer

- **WHEN** an operator calls `Get` with an OrganizerId other than their
  token's tenant
- **THEN** the system SHALL reject it with a permission-denied error

### Requirement: Org-scoped authorization from the role claim

The system SHALL authorize organizer requests from the token: it SHALL
validate the JWT, require the organizer-console project id in the token
`aud`, and read the roles claim (`role → { orgId → domain }`) where the inner
orgId is the tenant. It SHALL authorize the request against `{tenant, role}`
and resolve the active tenant from the session's login-scope org. All
authorization failures SHALL return `PERMISSION_DENIED` (never a server
error); an absent/invalid token SHALL return `UNAUTHENTICATED`.

#### Scenario: Missing or empty roles claim is denied

- **WHEN** a request's token carries no `organizer-console` role for the
  target tenant
- **THEN** the system SHALL reject it with `PERMISSION_DENIED`

#### Scenario: Token audience without the project id is denied

- **WHEN** a request's token `aud` does not include the organizer-console
  project id
- **THEN** the system SHALL reject it with `PERMISSION_DENIED`

#### Scenario: Login-scope org and requested organizer must match

- **WHEN** the session's login-scope org does not map to the requested
  Organizer
- **THEN** the system SHALL reject it with `PERMISSION_DENIED`

#### Scenario: Unauthenticated request is rejected

- **WHEN** a request has no valid token
- **THEN** the system SHALL reject it with `UNAUTHENTICATED`
