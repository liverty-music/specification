## 1. Specification (proto)

- [ ] 1.1 `rpc/organizer/v1/organizer_service.proto`: bare-verb `Get` (request carries `OrganizerId`) returning the Organizer identity + associated artists; import the `Organizer` entity from `organizer-accounts`; document the error matrix
- [ ] 1.2 `buf lint`/`format`/`breaking` pass; open specification PR, merge, cut Release, confirm BSR gen succeeds

## 2. Backend — server & authorization

- [ ] 2.1 Dedicated organizer Connect server (own port) serving `rpc.organizer.v1.OrganizerService`; excluded from the consumer and admin servers
- [ ] 2.2 Org-scoped authorization interceptor: validate JWT, require the organizer-console project id in `aud`, read `role → { orgId }`, authorize `{tenant, role}`, resolve active tenant from login-scope org
- [ ] 2.3 `Get` handler: verify request `OrganizerId` == token tenant; resolve tenant→Organizer via the `zitadel_org_id` link; return identity + associated artists
- [ ] 2.4 Tests (crown-jewel security): cross-organizer `Get` → PERMISSION_DENIED; missing role / missing `aud` / login-scope mismatch → PERMISSION_DENIED; no token → UNAUTHENTICATED; happy path returns own organizer
- [ ] 2.5 `make check` passes with upgraded BSR package

## 3. Cloud-provisioning (ingress)

- [ ] 3.1 `api.organizer.{base}` ingress host: HTTPRoute + TLS cert (certmap) + Cloud DNS (dev + prod); health check
- [ ] 3.2 CORS allowlist limited to the `organizer.{base}` origin
- [ ] 3.3 `make lint` (kustomize render) passes; `pulumi preview` shows only intended additions

## 4. Ship to prod

- [ ] 4.1 Backend PR merged → release → prod pin bump; confirm the organizer server pod is running
- [ ] 4.2 Cloud-provisioning PR merged → ArgoCD synced (host, cert, DNS, CORS)
- [ ] 4.3 Verify in prod: an operator's console reads their own organizer via `api.organizer.liverty-music.app`; a cross-organizer request is denied; the organizer service is not reachable on the consumer/admin API hosts
