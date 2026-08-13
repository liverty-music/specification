## Purpose

The organizer (seller) frontend shell: a dedicated `organizer.html` entry,
bundle-isolated from the consumer SPA and admin console, authenticated
against the operator's own Zitadel tenant org via domain discovery, with a
role-claim route guard and a post-login placeholder. Business screens land
in later changes.

## ADDED Requirements

### Requirement: Bundle isolation from the consumer SPA and admin console

The organizer console SHALL be built as a separate Vite/Rollup entry point
(`organizer.html`) such that no organizer-only code is included in any chunk
loaded by the consumer SPA or the admin console. Adding it MUST NOT increase
the consumer SPA's downloaded bundle size or regress its Core Web Vitals.

#### Scenario: Consumer page loads no organizer code

- **WHEN** a fan loads the consumer SPA at the consumer hostname
- **THEN** the consumer entry's chunk graph SHALL contain no module
  originating from the organizer source directory

### Requirement: Authenticate operators via domain discovery, one client for all tenants

The organizer console SHALL authenticate operators through Zitadel OIDC
(PKCE, no client secret) using the shared `organizer-console` client, with
the operator's tenant org resolved by **email domain discovery** — the
operator enters their email and is routed to their own org, with no fixed
org id at build time and no org picker.

#### Scenario: Operator signs in and is routed to their org

- **WHEN** an operator enters their email and completes sign-in
- **THEN** domain discovery SHALL route them to their own Organizer tenant
  org and return them authenticated to the console

#### Scenario: One OIDC client serves all tenants

- **WHEN** operators of different Organizer tenant orgs sign in
- **THEN** the same `organizer-console` OIDC client SHALL serve them all (no
  per-tenant client, no build-time org id)

### Requirement: Route guard admits only master-role operators

The organizer console SHALL guard its routes: unauthenticated visitors are
sent to sign-in, and an authenticated user is admitted only if the token's
`organizer-console` project roles include `master`; otherwise access is
denied. The backend remains the source of truth for authorization; the guard
is a UX gate. On success the operator lands on a post-login welcome
placeholder.

#### Scenario: Unauthenticated visitor is redirected to sign-in

- **WHEN** an unauthenticated visitor navigates to an organizer console route
- **THEN** the guard SHALL redirect them to Zitadel sign-in

#### Scenario: Authenticated operator with master role sees the placeholder

- **WHEN** an authenticated operator whose token carries the `master` role
  loads the console
- **THEN** they SHALL see the post-login welcome placeholder

#### Scenario: Authenticated account without the master role is denied

- **WHEN** an authenticated user whose token lacks the `master` role loads
  the console
- **THEN** the guard SHALL deny access to organizer screens

### Requirement: Organizer runtime config resolves the org at login

The organizer console SHALL load its runtime config from `/config.json`
carrying the Zitadel issuer, the `organizer-console` client id, and
`apiBaseUrl` pointing at the organizer API host. It SHALL **omit a fixed
organization id** — the tenant org is resolved at login via domain
discovery, not baked into config.

#### Scenario: Organizer config omits a fixed org id

- **WHEN** the organizer console loads `/config.json`
- **THEN** the config SHALL provide the issuer, `organizer-console` client
  id, and the organizer `apiBaseUrl`
- **AND** it SHALL NOT require a fixed organization id
