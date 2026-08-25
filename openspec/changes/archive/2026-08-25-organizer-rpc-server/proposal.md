## Why

Organizer operators need an API to read their own Organizer and the artists it
represents. This sub-change (4/4 of roadmap step ①) adds the organizer-facing
`OrganizerService.Get` and `OrganizerService.ListArtists` on a **dedicated**
Connect server at `api.organizer.{base}` with its own CORS, cert, DNS, and
health, plus **org-scoped role-claim authorization** — every prior audience
surface on this platform (`admin-rpc-server`) gets its own server, and the
external organizer audience must too. Grounded in
`docs/organizer-platform-design.md` and `docs/zitadel-tenancy-model.md`,
tracked by liverty-music/specification#759. Depends on `organizer-accounts`
(the Organizer entity) and `organizer-tenancy` (the `organizer-console`
project + audience).

## What Changes

- Add `rpc/organizer/v1/organizer_service.proto` with two bare-verb read RPCs,
  mirroring the admin `OrganizerService`'s separation of entity-get from
  roster-list (the organizer entity intentionally carries no artist field):
  - **`Get`** returns the caller's own Organizer identity (id, name), resolved
    from the token — `GetRequest` is empty. The console has no `OrganizerId`
    before this call, so `Get` is the sanctioned bootstrap that yields it,
    mirroring the fan `UserService.Create` resolve-from-token exception.
  - **`ListArtists`** returns the artists the Organizer represents; it carries
    the `OrganizerId` obtained from `Get`, verified to resolve to the caller's
    own Organizer (`rpc-auth-scoping`).
  Both RPCs pass the same org-scoped authorization.
- Serve them on a **dedicated organizer Connect server** at
  `api.organizer.{base-domain}` with its own CORS allowlist (only the
  `organizer.{base}` origin), TLS cert, Cloud DNS, and health check. The
  fan and admin servers SHALL NOT serve organizer services, and this
  server SHALL NOT serve fan or admin services.
- Add an **org-scoped authorization interceptor**: validate the JWT, require
  the organizer-console project id in the token `aud`, and read the roles claim
  (`role → { orgId → domain }`, where each `orgId` is a Zitadel org id and the
  top role is `owner`). The caller's Zitadel org is fixed by two token-derived
  ids that MUST agree — exactly one login-scope scope
  (`urn:zitadel:iam:org:id:<orgId>`) and the `orgId` under which the operator
  holds a role — and its `Organizer` is resolved via the `zitadel_org_id` link;
  `ListArtists`'s `OrganizerId` MUST equal that resolved Organizer. Reject with
  `PERMISSION_DENIED` (non-revealing) on a missing/empty roles claim, an `aud`
  without the project id, zero/multiple login-scope orgs, org-id disagreement,
  or no linked Organizer; `FAILED_PRECONDITION` when the caller's own Organizer
  is deactivated (own org — not concealed); `UNAUTHENTICATED` when the token is
  absent/invalid.

Explicit non-goals: organizer-side `Update` and any write/business or
association-mutation RPCs (later changes); managing the roster
(`AssociateArtist`/`DisassociateArtist`) stays admin-only in
`organizer-accounts`; the admin surface itself (in `organizer-accounts`); an
operator identity/profile RPC — the console reads the operator's email/name
from the OIDC token, so no server RPC is needed this phase; roster pagination
(deferred — rosters are admin-curated and small).

## Capabilities

### New Capabilities
- `organizer-rpc-server`: the dedicated organizer Connect server
  (`api.organizer.{base}` + CORS + cert + DNS + health), the
  `OrganizerService.Get` and `OrganizerService.ListArtists` RPCs, and the
  org-scoped role-claim authorization with its failure matrix.

### Modified Capabilities
<!-- None. The organizer server is a new, isolated surface; existing
     fan and admin servers are unchanged (they already exclude services
     they do not own). -->

## Impact

- **specification**: new `rpc/organizer/v1/organizer_service.proto` (imports
  the `Organizer` and `Artist` entities from `organizer-accounts`). Ships via
  the cross-repo release order.
- **backend**: a dedicated organizer Connect server + `OrganizerService.Get`
  and `ListArtists` handlers + the org-scoped authorization interceptor
  (analogous to `rpc-auth-scoping`, org-scoped variant); resolves the caller's
  Organizer via the `zitadel_org_id` link and reads the roster from
  `organizer-accounts`.
- **cloud-provisioning**: the `organizer-console-api` workload (name per
  `workload-naming-convention`, mirroring `fan-api`/`admin-console-api`) at
  `api.organizer.{base}` — HTTPRoute (`organizer-console-api-route`), TLS cert,
  Cloud DNS, CORS config, and health; mirrors `admin-rpc-server`.
