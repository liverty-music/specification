## Context

See proposal.md - Why. Mirrors `admin-rpc-server` (each audience gets its own
Connect server + ingress + CORS + cert + DNS + health). Depends on
`organizer-accounts` (the `Organizer` entity + the `zitadel_org_id`
tenant→Organizer link) and `organizer-tenancy` (the `organizer-console`
project id used as the token audience). Full design + authorization matrix:
[`docs/organizer-platform-design.md`](../../../docs/organizer-platform-design.md);
Zitadel claim shapes in
[`docs/zitadel-tenancy-model.md`](../../../docs/zitadel-tenancy-model.md).

## Goals / Non-Goals

**Goals:** a dedicated, isolated organizer API server; `OrganizerService.Get`;
correct org-scoped authorization with an explicit failure matrix.

**Non-Goals:** organizer-side `Update`/`List` (Phase 2); write/business RPCs;
the admin surface (`organizer-accounts`).

## Decisions

**D1 — Dedicated server per audience.** The organizer audience is external
and org-scoped, distinct from consumer (public) and admin (Google-Workspace)
audiences, so it gets its own Connect server, ingress `api.organizer.{base}`,
CORS allowlist, cert, DNS, and health — and is excluded from the other
servers. Mirrors `admin-rpc-server`.

**D2 — Authorization from the org-scoped role claim.** Validate JWT →
require the organizer-console project id in `aud` (console requests the
`...:project:id:{id}:aud` scope) → read `role → { orgId → domain }`; the
inner orgId is the tenant. Authorize `{tenant, role}`; resolve the active
tenant from the session's login-scope org; a multi-org operator is
authorized only against that org. Analogous to `rpc-auth-scoping` (body id
vs token), here target Organizer vs token tenant.

**D3 — Every failure is PERMISSION_DENIED / UNAUTHENTICATED, never 500.**
Missing/empty roles claim (require `accessTokenRoleAssertion=true` on the
app), `aud` without the project id, or login-scope↔target mismatch →
`PERMISSION_DENIED`; absent/invalid token → `UNAUTHENTICATED`.

**D4 — `Get` request shape.** `GetRequest` carries an explicit `OrganizerId`
verified equal to the token tenant (consistent with `rpc-auth-scoping`),
rejecting any other value.

## Risks / Trade-offs

- **Assertion/aud misconfig silently denies or over-permits** → assert
  `accessTokenRoleAssertion` on the app and require the project id in `aud`;
  cover the no-role / wrong-aud / scope-mismatch paths with tests (the
  crown-jewel security tests).
- **Tenant→Organizer resolution** → read the `zitadel_org_id` link from
  `organizer-accounts` (DB is source of truth); do not depend on a Zitadel
  round-trip per request.

## Migration Plan

1. specification: `rpc/organizer/v1/organizer_service.proto` → merge →
   Release → BSR gen.
2. backend: dedicated organizer Connect server + `Get` handler + org-scoped
   authorization interceptor; tests for the failure matrix.
3. cloud-provisioning: `api.organizer.{base}` ingress (HTTPRoute, cert, Cloud
   DNS), CORS, health; mirror `admin-rpc-server`.
- Rollback: additive server + host; remove with no consumer/admin impact.

## Open Questions

- None blocking. The exact port/health wiring follows the `admin-rpc-server`
  precedent and is an implementation detail.
