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
- Sub-owner roles (only `master` now); per-org branding.

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
radius). Note the `machine-user` "no rotation, expires 2099" caveat applies
and warrants a rotation runbook given this user's power.

**D4 — Tenant-org login policy is set explicitly, never inherited.** A new
org inherits the instance `DefaultLoginPolicy` = the admin Google-IdP-only
policy, which would make external operators unable to sign in. Provisioning
MUST set a passkey-only policy + `allowDomainDiscovery`. This change defines
the required shape; `organizer-accounts` applies it per org.

**D5 — No proto in this change.** Organizer tenancy is IaC + spec only; the
entity/RPC proto lands in `organizer-accounts`. So this change ships without
BSR generation.

## Risks / Trade-offs

- **Latent verification** → the tenant-org login-policy requirement can only
  be observed once orgs are created (`organizer-accounts`). It is a forward
  contract; its acceptance test lives in that change.
- **Machine-user power** → mitigate with the narrowest instance role that
  still allows org-create + grants, credential isolation, and a rotation
  runbook.
- **Topology drift detection** → Pulumi must be taught that runtime tenant
  orgs are not drift (the modified `identity-management` "No third org"
  scenario), else it would try to revert them.

## Migration Plan

1. specification: the `identity-management` topology delta + the new
   `organizer-tenancy` capability spec → merge (no BSR gen needed).
2. cloud-provisioning (IaC): add the `organizer-console` project + `master`
   role + `organizer-console`/`backend-api` apps in the `liverty-music` org,
   and the `organizer-provisioner` machine user + credential; ensure Pulumi
   does not treat runtime tenant orgs as drift.
- Rollback: additive — remove the project, apps, and machine user; no
  consumer/admin impact (no tenant orgs exist yet at this stage).

## Open Questions

- The exact narrowest Zitadel instance role for `organizer-provisioner`
  (e.g. an org-manager-class role vs `IAM_OWNER`) is an implementation
  detail confirmed during the cloud-provisioning task; it does not change
  the spec or the decomposition.
