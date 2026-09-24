## Purpose

The static Zitadel platform scaffolding for the Organizer B2B tenancy model:
a shared, actor-named `organizer-console` project (roles + apps) owned by the
product org, a dedicated provisioner machine user, and the login policy that
runtime-provisioned Organizer tenant orgs must receive. Per-Organizer orgs,
the domain entity, the console, and the API server are separate changes.

## ADDED Requirements

### Requirement: Organizer tenant orgs use a passkey-primary login policy with a designed recovery path

Every runtime-provisioned Organizer tenant org SHALL be given an **explicit**
login policy — it SHALL NOT inherit the instance default (admin
Google-IdP-only) policy. The policy SHALL make **passkeys the primary
credential** and SHALL have this shape:

- `passwordlessType = PASSWORDLESS_TYPE_ALLOWED` — passkeys enabled and
  primary; operators enroll a passkey on first login (the backend creates the
  operator with `request_passwordless_registration=true` and delivers the
  Zitadel passkey-registration init link).
- `allowUsernamePassword = false` — no passwords for Organizer operators.
- `allowRegister = false` — no open self-registration; operator accounts are
  backend-provisioned for vetted Organizers only.
- `allowExternalIDP = true` — permit OIDC federation so an Organizer that
  already has a workspace IdP (Google Workspace / Microsoft Entra) can
  federate; wiring a *specific* tenant IdP is a per-tenant runtime concern.
- `ignoreUnknownUsernames = true` — the login flow SHALL NOT disclose whether
  a given account or org exists (anti-enumeration).
- `allowDomainDiscovery` — **NOT required (MVP defaults it off)**. Org
  resolution is org-pinned (below), not email-domain-based, so no per-tenant
  domain verification is needed. Email-domain discovery is a **future optional
  enhancement** for a tenant that verifies a custom domain and wants
  type-email-only routing (typically alongside enterprise SSO).

A **recovery path MUST exist** — passkey-only with **no** recovery is
prohibited. Recovery SHALL be an **admin-initiated re-invite** (Zitadel
re-issues the operator's passkey-registration link after out-of-band
verification), optionally with an email magic-link/OTP self-serve fallback;
any non-passkey fallback lane SHALL be step-up protected so it is not a weaker
bypass. The policy SHALL NOT rely on a hard `allowLocalAuthentication=false`
lockdown (Zitadel #11682 / #8996 make full passkey-only lockdown fragile);
`allowUsernamePassword=false` expresses the "no passwords" intent while the
init-link/recovery lane stays available.

Synced passkeys (iCloud Keychain / Google Password Manager) survive
single-device loss, so a second **hardware** authenticator is NOT mandated for
this operator persona (reserve that for regulated / super-admin accounts).

**Org resolution SHALL be org-pinned, not email-domain-based.** The single
OIDC app serves all tenants; the caller's org is fixed by *where they enter*,
and the console pins it via the Zitadel `urn:zitadel:iam:org:id:<orgId>`
scope: (a) first login uses the org-scoped passkey init link; (b) a returning
operator on the same device uses the `org_id` the console remembered at first
login; (c) a fresh device / cleared storage resolves the org via an org handle
(org code/slug in the URL) **or** an app-layer "email me a sign-in link" flow
(the backend looks up the operator's org(s) and emails an org-pinned link —
this works for consumer/free-mail addresses and never discloses org existence).
An operator SHALL NOT be routed to a different org by supplying a different
email; a mismatched org-pinned entry simply fails auth (no cross-org access).
This uniform path covers consumer-domain operators (the common indie-artist /
gmail case) without any per-tenant domain verification.

Applying this policy per org, the exact field values, per-tenant IdP wiring,
and the init-link channel/TTL are runtime concerns of `organizer-accounts`;
the org-handle carrier (console URL / `/config.json`) is delivered by
`organizer-console` / `frontend-runtime-config`. This requirement defines the
required shape. (Best-practice basis recorded in design.md "Best-practice
review".)

#### Scenario: A provisioned tenant org has the passkey-primary policy

- **WHEN** an Organizer tenant org is provisioned
- **THEN** it SHALL have an explicitly set login policy, not the inherited
  admin default
- **AND** the policy SHALL be passkey-primary
  (`passwordlessType=PASSWORDLESS_TYPE_ALLOWED`, `allowUsernamePassword=false`,
  `allowRegister=false`)
- **AND** `allowExternalIDP` and `ignoreUnknownUsernames` SHALL be enabled
- **AND** `allowDomainDiscovery` SHALL NOT be required (MVP defaults it off;
  org resolution is org-pinned)

#### Scenario: Operator completes first login by enrolling a passkey

- **WHEN** the backend creates a no-password operator with
  `request_passwordless_registration=true` and delivers the returned
  passkey-registration init link
- **THEN** the operator SHALL complete first login by enrolling a passkey via
  that link
- **AND** passkeys SHALL be the credential used on subsequent logins

#### Scenario: A recovery path exists for a lost passkey

- **WHEN** an operator loses access to their passkey(s)
- **THEN** an admin SHALL be able to re-invite them (re-issue the
  passkey-registration link) after out-of-band verification
- **AND** a policy with no recovery path (passkey-only, no re-invite / no
  fallback) SHALL be rejected
- **AND** any non-passkey fallback lane SHALL be step-up protected

#### Scenario: Org is resolved by org-pinned entry for every operator

- **WHEN** any operator (consumer / free-mail such as `gmail.com`, or a custom
  domain) signs in
- **THEN** the org SHALL be resolved by an **org-pinned entry**, never by the
  email domain: the org-scoped passkey init link on first login; a remembered
  `org_id` on the same device thereafter; and on a fresh device an org handle
  (org code/slug in the URL) or an app-layer "email me a sign-in link" flow
  (backend resolves the operator's org(s) and emails an org-pinned link)
- **AND** the console SHALL pin the org via the Zitadel
  `urn:zitadel:iam:org:id:<orgId>` scope
- **AND** an operator SHALL NOT be routed into a different org by supplying a
  different address (a mismatched org-pinned entry simply fails auth — no
  cross-org access; `ignoreUnknownUsernames` keeps org existence undisclosed)
- **AND** no per-tenant domain verification SHALL be required for this path
- **AND** the concrete console URL / runtime-config carrier for the org handle
  is delivered by `organizer-console` / `frontend-runtime-config`

#### Scenario: Email-domain discovery is a future optional enhancement

- **WHEN** a later change enables type-email-only routing for an Organizer that
  has a **verified** custom domain (typically alongside enterprise SSO)
- **THEN** that enhancement MAY set `allowDomainDiscovery=true` for that org,
  gated on domain ownership verification (DNS-TXT) and excluding consumer /
  free-mail domains
- **AND** it SHALL remain additive — the org-pinned path above stays the
  baseline and is never removed
- **AND** this MVP change neither requires nor implements domain discovery
