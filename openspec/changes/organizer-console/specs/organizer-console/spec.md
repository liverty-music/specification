## Purpose

The organizer (seller) frontend shell: a dedicated `organizer.html` entry,
bundle-isolated from the consumer SPA and admin console, authenticated
against the operator's own Zitadel tenant org via org-pinned entry, with a
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

### Requirement: Authenticate operators via org-pinned entry, one client for all tenants

The organizer console SHALL authenticate operators through Zitadel OIDC
(PKCE, no client secret) using the shared `organizer-console` client, with
the operator's tenant org resolved by **org-pinned entry** — NOT by email
domain. The org is fixed by *where the operator enters*: the org-scoped
passkey init link on first sign-in, then an **org handle** (an org code/slug
in the URL, or a remembered `org_id`, or an app-level "email me a sign-in
link"), which the console turns into the Zitadel
`urn:zitadel:iam:org:id:<orgId>` scope on the OIDC request. There is no fixed
org id at build time and no org picker. (Email-domain discovery is a future
optional enhancement per `organizer-tenancy`, not used here — so consumer /
free-mail operators work without per-tenant domain verification.)

#### Scenario: Operator signs in and is routed to their org by org-pinned entry

- **WHEN** an operator opens the console with an org handle (org code/slug or
  a remembered `org_id`) and completes sign-in
- **THEN** the console SHALL pin the org via the `org:id` scope and return
  them authenticated to their own Organizer tenant org — never routing by raw
  email domain
- **AND** a mismatched org handle SHALL simply fail auth (no cross-org access)

#### Scenario: One OIDC client serves all tenants

- **WHEN** operators of different Organizer tenant orgs sign in
- **THEN** the same `organizer-console` OIDC client SHALL serve them all (no
  per-tenant client, no build-time org id)

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
