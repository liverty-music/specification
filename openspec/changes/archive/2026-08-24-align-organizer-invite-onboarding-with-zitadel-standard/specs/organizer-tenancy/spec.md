## MODIFIED Requirements

### Requirement: Organizer tenant orgs use a passkey-primary login policy with a designed recovery path

Every runtime-provisioned Organizer tenant org SHALL be given an **explicit**
login policy — it SHALL NOT inherit the instance default (admin
Google-IdP-only) policy. The policy SHALL make **passkeys the primary
credential** and SHALL have this shape:

- `passwordlessType = PASSWORDLESS_TYPE_ALLOWED` — passkeys enabled and primary;
  operators enroll a passkey on first login.
- `allowUsernamePassword = true` — **local authentication is enabled.** Despite
  its name, this field gates ALL local authentication (username plus **passkey**
  OR password), not only passwords: with it disabled, the hosted login UI
  renders no username-entry form and, with no external IdP configured, the
  invited operator is left with an empty login card and cannot proceed.
  Passkey-primary / "no passwords" is therefore expressed by
  `passwordlessType=ALLOWED` **plus never setting a password on the operator**
  (the operator's only usable local method is the passkey), NOT by disabling
  local authentication.
- `allowRegister = false` — no open self-registration; operator accounts are
  backend-provisioned for vetted Organizers only.
- `allowExternalIDP = true` — permit OIDC federation so an Organizer that
  already has a workspace IdP can federate.
- `ignoreUnknownUsernames = true` — the login flow SHALL NOT disclose whether a
  given account or org exists (anti-enumeration).
- `defaultRedirectUri = <organizer console origin>` — after the operator
  completes credential setup via the invitation flow (which runs outside any
  in-flight OIDC request), the identity provider SHALL redirect them to the
  organizer console, from which the console completes sign-in. Without this, an
  operator who accepts the invite would dead-end on an identity-provider page
  with no path back to the console.
- `allowDomainDiscovery` — **NOT required (MVP defaults it off).**

A **recovery path MUST exist** — passkey-only with **no** recovery is
prohibited. Recovery SHALL be an **admin-initiated re-invite** (the system
re-issues the operator's invitation after out-of-band verification), optionally
with an email magic-link/OTP self-serve fallback; any non-passkey fallback lane
SHALL be step-up protected so it is not a weaker bypass. The policy SHALL NOT
rely on a hard `allowLocalAuthentication=false` lockdown; `no password on the
operator` expresses the "no passwords" intent while the invite/recovery lane
stays available.

Synced passkeys (iCloud Keychain / Google Password Manager) survive
single-device loss, so a second **hardware** authenticator is NOT mandated for
this operator persona.

**Org resolution is bound to the operator's account, not to a URL parameter.**
The single OIDC app serves all tenants; the operator's org is fixed by the
**invitation** (the invite code is bound to the operator, who belongs to exactly
one tenant org) and, thereafter, by the operator's authenticated session/token.
An operator SHALL NOT be routed to a different org by supplying a different
email, and a session belonging to a different org SHALL NOT satisfy an
onboarding entry for this tenant (the console enforces the token's org — see
`organizer-console`). This covers consumer-domain operators without any
per-tenant domain verification.

Applying this policy per org, the exact field values, per-tenant IdP wiring, and
the invitation channel/TTL are runtime concerns of `organizer-accounts`. This
requirement defines the required shape.

#### Scenario: A provisioned tenant org has the passkey-primary policy

- **WHEN** an Organizer tenant org is provisioned
- **THEN** it SHALL have an explicitly set login policy, not the inherited admin
  default
- **AND** the policy SHALL be passkey-primary with **local authentication
  enabled** (`passwordlessType=PASSWORDLESS_TYPE_ALLOWED`,
  `allowUsernamePassword=true`, `allowRegister=false`) and the operator SHALL be
  created with no password so the passkey is their only usable local method
- **AND** `allowExternalIDP` and `ignoreUnknownUsernames` SHALL be enabled

#### Scenario: The policy renders a usable login and returns the operator to the console

- **WHEN** an invited operator reaches the tenant org's hosted login
- **THEN** local authentication SHALL be available (no empty login card)
- **AND** after the operator completes passkey setup via the invitation flow,
  the identity provider SHALL redirect them to the organizer console
  (`defaultRedirectUri`)

#### Scenario: Operator completes first login by enrolling a passkey

- **WHEN** the backend creates a no-password operator and the operator opens the
  invitation and enrolls a passkey
- **THEN** the operator SHALL complete first login by enrolling a passkey via the
  invitation flow
- **AND** passkeys SHALL be the credential used on subsequent logins

#### Scenario: A recovery path exists for a lost passkey

- **WHEN** an operator loses access to their passkey(s)
- **THEN** an admin SHALL be able to re-invite them (re-issue the invitation)
  after out-of-band verification
- **AND** a policy with no recovery path (passkey-only, no re-invite / no
  fallback) SHALL be rejected
- **AND** any non-passkey fallback lane SHALL be step-up protected

#### Scenario: Org is resolved by org-pinned entry for every operator

- **WHEN** any operator (consumer / free-mail such as `gmail.com`, or a custom
  domain) signs in
- **THEN** the org SHALL be resolved from the operator's own account/token, never
  by the email domain: the invitation binds the operator to exactly one tenant
  org on first login, and the authenticated session/token thereafter
- **AND** an operator SHALL NOT be routed into a different org by supplying a
  different address, and a session belonging to a different org SHALL NOT satisfy
  onboarding for this tenant (no cross-org access; `ignoreUnknownUsernames` keeps
  org existence undisclosed)
- **AND** no per-tenant domain verification SHALL be required for this path

#### Scenario: Email-domain discovery is a future optional enhancement

- **WHEN** a later change enables type-email-only routing for an Organizer that
  has a **verified** custom domain (typically alongside enterprise SSO)
- **THEN** that enhancement MAY set `allowDomainDiscovery=true` for that org,
  gated on domain ownership verification (DNS-TXT) and excluding consumer /
  free-mail domains
- **AND** it SHALL remain additive — the account-bound org resolution above stays
  the baseline and is never removed
- **AND** this change neither requires nor implements domain discovery
