## Context

See proposal.md - Why. Grounded in
[`docs/organizer-platform-design.md`](../../../docs/organizer-platform-design.md)
(the `organizer-tenancy` row of the four-change decomposition) and
[`docs/zitadel-tenancy-model.md`](../../../docs/zitadel-tenancy-model.md).
Today the instance pins exactly two orgs (`admin`, `liverty-music`) with a
single `admin` role; the `admin` org owns an `admin-console` project and the
`liverty-music` org owns the consumer `liverty-music` project. There is no
Organizer tenancy. This change adds the static platform scaffolding for it
and relaxes the topology pin — nothing per-tenant and no domain entity.

## Goals / Non-Goals

**Goals:**
- The static Zitadel resources every Organizer sub-change depends on: one
  shared `organizer-console` project (role + apps) and a provisioner machine
  user.
- Relax the topology pin so runtime Organizer tenant orgs are legal (not
  drift).
- Fix the required tenant-org login policy shape so later provisioning is
  unambiguous.

**Non-Goals:**
- The Organizer domain entity, admin vetting, and the runtime provisioning
  saga (`organizer-accounts`).
- `organizer.html` and its hosting (`organizer-console`).
- The `api.organizer.*` server, `OrganizerService.Get`, and org-scoped authz
  (`organizer-rpc-server`).
- Sub-owner roles (only `owner` now — named `owner` not `admin` to avoid
  collision with the internal `admin-console` role; editor/viewer/reception
  deferred); per-org branding.

## Decisions

**D1 — The shared project is owned by the `liverty-music` org, not a new
`platform` org nor the `admin` org.** The organizer console is a
Liverty-Music product surface, so it belongs with the other product
projects; a *separate* project (not the fan `liverty-music` project) keeps
its roles/grants/branding independent; and the `admin` org is hardened as
internal-only (Google Workspace, default org), so an external-facing app
must not live there. Owner org is only the project's administrative home —
operators authenticate in their own tenant org, so the owner org's login
policy never applies to them. (Full rationale: tenancy-model doc.)

**D2 — Actor-named project (`organizer-console`), not a generic `console`.**
Every mature platform splits back-office by actor; a generic name would
collide with a future `venue-console`. RBAC (roles/grants) is project-scoped,
so a distinct actor gets a distinct project; multiple apps (console web,
later a reception PWA) can share one project.

**D3 — Dedicated `organizer-provisioner` machine user.** Creating orgs +
cross-org grants needs instance-level rights far broader than the existing
single-org `backend-app` user (`ORG_USER_MANAGER` on one org). A dedicated
user isolates that blast radius; credential in ESC/Secret Manager.
*Alternative — reuse `backend-app`:* rejected (wrong scope + coupled blast
radius).

*Scope of the isolation (precise):* the isolation is at the
**Zitadel-identity / role** level — a distinct machine user with a distinct
instance role, so a leak of the `backend-app` key cannot create orgs and a
leak of the provisioner key is a separate credential. It is **not** isolated
at the GCP secret-access layer in this change: the backend consumes the
provisioner key at runtime as the `backend-app` GCP service account, so that
SA is granted read access to it (a `-backend-app-accessor` binding on the GSM
secret). Isolating GCP-layer read access — a dedicated provisioner *workload*
+ GCP SA bound to only this secret — is a **future hardening** designed
together with the backend consumption in `organizer-accounts`.

*Credential lifecycle (revised after best-practice review):* the security
delta over the existing `backend-app` "expires 2099, no rotation" pattern is
the **root key's own lifecycle**, not the operational tokens. Any machine user
authenticating with a JWT-profile key already gets **short-lived access
tokens** from the standard `jwt-bearer` OAuth flow (Zitadel default — no
long-lived bearer / PAT is stored, and nothing bespoke to build). What this
high-privilege identity MUST additionally satisfy is a **finite root-key
expiry + rotation runbook** — a year-2099 non-expiring key is prohibited.
Automated rotation / workload-identity federation is the target end-state
(future hardening); the rotation runbook is authored in `organizer-accounts`,
where the key is first consumed. Because the finite expiry (currently
`2027-08-13`) is a hardcoded date with no automated rotation, a **key-expiry
monitoring alert** (Cloud Monitoring / secret-age) SHALL accompany the runbook
so the key cannot silently expire and stall runtime provisioning.

**D4 — Tenant-org login policy is set explicitly, never inherited, and is
passkey-primary with a designed recovery path (not passkey-only).** A new org
inherits the instance `DefaultLoginPolicy` = the admin Google-IdP-only policy
(confirmed in Zitadel source `getOrgLoginPolicy`: an org with no active custom
policy falls back to the instance default), which would make external
operators unable to sign in. Provisioning MUST set an explicit policy.

The 2025-2026 state-of-the-art for a B2B operator console invite→first-login
flow is **passkey-primary with a passwordless fallback**, not passkey-only:
synced passkeys (iCloud/Google) survive single-device loss, so passkeys are
the right primary, but a recovery lane is non-negotiable (whole-account loss,
offboarding, and unfinished FIDO cross-ecosystem migration are residual gaps).
Zitadel-specific: a hard passkey-only lockdown is currently fragile
(`allowLocalAuthentication=false` bugs — zitadel#11682/#8996), reinforcing
"keep a fallback". So the required shape is: `passwordlessType=ALLOWED`
(primary) + `allowUsernamePassword=false` (no passwords) + `allowRegister=
false` (backend-provisioned only) + `allowExternalIDP=true` (federate to a
tenant's workspace IdP when it has one) + `ignoreUnknownUsernames=true` (no
enumeration), plus a mandatory recovery path (admin re-invite via re-issued
passkey init link; optional step-up-protected magic-link/OTP). A second
**hardware** authenticator is NOT mandated for this operator persona (reserve
for regulated / super-admin). **Org resolution is org-pinned, not
email-domain-based** — see D6 — so `allowDomainDiscovery` is NOT in the MVP
shape. This change defines the required shape; `organizer-accounts` applies it per org
(exact values, per-tenant IdP wiring, init-link channel/TTL). Full rationale +
sources: "Best-practice review" below.

**D5 — No proto in this change.** Organizer tenancy is IaC + spec only; the
entity/RPC proto lands in `organizer-accounts`. So this change ships without
BSR generation.

**D6 — Org resolution is org-pinned, not email-domain discovery (MVP).**
Because first login already persists `org_id` (the console remembers it) and
the console can always pin the org via the `urn:zitadel:iam:org:id:<orgId>`
scope, a *single* org-pinned path serves everyone: org-scoped init link →
remembered `org_id` → on a fresh device an org code/slug or an app-layer
"email me a sign-in link" (backend org lookup, works for gmail). Email-domain
discovery would only add value in one narrow spot — a custom-domain operator
on a fresh device typing their email instead of an org code — at the cost of
per-tenant DNS-TXT domain verification, enumeration hardening, and a console
branch, and it does not help the consumer-domain (gmail) majority at all. The
app-layer "email me a link" flow delivers the same "just type your email" UX
uniformly without domain verification, so it strictly dominates. Domain
discovery is therefore **dropped from the MVP** and recorded as a future
optional enhancement (verified custom domain + enterprise SSO). *Alternative —
require domain discovery as a second path:* rejected (redundant branch + real
per-tenant verification burden for a minor, minority-only convenience).

## Risks / Trade-offs

- **Latent verification** → the tenant-org login-policy requirement can only
  be observed once orgs are created (`organizer-accounts`). It is a forward
  contract; its acceptance test lives in that change.
- **Machine-user power** → mitigate with the narrowest built-in instance role
  (`IAM_ORG_MANAGER`, not `IAM_OWNER`), credential isolation, **short-lived
  operational tokens** (JWT-profile mint), and a rotation runbook. `IAM_ORG_
  MANAGER` still manages all orgs; a custom minimal `defaults.yaml` role is a
  recorded future hardening.
- **Passkey recovery** → passkey-primary is correct, but the recovery lane
  (admin re-invite; optional step-up magic-link/OTP) is mandatory — a
  passkey-only-no-recovery org would lock operators out. Zitadel's hard
  passkey-only lockdown is fragile (zitadel#11682/#8996), so the policy
  expresses "no passwords" via `allowUsernamePassword=false`, not a full
  `allowLocalAuthentication=false` lockdown.
- **Org resolution** → **org-pinned for everyone** (D6): org-scoped init link
  → remembered `org_id` → org code/slug or app-layer "email me a link" → the
  Zitadel `urn:zitadel:iam:org:id:<orgId>` scope. Keep `ignoreUnknownUsernames=
  true` so the login endpoint is not a tenant-enumeration oracle. No
  email-domain discovery and no per-tenant domain verification in the MVP; a
  mismatched org-pinned entry just fails auth. (Console URL/config carrier:
  `organizer-console` / `frontend-runtime-config`.)
- **Topology drift detection** → Pulumi must be taught that runtime tenant
  orgs are not drift (the modified `identity-management` "No third org"
  scenario), else it would try to revert them.

## Migration Plan

1. specification: the `identity-management` topology delta + the new
   `organizer-tenancy` capability spec → merge (no BSR gen needed).
2. cloud-provisioning (IaC): add the `organizer-console` project + `owner`
   role + `organizer-console`/`backend-api` apps in the `liverty-music` org,
   and the `organizer-provisioner` machine user + credential; ensure Pulumi
   does not treat runtime tenant orgs as drift.
- Rollback: additive — remove the project, apps, and machine user; no
  consumer/admin impact (no tenant orgs exist yet at this stage).

## Open Questions

*(none open — the former role question is resolved below.)*

- ~~The exact narrowest Zitadel instance role for `organizer-provisioner`.~~
  **Resolved:** `IAM_ORG_MANAGER` — the narrowest **built-in** instance role
  that permits `org.create` + cross-org Project/User grants (verified against
  Zitadel's role model; strictly less than `IAM_OWNER`). A still-narrower
  custom `defaults.yaml` `InternalAuthZ.RolePermissionMappings` role is
  possible but edits the Zitadel deployment config → deferred as future
  hardening.

## Best-practice review (2026-08)

This change was reviewed against current Zitadel docs (context7) and IDaaS
industry guidance (NIST SP 800-63B-4, FIDO Alliance 2024-25, Okta/Auth0/Clerk/
WorkOS/Corbado, Google Cloud workload-identity). Verdicts:

- **Org = tenant, project-per-actor, Project Grant, roles claim** → sound,
  matches Zitadel's recommended B2B model. Unchanged.
- **Explicit per-org login policy (no inherit)** → correct and necessary
  (confirmed `getOrgLoginPolicy` falls back to the admin default otherwise).
- **Login method** → passkey-primary is state-of-the-art; **passkey-only with
  no recovery** was flagged as an anti-pattern and softened to **passkey-
  primary + designed recovery + optional federation** (synced passkeys reduce,
  but don't remove, the single-credential risk). See D4.
- **Org resolution** → email-domain discovery was initially specced, then
  dropped: since first login persists `org_id` and the console pins the org
  via the `org:id` scope, one org-pinned path serves everyone; domain
  discovery is a redundant branch with a real per-tenant DNS-verification cost
  that helps only a custom-domain minority on fresh devices, and an app-layer
  "email me a link" flow beats it uniformly. MVP = org-pinned only; domain
  discovery deferred as a future optional enhancement. See D6.
- **Provisioner credential** → an indefinite year-2099 static key on a
  high-privilege identity is an anti-pattern; revised to a finite root-key
  expiry + rotation runbook (operational access tokens are already short-lived
  via the standard `jwt-bearer` flow). See D3.
- **Provisioner role** → `IAM_ORG_MANAGER` is broad (all-org management); kept
  as the narrowest built-in, with a custom minimal role recorded as future
  hardening.

Deferred to `organizer-accounts` (runtime): exact per-org login-policy values,
per-tenant IdP federation wiring, init-link channel/TTL, the provisioner
credential-minting + rotation implementation, a **dedicated provisioner
workload + GCP SA** that isolates GCP-layer read access to the provisioner key
(so `backend-app`'s SA no longer reads it — see D3), and a **key-expiry
monitoring alert** for the finite provisioner key.

## Zitadel built-in surface (used vs custom)

Grounds the downstream cluster (`organizer-accounts`, `organizer-console`):
the login / passkey / token / role-grant machinery is Zitadel-native (this
instance already self-hosts Login v2), so only a thin app layer is custom.

**Used as-is (Zitadel built-in):**
- Hosted **Login v2 UI** (already self-hosted) — sign-in, passkey (WebAuthn)
  prompt, IdP/SSO redirect, MFA/step-up. No custom login screens.
- **Passkey registration link API** (`POST /v2/users/{id}/passkeys/
  registration_link`) — `sendLink` (Zitadel emails via urlTemplate) or
  `returnCode` (self-distribute). First-login enrollment on the hosted page.
- **Management API** — create org, create human user, set org login policy,
  Project Grant, User Grant, IdP config (the `organizer-accounts` saga).
- **OIDC/OAuth2 + PKCE**, JWT/JWKS, token lifetimes (`DefaultOidcSettings`),
  refresh tokens.
- **Roles claim assertion** (`accessTokenRoleAssertion`) + Project/User Grant
  → tenant-scoped `owner` role in the token.
- **Reserved scopes**: `urn:zitadel:iam:org:id:<orgId>` (org-pin) and
  `...:project:id:<id>:aud` (audience).
- **Login-policy flags**: `passwordlessType`, `allowUsernamePassword`,
  `allowRegister`, `allowExternalIDP`, `ignoreUnknownUsernames`.
- **External IdP federation** templates (Google Workspace / Entra OIDC) —
  future per-tenant.
- **SMTP notifications** (Postmark wired) — can send the passkey init link.
- **Actions v2** — optional stable `organizer-id` custom claim (future).

**Custom (this cluster builds):**
- organizer console SPA (post-auth console + OIDC client via `oidc-client-ts`
  PKCE; login redirects to hosted Login v2).
- Org-pinned resolution glue (slug→`org_id`, remembered `org_id`, app-layer
  "email me a sign-in link" backend lookup) — the org pre-step, since domain
  discovery is dropped (D6). Credential screens stay Zitadel's.
- Provisioning saga orchestration (backend Go) + Organizer DB row.
- Backend authz (`aud` + tenant-scoped roles claim validation).
- Hosting (`organizer.{base}` DNS/cert/HTTPRoute/`config.json`).

Boundary: **identity / passkey / token / role-grant = Zitadel built-in;
org pre-step + console + provisioning + hosting = custom.**
