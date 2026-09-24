# Bootstrap operator credentials on first sign in

## Purpose

The first operator of a newly created Organizer sets up a passkey from a
single invitation email and lands in the organizer console signed in to their
own Organizer, without ever typing a code; an admin re-invites them when they
lose access.

## Requirements

### Requirement: Operator bootstraps credentials on first sign-in

When an admin creates an Organizer (OrganizerUseCase.Create), its tenant
provisioning (Organizer.ProvisionTenant) SHALL create the initial operator as a
human user in the Organizer's tenant with a **verified email and no password**,
and onboard them using the identity provider's **standard invitation flow**: the
system creates an invite code for the operator and has the identity provider
send **one** branded invitation email whose
"accept" link opens the identity provider's own credential-setup page with the
code already carried in the link. The operator SHALL complete first sign-in by
**clicking that link** (never by transcribing a code) and registering a passkey.
On completion the operator SHALL be returned to the organizer console
authenticated (the tenant's post-setup redirect targets the console, as
Organizer.ProvisionTenant sets it up), landing on the owner-gated placeholder.

The invitation email SHALL be the **only** message the operator must act on for
first sign-in (no separate "transport" email, and no second code email under the
normal single-entry flow). The credential (invite/verification code) SHALL
remain on the identity-provider surface and SHALL NOT be exposed in a
console/application URL.

Recovery SHALL be an **admin-initiated re-invite** (the system re-issues the
operator's invitation), consistent with the tenant's passkey-primary policy
that Organizer.ProvisionTenant sets up. Org resolution is bound to the
operator's account by the invitation itself — the operator cannot be routed to a
different org by supplying a different email (no cross-org access).

#### Scenario: Operator completes first sign-in via init link and passkey

- **WHEN** an initial operator opens their invitation ("accept invite") link and
  starts first sign-in
- **THEN** they SHALL register a passkey without transcribing any code, and be
  returned to the organizer console authenticated to their own Organizer tenant
  org

#### Scenario: Operator is routed to their org by org-pinned entry

- **WHEN** an operator signs in (first-time via the invitation, or thereafter
  with their passkey)
- **THEN** the org SHALL be resolved from the operator's own account/token — the
  invitation binds the operator to exactly one tenant org — never by raw email
  domain
- **AND** supplying a different email SHALL NOT route them into a different org
  (no cross-org access)

#### Scenario: The invitation credential is never placed in a console URL

- **WHEN** the invitation email and its link are generated
- **THEN** the invite/verification code SHALL appear only on the identity
  provider surface and SHALL NOT appear in any console/application URL

#### Scenario: Recovery is an admin re-invite

- **WHEN** an operator cannot sign in (e.g. lost all authenticators)
- **THEN** recovery SHALL be an admin-initiated re-invite that re-issues the
  operator's invitation, not a weaker password/self-registration lane
