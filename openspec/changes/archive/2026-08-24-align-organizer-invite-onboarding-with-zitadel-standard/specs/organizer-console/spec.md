## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: login_hint pre-fill for first-time sign-in

**Reason**: First-time sign-in no longer routes through the console. Under the
Zitadel-standard invitation flow (this change), the invitation links directly to
the identity provider's credential-setup page (with the code carried in the
link), and the operator is returned to the console only *after* accepting the
invite (via the tenant login policy default redirect). The console-first
onboarding that `login_hint` supported — a console URL of the form
`organizer.{base}/?org_id=<id>&login_hint=<email>` that pre-fills and
auto-submits the email step — no longer exists, and onboarding correctness no
longer depends on `login_hint`. (This also removed a confusing "type the code"
screen that did not match the "click the link" invitation email.)

**Migration**: The frontend's `login_hint` handling is no longer load-bearing
for onboarding and MAY be retained only as an optional pre-fill convenience or
removed; no operator flow depends on it. First-time entry is covered by the
identity provider's invitation flow plus the tenant login policy default
redirect (see `organizer-accounts` and `organizer-tenancy`).
