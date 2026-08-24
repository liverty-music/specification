# organizer-console Specification

## Purpose
The organizer (seller) frontend shell: a dedicated `organizer.html` entry,
bundle-isolated from the consumer SPA and admin console, authenticated
against the operator's own Zitadel tenant org via org-pinned entry, with a
role-claim route guard and a post-login placeholder. Business screens land
in later changes.
## Requirements
### Requirement: Bundle isolation from the consumer SPA and admin console

The organizer console SHALL be built as a separate Vite/Rollup entry point
(`organizer.html`) such that no organizer-only code is included in any chunk
loaded by the consumer SPA or the admin console. Adding it MUST NOT increase
the consumer SPA's downloaded bundle size or regress its Core Web Vitals.

#### Scenario: Consumer page loads no organizer code

- **WHEN** a fan loads the consumer SPA at the consumer hostname
- **THEN** the consumer entry's chunk graph SHALL contain no module
  originating from the organizer source directory

### Requirement: Authenticate operators via org-pinned entry, one client for all tenants

The organizer console SHALL authenticate operators through Zitadel OIDC (PKCE,
no client secret) using the shared `organizer-console` client. The operator's
tenant org is **bound to their account** — NOT to a URL parameter and NOT to
email domain:

- **First sign-in** happens through the identity provider's standard invitation
  flow (the invite links to the IdP, not the console). After the operator sets
  up a passkey, the tenant login policy's default redirect returns them to the
  console (see `organizer-tenancy` / `organizer-accounts`); the console then
  completes OIDC using the operator's freshly established session.
- **Returning sign-in** is initiated from the console and authenticated with the
  operator's existing passkey.

The console SHALL **enforce that the authenticated token's org is the intended
tenant org**. A session belonging to a different org (e.g. an unrelated Zitadel
SSO session already present in the browser) SHALL NOT be silently accepted for a
different operator/tenant: the console SHALL detect the mismatch and force
re-authentication (or sign the stale session out) rather than admitting the
wrong operator. There is no fixed org id at build time and no org picker.

#### Scenario: Operator signs in and is routed to their org by org-pinned entry

- **WHEN** an operator completes sign-in
- **THEN** the console SHALL return them to their own Organizer tenant org,
  resolved from their authenticated account/token (the org is bound to the
  operator) — never by raw email domain
- **AND** a session or entry that does not resolve to the operator's own org
  SHALL fail auth (no cross-org access)

#### Scenario: One OIDC client serves all tenants

- **WHEN** operators of different Organizer tenant orgs sign in
- **THEN** the same `organizer-console` OIDC client SHALL serve them all (no
  per-tenant client, no build-time org id)

#### Scenario: Invited operator lands on the console after accepting the invite

- **WHEN** an invited operator completes credential setup via the identity
  provider's invitation flow
- **THEN** they SHALL be returned to the organizer console and, after the console
  completes OIDC, land authenticated on their own Organizer tenant org

#### Scenario: A reused or mismatched session does not silently onboard the wrong operator

- **WHEN** the console is entered while a Zitadel session for a different org
  already exists in the browser
- **THEN** the console SHALL NOT admit that session as the intended operator; it
  SHALL force re-authentication (or sign the stale session out) so the operator
  is authenticated as the correct tenant — never routed into another org

### Requirement: Route guard admits only owner-role operators

The organizer console SHALL guard its routes: unauthenticated visitors are
sent to sign-in, and an authenticated user is admitted only if the token's
`organizer-console` project roles include `owner`; otherwise access is
denied. The backend remains the source of truth for authorization; the guard
is a UX gate. On success the operator lands on a post-login welcome
placeholder.

#### Scenario: Unauthenticated visitor is redirected to sign-in

- **WHEN** an unauthenticated visitor navigates to an organizer console route
- **THEN** the guard SHALL redirect them to Zitadel sign-in

#### Scenario: Authenticated operator with owner role sees the placeholder

- **WHEN** an authenticated operator whose token carries the `owner` role
  loads the console
- **THEN** they SHALL see the post-login welcome placeholder

#### Scenario: Authenticated account without the owner role is denied

- **WHEN** an authenticated user whose token lacks the `owner` role loads
  the console
- **THEN** the guard SHALL deny access to organizer screens

### Requirement: Organizer runtime config resolves the org at login

The organizer console SHALL load its runtime config from `/config.json`
carrying the Zitadel issuer, the `organizer-console` client id, and
`apiBaseUrl` pointing at the organizer API host. It SHALL **omit a fixed
organization id** — one client serves all tenants and the tenant org is
resolved at login by **org-pinned entry** (an org handle carried in the URL /
remembered / re-issued sign-in link), not baked into config nor resolved by
email domain.

#### Scenario: Organizer config omits a fixed org id

- **WHEN** the organizer console loads `/config.json`
- **THEN** the config SHALL provide the issuer, `organizer-console` client
  id, and the organizer `apiBaseUrl`
- **AND** it SHALL NOT require a fixed organization id (the org is resolved
  per session by org-pinned entry)

