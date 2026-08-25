## 1. Specification (proto)

- [x] 1.1 `rpc/organizer/v1/organizer_service.proto`: bare-verb `Get` (empty `GetRequest` — token-derived bootstrap, mirrors `UserService.Create`; `GetResponse` wraps the `Organizer` entity — identity only) and bare-verb `ListArtists` (carries the `OrganizerId` from `Get`; `ListArtistsResponse` carries `repeated Artist artists`); import the `Organizer` and `Artist` entities from `organizer-accounts`; document the per-RPC error matrix: INVALID_ARGUMENT (missing/malformed `OrganizerId` on `ListArtists`) / FAILED_PRECONDITION (caller's own Organizer deactivated) / PERMISSION_DENIED (any other authz failure, non-revealing — deliberately no `NOT_FOUND`) / UNAUTHENTICATED (absent/invalid token)
- [x] 1.2 `buf lint`/`format`/`breaking` pass; open specification PR, merge, cut Release, confirm BSR gen succeeds

## 2. Backend — server & authorization

- [x] 2.1 Dedicated organizer Connect server on its own port (`ORGANIZER_SERVER_PORT`, e.g. 8091 — distinct from fan 8080 / admin 8090 / webhook 9090) serving `rpc.organizer.v1.OrganizerService`; excluded from the fan and admin servers; built via the shared `NewConnectServer` factory so health stays on its own unauthenticated mux
- [x] 2.2 Org-scoped authorization interceptor: validate JWT, require the organizer-console project id in `aud`, read `role → { orgId }` (preserve the inner `orgId` — the existing extraction flattens to `[]string` and discards it), derive the caller's Zitadel org as the id appearing in BOTH exactly one login-scope scope `urn:zitadel:iam:org:id:<orgId>` (zero or multiple → deny) and an `orgId` under which the operator holds a role (the two MUST agree; any role suffices, top role `owner`); applies to `Get` and `ListArtists`
- [x] 2.3 `Get` handler: resolve the caller's Organizer from the token by the `zitadel_org_id` matching the caller's Zitadel org (add a `GetByZitadelOrgID` lookup); if active return identity (id, name), if deactivated → FAILED_PRECONDITION, if none linked → PERMISSION_DENIED (non-revealing). `ListArtists` handler: same resolution + state handling; additionally verify the supplied `OrganizerId` equals the resolved Organizer; return the roster via the repository (empty when none), `ORDER BY a.id` ascending (stable, UUID v7 ≈ creation order; mirrors the existing `listPerformersByEventIDs` convention)
- [x] 2.4 Tests (crown-jewel security): cross-organizer `ListArtists` (`OrganizerId` resolving to another org) → PERMISSION_DENIED; missing role / missing `aud` / login-scope↔role-claim disagreement / zero-or-multiple login-scope orgs / no-linked-Organizer → PERMISSION_DENIED (non-revealing); caller's own Organizer deactivated → FAILED_PRECONDITION; missing/malformed `OrganizerId` on `ListArtists` → INVALID_ARGUMENT; no token → UNAUTHENTICATED; happy paths: `Get` resolves own organizer from the token, `ListArtists` returns own roster (incl. empty roster)
- [x] 2.5 `make check` passes with upgraded BSR package

## 3. Cloud-provisioning (ingress)

- [x] 3.1 `organizer-console-api` workload (name per `workload-naming-convention`, mirroring `admin-console-api`) at `api.organizer.{base}`: HTTPRoute `organizer-console-api-route` + Service `organizer-console-api-svc` + TLS cert (certmap) + Cloud DNS (dev + prod) + HealthCheckPolicy `organizer-console-api-policy`
- [x] 3.2 CORS allowlist per env (`ORGANIZER_CORS_ALLOWED_ORIGINS`): prod = `https://organizer.liverty-music.app` only; dev = `https://organizer.dev.liverty-music.app` + localhost dev origins (mirroring the fan/admin overlays) so the dev console isn't blocked
- [x] 3.3 `make lint` (kustomize render) passes; `pulumi preview` shows only intended additions

## 4. Ship to prod

- [x] 4.1 Backend PR merged → release → prod pin bump; confirm the organizer server pod is running
- [x] 4.2 Cloud-provisioning PR merged → ArgoCD synced (host, cert, DNS, CORS)
- [x] 4.3 Verify in prod (at the API level, using a real operator token — the organizer console UI that *consumes* these RPCs is a separate follow-up change, so verification is via `api.organizer.liverty-music.app` directly): `Get` returns the operator's own organizer (200) and `ListArtists` its roster (200, empty allowed); a cross-organizer request is denied (`PERMISSION_DENIED`, non-revealing); the organizer service is not reachable on the fan/admin API hosts (404); no-token is `UNAUTHENTICATED` (401); and the login-scope token shape holds (exactly one inner orgId in the project-roles claim, project id in `aud`). All confirmed 2026-08-25. (Prod verification also surfaced and fixed a create-order grant gap — the organizer IAM user's read-only `app`-schema grant had to be re-applied via a catch-up migration once Pulumi created the user.)
