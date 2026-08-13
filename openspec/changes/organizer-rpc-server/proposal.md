## Why

Organizer operators need an API to read their own Organizer. This sub-change
(4/4 of roadmap step ①) adds the organizer-facing `OrganizerService.Get` on a
**dedicated** Connect server at `api.organizer.{base}` with its own CORS,
cert, DNS, and health, plus **org-scoped role-claim authorization** — every
prior audience surface on this platform (`admin-rpc-server`) gets its own
server, and the external organizer audience must too. Grounded in
`docs/organizer-platform-design.md` and `docs/zitadel-tenancy-model.md`,
tracked by liverty-music/specification#759. Depends on `organizer-accounts`
(the Organizer entity) and `organizer-tenancy` (the `organizer-console`
project + audience).

## What Changes

- Add `rpc/organizer/v1/organizer_service.proto`: bare-verb **`Get`**
  returning the authenticated Organizer's identity + associated artists. The
  request carries an `OrganizerId` that MUST equal the token-derived tenant.
- Serve it on a **dedicated organizer Connect server** at
  `api.organizer.{base-domain}` with its own CORS allowlist (only the
  `organizer.{base}` origin), TLS cert, Cloud DNS, and health check. The
  consumer and admin servers SHALL NOT serve organizer services, and this
  server SHALL NOT serve consumer/admin services.
- Add an **org-scoped authorization interceptor**: validate the JWT, require
  the organizer-console project id in the token `aud`, read the roles claim
  (`role → { orgId → domain }`), and authorize `{tenant, role}` — the inner
  orgId is the tenant. Reject with `PERMISSION_DENIED` on a missing/empty
  roles claim, an `aud` without the project id, or a mismatch between the
  session's login-scope org and the requested Organizer; `UNAUTHENTICATED`
  when the token is absent/invalid.

Explicit non-goals: organizer-side `Update`/`List` (Phase 2); any write/
business RPCs (later changes); the admin surface (in `organizer-accounts`).

## Capabilities

### New Capabilities
- `organizer-rpc-server`: the dedicated organizer Connect server
  (`api.organizer.{base}` + CORS + cert + DNS + health), the
  `OrganizerService.Get` RPC, and the org-scoped role-claim authorization
  with its failure matrix.

### Modified Capabilities
<!-- None. The organizer server is a new, isolated surface; existing
     consumer/admin servers are unchanged (they already exclude services
     they do not own). -->

## Impact

- **specification**: new `rpc/organizer/v1/organizer_service.proto` (imports
  the `Organizer` entity from `organizer-accounts`). Ships via the cross-repo
  release order.
- **backend**: a dedicated organizer Connect server + `OrganizerService.Get`
  handler + the org-scoped authorization interceptor (analogous to
  `rpc-auth-scoping`, tenant variant); reads the tenant→Organizer link
  (`zitadel_org_id`) from `organizer-accounts`.
- **cloud-provisioning**: `api.organizer.{base}` ingress host (HTTPRoute,
  cert, Cloud DNS), CORS config, and health; mirrors `admin-rpc-server`.
