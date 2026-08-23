## MODIFIED Requirements

### Requirement: Initial operator bootstraps credentials on first sign-in

The system SHALL create the initial operator as a human user in the Organizer's
tenant org with a **verified email and no password**, and onboard them using
Zitadel's **standard invitation flow**: the system creates an invite code for
the operator and has Zitadel send **one** branded invitation email whose
"accept" link opens the identity provider's own credential-setup page with the
code already carried in the link. The operator SHALL complete first sign-in by
**clicking that link** (never by transcribing a code) and registering a passkey.
On completion the operator SHALL be returned to the organizer console
authenticated (the tenant login policy's post-setup redirect targets the
console — see `organizer-tenancy`), landing on the owner-gated placeholder.

The invitation email SHALL be the **only** message the operator must act on for
first sign-in (no separate "transport" email, and no second code email under the
normal single-entry flow). The credential (invite/verification code) SHALL
remain on the identity-provider surface and SHALL NOT be exposed in a
console/application URL.

Recovery SHALL be an **admin-initiated re-invite** (the system re-issues the
operator's invitation), consistent with the tenant org's passkey-primary policy
and its recovery path in `organizer-tenancy`. Org resolution is bound to the
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
