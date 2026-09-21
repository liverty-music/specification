# Get

## Purpose

The organizer-facing API surface: a dedicated Connect server at
`api.organizer.{base}` serving `OrganizerService.Get` and
`OrganizerService.ListArtists`, isolated from the fan and admin servers,
with org-scoped role-claim authorization so an operator can read only their own
Organizer and the artists it represents.

## Requirements

### Requirement: OrganizerService.Get returns the caller's own organizer

The system SHALL expose a bare-verb `Get` returning the caller's own
Organizer's identity (id, name), resolved from the authenticated token (the
Zitadel org it is scoped to) — NOT from a client-supplied id. `GetRequest`
carries no fields: the organizer console holds no `OrganizerId` before this
call, so `Get` is the sanctioned bootstrap that yields it, mirroring the fan
`UserService.Create` resolve-from-token exception. The roster of represented
artists is returned by a separate `ListArtists` RPC, not embedded in the `Get`
response.

#### Scenario: Operator reads their own organizer

- **WHEN** an authenticated operator calls `Get`
- **THEN** the system SHALL resolve their Organizer from the token and return
  its id and name
