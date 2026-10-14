# Sign in as organizer

## Purpose

An operator signs in to the organizer console, a separate app from the fan
app and the admin console, and always lands in their own Organizer's tenant,
never another one, whether signing in for the first time from an invitation or
returning with a passkey.

## Requirements

### Requirement: Sign in as organizer via org-pinned entry

The organizer console SHALL authenticate operators through the identity provider's
sign-in (PKCE, no client secret) using the shared `organizer-console` client. The operator's
tenant org is **bound to their account** — NOT granted by a URL parameter and NOT by
email domain. An entry link MAY carry the tenant org's id as a hint (the `org_id`
query parameter of the invitation's return address) so that sign-in uses that
org's login policy, and the console MAY remember the hint on the device for later
sign-ins. The hint never grants access: the authenticated token's org decides, and
a hint that differs from it leads to re-authentication or denial, never into the
hinted org:

- **First sign-in** happens through the identity provider's standard invitation
  flow (the invite links to the IdP, not the console). After the operator sets
  up a passkey, the tenant login policy's default redirect returns them to the
  console (as Organizer.ProvisionTenant sets it up); the console then
  completes OIDC using the operator's freshly established session.
- **Returning sign-in** is initiated from the console and authenticated with the
  operator's existing passkey.

The console SHALL **enforce that the authenticated token's org is the intended
tenant org** (the remembered hint, when there is one). A session belonging to a different org (e.g. an unrelated identity-provider
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

- **WHEN** the console is entered while an identity-provider session for a different org
  already exists in the browser
- **THEN** the console SHALL NOT admit that session as the intended operator; it
  SHALL force re-authentication (or sign the stale session out) so the operator
  is authenticated as the correct tenant — never routed into another org

#### Scenario: A hint for another org grants nothing

- **WHEN** an operator of one Organizer opens the console through a link whose `org_id` names another tenant org
- **THEN** the console SHALL NOT admit them into that org: after one re-authentication the token's org still differs, and the access denied page is shown
