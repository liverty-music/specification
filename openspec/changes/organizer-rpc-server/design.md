## Context

See proposal.md - Why. Mirrors `admin-rpc-server` (each audience gets its own
Connect server + ingress + CORS + cert + DNS + health). Depends on
`organizer-accounts` (the `Organizer` and `Artist` entities, the
`zitadel_org_id` link between an Organizer and its Zitadel org, and the
`organizer_artists` roster) and
`organizer-tenancy` (the `organizer-console` project id used as the token
audience). Full design + authorization matrix:
[`docs/organizer-platform-design.md`](../../../docs/organizer-platform-design.md);
Zitadel claim shapes in
[`docs/zitadel-tenancy-model.md`](../../../docs/zitadel-tenancy-model.md).

## Goals / Non-Goals

**Goals:** a dedicated, isolated organizer API server; `OrganizerService.Get`
and `ListArtists` (the read surface for step ①); correct org-scoped
authorization with an explicit failure matrix.

**Non-Goals:** organizer-side `Update` and write/business or association-
mutation RPCs (later); roster mutation (`AssociateArtist`/`DisassociateArtist`)
stays admin-only; the admin surface (`organizer-accounts`).

## Decisions

**D1 — Dedicated server per audience.** The organizer audience is external
and org-scoped, distinct from fan (public) and admin (Google-Workspace)
audiences, so it gets its own Connect server — the `organizer-console-api`
workload (named per `workload-naming-convention`, mirroring `fan-api` and
`admin-console-api`) — at ingress `api.organizer.{base}`, with its own CORS
allowlist, cert, DNS, and health, and is excluded from the other servers.
Mirrors `admin-rpc-server`.

**D2 — Authorization from the org-scoped role claim.** No "tenant" entity
exists in the domain; the only defined nouns are the `Organizer` (entity), its
Zitadel org, and the `zitadel_org_id` link between them. Authorization is
therefore stated in those terms. Validate JWT → require the organizer-console
project id in `aud` (console requests the `...:project:id:{id}:aud` scope) →
read `role → { orgId → domain }`, where each `orgId` is a Zitadel org id (the
top role is `owner`, not `admin`). The caller's Zitadel org is the id that
appears BOTH in the login-scope scope (`urn:zitadel:iam:org:id:<orgId>`) and as
an `orgId` under which the operator holds a role; these two derivations MUST
agree. A multi-org operator is authorized only against their login-scope org.
Holding any role for that org is sufficient (no specific-role gate this phase).
The existing backend role extraction flattens the claim to a `[]string` of role
names and discards the inner `orgId` — the org-scoped interceptor MUST preserve
`role → orgId` so the caller's Zitadel org can be derived. Applies uniformly to
`Get` and `ListArtists`. Analogous to `rpc-auth-scoping` (body id vs token),
here the requested `OrganizerId` (resolved via `zitadel_org_id`) vs the caller's
Zitadel org.

**D3 — Authorization failures are PERMISSION_DENIED / UNAUTHENTICATED, never
500; existence is never revealed.** Missing/empty roles claim (require
`accessTokenRoleAssertion=true` on the app), `aud` without the project id,
login-scope↔role-claim org disagreement, requested `OrganizerId` resolving to a
different org, the caller's Organizer being **deactivated** (per
`organizer-accounts`, which mandates rejecting operations on a deactivated
Organizer), or **no Organizer linked** to the caller's Zitadel org → all
`PERMISSION_DENIED`, non-revealing (unlike the admin surface, which returns
`NOT_FOUND`, because the organizer surface is external and org-scoped, matching
`rpc-auth-scoping`'s "SHALL NOT reveal whether the resource exists"). Absent or
invalid token → `UNAUTHENTICATED`. The one non-authz exception: a missing or
malformed `OrganizerId` fails validation first → `INVALID_ARGUMENT` via
protovalidate.

**D4 — `Get` / `ListArtists` request shape.** Each request carries an explicit
`OrganizerId` verified to resolve to the caller's own Organizer (its
`zitadel_org_id` equals the caller's Zitadel org), consistent with
`rpc-auth-scoping`, rejecting any other value. `GetResponse` wraps the
`Organizer` entity; `ListArtistsResponse` carries `repeated Artist artists`.

**D5 — Roster is a separate RPC, not embedded in `Get`.** The `Organizer`
entity intentionally carries no artist field, and the admin `OrganizerService`
already models the roster with a dedicated `ListArtists` RPC (Get returns the
entity; ListArtists returns the roster). The organizer-facing surface mirrors
that split — and the fan `UserService.Get`, which likewise returns only
its entity — rather than embedding artists in `GetResponse`. This keeps entity
reads and roster reads independently cacheable and paginatable in a later phase.

**D6 — `ListArtists` stable order by artist id.** Return the roster
`ORDER BY a.id` ascending. Artist ids are UUID v7 (minted by the backend's
single `entity.NewID()` site), so id order is a deterministic, unique,
effectively creation-time ordering — fixing UI reordering and test flakiness
and giving a total order a later pagination phase can page over without a
tie-breaker. This mirrors the existing `listPerformersByEventIDs` `ORDER BY
a.id` convention (same "stable, if not semantically billed" rationale). It
orders by artist creation, not roster-add time; a roster-add ordinal is a
future concern, tracked separately.

## Risks / Trade-offs

- **Assertion/aud misconfig silently denies or over-permits** → assert
  `accessTokenRoleAssertion` on the app and require the project id in `aud`;
  cover the no-role / wrong-aud / scope-mismatch paths with tests (the
  crown-jewel security tests).
- **Organizer resolution** → resolve the caller's Organizer by the
  `zitadel_org_id` link from `organizer-accounts` (DB is source of truth); do
  not depend on a Zitadel round-trip per request.

## Migration Plan

1. specification: `rpc/organizer/v1/organizer_service.proto` → merge →
   Release → BSR gen.
2. backend: dedicated organizer Connect server + `Get` and `ListArtists`
   handlers + org-scoped authorization interceptor; tests for the failure
   matrix.
3. cloud-provisioning: `api.organizer.{base}` ingress (HTTPRoute, cert, Cloud
   DNS), CORS, health; mirror `admin-rpc-server`.
- Rollback: additive server + host; remove with no fan or admin impact.

## Open Questions

- None blocking. The exact port/health wiring follows the `admin-rpc-server`
  precedent and is an implementation detail.
