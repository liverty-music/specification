# Organizer Platform — Design & Change Decomposition

Durable design for the **Organizer** feature cluster (roadmap change ① of
`ticketing-platform-roadmap.md`, "the vetted seller foundation"). The
original single `organizer-accounts` change grew too large — a
spec-completeness audit surfaced ~33 gaps spanning identity, provisioning,
a dedicated API server, dedicated hosting, and offboarding. To avoid
losing scope coverage, ① is **decomposed into four changes** (see the last
section); this document is the source of truth they are authored from.

Related: identity/RBAC mechanics live in
[`zitadel-tenancy-model.md`](./zitadel-tenancy-model.md); this doc covers
the Organizer domain, its surfaces, and the resolved audit gaps.

## Confirmed decisions

- **Organizer = the vetted seller entity**, distinct from Artist/Performer
  (schema.org `organizer`). Exists only via admin creation → existence is
  the vetting; **no business `verified` flag**.
- **Entity fields:** `OrganizerId` (UUIDv7), `OrganizerName` (1–200 chars),
  `zitadel_org_id` (the tenant org, unique, backend-only), and an
  operational `provisioning_state` (`provisioning` / `active` /
  `deactivated`) — this is a lifecycle marker, **not** the rejected
  business `verified` flag.
- **Organizer↔Artist:** an Organizer represents many Artists; **each Artist
  is represented by at most one Organizer** via a partial-unique index on
  `artist_id` (`WHERE provisioning_state != 'deactivated'`, so a
  deactivated Organizer frees its artists for re-association).
- **Tenancy: Zitadel org-per-Organizer** + a shared, actor-named
  `organizer-console` project (owned by the `liverty-music` org),
  Project-Granted to each Organizer org; `owner` role via User Grant.
  Actor-named so a future `venue-console` never collides. Full model:
  `zitadel-tenancy-model.md`.
- **Provisioning:** static platform is IaC; per-Organizer org + grant +
  operator is created **at runtime via the Zitadel Management API** in the
  admin vetting flow.
- **Login (confirmed 2026-08 after best-practice review):** organizer tenant
  orgs use a **passkey-primary** login policy — `passwordlessType=ALLOWED`,
  `allowUsernamePassword=false` (no passwords), `allowRegister=false`
  (backend-provisioned only), `allowExternalIDP=true` (federate to a tenant's
  own workspace IdP when it has one), `ignoreUnknownUsernames=true` —
  explicitly set at provisioning (never inherit the admin default). A
  **recovery path is mandatory** (admin re-invite via re-issued passkey init
  link; optional step-up-protected magic-link/OTP); passkey-only-with-no-
  recovery is prohibited (synced passkeys reduce but do not remove single-
  credential risk; Zitadel hard passkey-only lockdown is fragile —
  #11682/#8996). **Org resolution is org-pinned, not email-domain-based**
  (org-scoped init link → remembered `org_id` → org-code/slug or app-layer
  "email me a link" → the `org:id` scope) — one OIDC app serves all tenants,
  no per-tenant domain verification; email-domain discovery is a future
  optional enhancement (`allowDomainDiscovery` off in MVP). Full rationale:
  the `organizer-tenancy` change design.md "Best-practice review".
- **Fan ⇄ operator same person:** two **independent identities** (separate
  `sub` per org); never linked/merged; no cross-org SSO between the fan app
  and the organizer console.
- **Offboarding:** a `deactivated` state hook ships now (backend rejects all
  organizer RPCs for a deactivated Organizer; operators deactivated in
  Zitadel). Full cascade is Phase 2.

## Domain model

```
Organizer(id, name, zitadel_org_id UNIQUE, provisioning_state)
   └──< organizer_artists (organizer_id, artist_id) >── Artist (existing)
        partial UNIQUE(artist_id) WHERE state != 'deactivated'
        both FKs ON DELETE CASCADE
```
`zitadel_org_id` is the load-bearing link from the token's tenant claim to
the Organizer PK; **DB is the source of truth**, org metadata mirror is
deferred. Not exposed on the consumer proto (internal linkage). Audit
timestamps use domain-specific `*_at` names (schema-lint bans
`created_at/updated_at`).

## RPC surface

- **Admin** (`rpc.admin.v1.OrganizerService`, admin-role gated, rides the
  existing admin server): bare-verb `Create`, `AssociateArtist`,
  `DisassociateArtist`, `List`, `Get`. `Create` takes `operator_email`
  (+ optional display name); non-idempotent on name but
  **compensating on the provisioning saga** (a retry completes a
  half-provisioned Organizer, never duplicates). `List`/`Get` are required
  for the admin management screen. `AssociateArtist` takes an existing
  `ArtistId` and **rejects `NOT_FOUND`** for unknown artists (no
  create-on-demand); rejects `ALREADY_EXISTS` if the artist is already
  claimed. `DisassociateArtist` is idempotent; reassignment = disassociate
  + associate.
- **Organizer** (`rpc.organizer.v1.OrganizerService`, org-scoped, dedicated
  server): bare-verb `Get` only for MVP (returns the caller's identity +
  associated artists). Request carries an `OrganizerId` verified to equal
  the token-derived tenant (rpc-auth-scoping, tenant variant). Update/List
  deferred.
- **protovalidate:** `OrganizerId.value = uuid`; wrap name in
  `OrganizerName` (`min_len=1, max_len=200`) per the `ArtistName`
  convention. Each RPC documents its error matrix (INVALID_ARGUMENT /
  NOT_FOUND / ALREADY_EXISTS / PERMISSION_DENIED / UNAUTHENTICATED).

## Provisioning saga (admin Create side effect)

Ordered, idempotent, compensating — keyed on `OrganizerId`:
1. Insert `organizers` row `provisioning_state = provisioning`.
2. Management API: create tenant org (name `org-<uuid-short>`, not the
   display name, to avoid collisions); **set the explicit passkey-primary
   login policy** (shape above: `passwordlessType=ALLOWED`,
   `allowUsernamePassword=false`, `allowRegister=false`, `allowExternalIDP=
   true`, `ignoreUnknownUsernames=true`; `allowDomainDiscovery` off in MVP).
3. Persist `zitadel_org_id` on the row.
4. Project-Grant `organizer-console` (role subset incl. `owner`) to the
   org.
5. Create the operator human user (no password) with
   `request_passwordless_registration=true` + User Grant `owner`; deliver the
   returned Zitadel **passkey-registration init link**
   (`requestPlatformType=platform`) → operator enrolls a passkey on first
   sign-in. Recovery = admin re-invite (re-issue the init link after
   out-of-band verification). Author the provisioner root-key **rotation
   runbook** here (the key created in `organizer-tenancy` is first consumed at
   this step).
6. Set `provisioning_state = active`.
On failure, a reconciler re-enters at the first incomplete step (each
Zitadel create is existence-checked). The operator is never left without an
`owner` grant.

**Machine user:** a dedicated `organizer-provisioner` (NOT the existing
single-org `backend-app` user) with the narrowest instance role that
permits org-create + cross-org grant; credential in ESC/Secret Manager,
isolated blast radius, rotation runbook required.

## Authorization (organizer surface)

Backend validates issuer/signature + **`aud` includes the organizer-console
project id** (console requests the `...:project:id:{id}:aud` scope), then
reads `urn:zitadel:iam:org:project:{projectId}:roles` = `role → { orgId →
domain }`; the inner orgId is the tenant. Failure matrix (all
`PERMISSION_DENIED`, never 500): missing/empty roles claim (require
`accessTokenRoleAssertion=true`, `projectRoleCheck=false`), `aud` without
the project id, login-scope org ≠ requested Organizer. A multi-org operator
is authorized only against the **session's login-scope org**. (The top role
in the roles claim is `owner`, not `admin`.) Zitadel
supplies identity + tenant + role; **which artists/events an Organizer may
touch is Liverty's own data** (`organizer_artists`, event ownership),
enforced in the backend.

## Delivery surfaces (the audit's deepest blind spot)

Mirroring the admin precedent (`admin-rpc-server`, `admin-console-hosting`):
- **Organizer API server:** serve `rpc.organizer.v1.OrganizerService` on a
  **dedicated** Connect server at `api.organizer.{base}` with its own CORS
  allowlist (only the `organizer.{base}` origin), cert, DNS, health, and
  tenant-scoped authorization. Exclude it from the consumer and admin
  servers. The **admin** OrganizerService rides the existing admin server.
- **Organizer console hosting:** serve `organizer.html` at
  `organizer.{base}` (`organizer.dev.liverty-music.app` /
  `organizer.liverty-music.app`) with HTTPRoute + certmap + Cloud DNS +
  per-host `/config.json`.
- **Runtime config:** the organizer `/config.json` carries the issuer + the
  `organizer-console` client id + `apiBaseUrl = api.organizer.{base}`, but
  **NOT a fixed `zitadelOrgId`** (one app serves all tenants). The org is
  resolved per session by an **org-pinned entry**, not the email domain: the
  org-scoped passkey init link on first login, then an org handle
  (org code/slug in the URL or a remembered `org_id`), and on a fresh device an
  org-code entry or an app-layer "email me a sign-in link" (backend org lookup,
  works for gmail) — all turned into the Zitadel
  `urn:zitadel:iam:org:id:<orgId>` scope. **Email-domain discovery is NOT used
  in the MVP** (a future optional enhancement for verified-custom-domain +
  enterprise-SSO tenants); **consumer/free-mail domains (gmail) never drive
  routing** (the common indie-artist case).
  Requires a `frontend-runtime-config` delta (its AppConfig currently assumes
  one static org) to carry the org handle.

## Observability

Emit backend analytics events `organizer.created` and
`organizer.artist.associated` (JetStream → PostHog), modeled as
admin-actor / group events keyed on `organizer_id` (no fan UserId); add
them to the event catalog in the same change. Wrap the provisioning call in
an OTel span + a `organizer_provisioning_failed` metric.

## Non-Goals (Phase 2 — stated so their absence is deliberate)

Slug/handle; contact/billing fields; organizer-side `Update`/`List`; full
offboarding cascade (org/grant/association teardown beyond the
`deactivated` hook); per-org branding; sub-owner 4-role RBAC + audit log;
org-creation rate limiting; the optional stable-`organizer-id` claim
Action. No data backfill (additive tables only).

## Change decomposition (① → four changes)

Dependency-ordered; each independently reviewable. Owned-gap references are
to the audit themes.

| Change | Scope | Owns (audit) | Depends on |
|--------|-------|--------------|------------|
| **`organizer-tenancy`** | `identity-management` topology delta (allow runtime Organizer tenant orgs); Zitadel platform **IaC**: `organizer-console` project + `owner` role + OIDC/API apps + `organizer-provisioner` machine user; per-org passkey-primary + recovery + federation + org-pinned-resolution login policy shape | A (login policy), C (machine user), identity topology | existing admin |
| **`organizer-accounts`** | Organizer **entity** (`zitadel_org_id`, `provisioning_state`) + Organizer↔Artist (partial-unique); **admin** `OrganizerService` (Create/AssociateArtist/DisassociateArtist/List/Get); **tenant provisioning saga** + operator bootstrap (email + init/passkey); **deactivated** hook; analytics events | A (operator seed/bootstrap), C (saga/linkage/state), D (offboard hook), E (entity/assoc/admin RPCs), G (analytics) | `organizer-tenancy` |
| **`organizer-console`** | `organizer.html` bundle-isolated entry (org-pinned login: org handle/slug + remembered `org_id` + "email me a link" → `org:id` scope; role-claim route guard; placeholder) + **hosting** (`organizer.{base}` DNS/cert/HTTPRoute/config.json) + `frontend-runtime-config` delta | A (route guard), C (login org-pinned), F (hosting, runtime-config) | `organizer-tenancy` (usable login target after `organizer-accounts`) |
| **`organizer-rpc-server`** | Dedicated organizer Connect server at `api.organizer.{base}` + CORS/cert/DNS/health; `rpc.organizer.v1.OrganizerService.Get`; **org-scoped role-claim authorization** (the failure matrix) | B (authz matrix), E (Get shape), F (server/CORS) | `organizer-tenancy` + `organizer-accounts` |

```
organizer-tenancy ──▶ organizer-accounts ──┬──▶ organizer-console
                                            └──▶ organizer-rpc-server
```

Downstream roadmap changes (②–⑥) depend on this cluster as a whole. Each
sub-change is created with `/opsx:propose` when its work starts.

## Open decisions (recommended defaults recorded above; confirm before build)

- ~~Login method~~ **Resolved (2026-08):** passkey-primary + mandatory
  recovery + optional workspace-IdP federation (not passkey-only, not
  password+MFA). See the Login bullet above.
- ~~Login org discovery~~ **Resolved (2026-08):** org-pinned entry (org
  handle/slug + remembered `org_id` + app-layer "email me a link" → `org:id`
  scope). Email-domain discovery dropped from MVP → future optional
  enhancement. See the Login bullet + `organizer-tenancy` design D6.
- Offboarding: **`deactivated` hook + partial-unique now** (recommended) vs
  fully Phase 2.
- Fan⇄operator: **two independent identities, no SSO** (recommended,
  confirm).
