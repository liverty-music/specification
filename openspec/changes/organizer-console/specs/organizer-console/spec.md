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
domain. The org is fixed by *where the operator enters*: an **invitation link**
on first sign-in (see `login_hint` requirement below), then an **org handle**
(an `org_id` carried in the URL, or a remembered `org_id`), which the console
turns into the Zitadel `urn:zitadel:iam:org:id:<orgId>` scope on the OIDC
request. There is no fixed org id at build time and no org picker.
(Email-domain discovery is a future optional enhancement per
`organizer-tenancy`, not used here — so consumer / free-mail operators work
without per-tenant domain verification.)

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

### Requirement: login_hint pre-fill for first-time sign-in

The organizer console SHALL accept a `login_hint` query parameter on entry and
pass it to the OIDC authorization request so Zitadel pre-fills the operator's
email address in the login form. This is the first-time sign-in mechanism: the
provisioning backend (organizer-accounts) sends an invitation email to the
operator containing a link of the form
`organizer.{base}/?org_id=<tenantOrgId>&login_hint=<email>`. Clicking it:

1. pins the tenant org via the `org:id` scope (existing org-handle logic);
2. pre-fills the email via `login_hint` so the operator skips the email entry
   step in Zitadel's login UI;
3. for uninitialized operators (no passkey registered), Zitadel's Login v2
   guides passkey registration **within the OIDC auth-request context** —
   provided the backend has created a pending **invite code** for the operator
   (Zitadel `CreateInviteCode`). Login v2 detects the invited user, sends a
   verification-code email, and after the code + passkey ceremony finalises the
   in-flight OIDC auth request, redirecting to `/auth/callback` → `/welcome`
   with no dead-end. Without an invite code, Login v2 has no auth method to
   offer a passwordless-only operator and renders an empty login form (verified
   dead-end, 2026-08-21); provisioning MUST therefore create the invite code.

The `login_hint` is a first-sign-in UX aid only; the console does not require
it to be present (returning operators sign in without it). The invite-code and
email-delivery responsibilities belong to the backend provisioner — see the
design D5 note and task 4.3.

#### Scenario: Invitation link pre-fills the operator's email on first sign-in

- **WHEN** an operator follows an invitation link containing `?org_id=<id>&login_hint=<email>`
- **THEN** the console SHALL pass `login_hint` to the OIDC authorization request
- **AND** Zitadel SHALL display the login form with the operator's email pre-filled
- **AND** for an uninitialized operator **who has a pending invite code**, Zitadel
  SHALL guide passkey registration within the OIDC flow and redirect to
  `/auth/callback` on completion
- **AND** for an uninitialized operator **with no invite code**, Zitadel SHALL
  render an empty login form (no auth method to offer) — so provisioning MUST
  create the invite code before inviting the operator

#### Scenario: Returning operator signs in without login_hint

- **WHEN** a returning operator navigates to the console with only `?org_id=<id>`
  (no `login_hint`)
- **THEN** the console SHALL initiate the OIDC flow with the `org:id` scope only
- **AND** Zitadel SHALL authenticate the operator using their existing passkey
