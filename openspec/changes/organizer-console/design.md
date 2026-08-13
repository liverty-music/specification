## Context

See proposal.md - Why. Mirrors the admin console pattern (bundle-isolated
entry + dedicated hosting) for the organizer surface. Depends on
`organizer-tenancy` (the `organizer-console` OIDC app + per-tenant login
policy with domain discovery). Full design:
[`docs/organizer-platform-design.md`](../../../docs/organizer-platform-design.md).

## Goals / Non-Goals

**Goals:** a bundle-isolated organizer entry, OIDC login via domain
discovery, a role-claim route guard, a placeholder, and the dedicated
hosting.

**Non-Goals:** business screens; the organizer API server
(`organizer-rpc-server`); per-org branding; a reception PWA.

## Decisions

**D1 — One OIDC client, org resolved by domain discovery.** A single
`organizer-console` client serves all tenants; the operator's org is resolved
at login by email domain discovery (enabled on tenant orgs in
`organizer-tenancy`). This is why the organizer `/config.json` omits a fixed
`zitadelOrgId` — baking one in would break the multi-tenant single-app model.

**D2 — Role-claim route guard, backend is source of truth.** Unlike the admin
console (where Google Workspace login *is* the wall), any tenant-org account
authenticates successfully; the console guard therefore inspects the
`organizer-console` project roles claim and admits only `master`. Real
enforcement is at the backend; the guard is UX.

**D3 — Dedicated hosting mirrors admin-console-hosting.** `organizer.{base}`
host with HTTPRoute + cert + Cloud DNS + per-host `/config.json`; bundle
isolation is enforced the same way as the admin console (consumer chunk
graph contains no organizer module).

**D4 — Consumer config contract unchanged.** The organizer entry defines its
own config shape (this change); the consumer's `frontend-runtime-config`
requirement governs the consumer SPA only and is not modified.

## Risks / Trade-offs

- **Shared AppConfig type** → if the organizer entry reuses the consumer
  AppConfig type, `zitadelOrgId` must become optional for the organizer
  variant; keep the consumer's required-org contract intact (implementation
  reconciliation, not a consumer spec change).
- **Bundle-isolation regression** → reuse the admin console's chunk-graph CI
  assertion.

## Migration Plan

1. frontend: `organizer.html` entry (bundle-isolated), OIDC via domain
   discovery, role-claim route guard, placeholder; chunk-graph CI assertion.
2. cloud-provisioning: `organizer.{base}` host (HTTPRoute, cert, Cloud DNS) +
   per-host ConfigMap; add the host to the `organizer-console` OIDC app
   redirect URIs.
- Rollback: additive entry + host; remove with no consumer/admin impact.
