## 1. Backend — server factory + admin authorization

- [x] 1.1 Extract a shared server/interceptor factory from `NewConnectServer` so the consumer and admin servers are built identically except for (port, CORS origins, extra interceptors, handler set); preserve the `interceptor-chain-ordering` invariants
- [x] 1.2 Implement an admin-authorization interceptor that reads the bridged claims and requires the `admin` role, rejecting others with `PERMISSION_DENIED`; place it after the claims bridge, before validation
- [x] 1.3 Remove the per-method `auth.RequireRole(ctx, "admin")` calls from `ConcertModerationHandler` (the handler returns to pure mapping)
- [x] 1.4 Add config for the admin server: `ADMIN_SERVER_PORT` and `ADMIN_CORS_ALLOWED_ORIGINS` (and wire defaults for local dev)
- [x] 1.5 Unit tests: admin server denies a valid non-admin JWT with `PERMISSION_DENIED`; allows an admin JWT; consumer server has no admin service registered; both chains preserve ordering

## 2. Backend — DI wiring of two servers

- [x] 2.1 In DI, build the consumer server (existing services, minus admin) and the admin server (admin services only) via the factory; give the admin server its own health handler
- [x] 2.2 Register BOTH servers with the shutdown Drain phase so both drain on signal
- [x] 2.3 Move `ConcertModerationService` registration to the admin server ONLY (boundary-gated); the consumer server stops serving it in the SAME release. Do NOT register it on the consumer server as a dual-serve — task 1.3 removed the per-method check and the admin-authorization interceptor is admin-server-only, so a consumer-side registration would be UNGATED. (If a zero-gap cutover is ever required, the only safe dual-serve is to additionally attach the admin-authorization interceptor to that handler on the consumer server too, then drop it in the follow-up — see design "Migration / sequencing".)
- [x] 2.4 `make check` green

## 3. cloud-provisioning — admin API ingress

- [x] 3.1 Expose a second container port on the backend Deployment for the admin server
- [x] 3.2 Add an admin backend `Service` (ClusterIP, `appProtocol: kubernetes.io/h2c`) targeting the admin port
- [x] 3.3 Add an `HTTPRoute` for `api.admin.{env}` on the shared external gateway → admin Service; leave the consumer API route unchanged
- [x] 3.4 Add certmap + Cloud DNS entries for `api.admin.{env}` and a gRPC `HealthCheckPolicy` for the admin Service
- [x] 3.5 Backend config/env: add `ADMIN_SERVER_PORT` + `ADMIN_CORS_ALLOWED_ORIGINS` (admin origins). KEEP the admin origin in the consumer `CORS_ALLOWED_ORIGINS` for now — it is removed only in the follow-up (5.4), AFTER the frontend flips to `api.admin`, so the admin console is never CORS-broken mid-cutover
- [x] 3.6 `make lint` / kustomize render green; `pulumi preview` clean for dev and prod

## 4. Frontend — admin client base URL

- [x] 4.1 Add the admin API base URL (`api.admin.{env}`) to the admin per-host runtime config (`/config.json`) and its env ConfigMaps
- [x] 4.2 Point the admin `ConcertModerationService` client at the admin API base URL from runtime config; leave the consumer client unchanged
- [x] 4.3 Tests + `make check` green

## 5. Ship to production (coordinated cutover)

- [ ] 5.1 Apply cloud-provisioning so `api.admin.{env}` is live (Service + route + cert + DNS + health) and the admin CORS config is in place. The consumer CORS still includes the admin origin. The `api.admin` route is unhealthy until the backend serves the admin port (5.2) — fine, nothing uses it yet
- [ ] 5.2 Release backend: the admin server serves `ConcertModerationService` (boundary-gated) on the admin port; the consumer server no longer serves it. NOTE: until 5.3, the admin console (still pointed at the consumer API) gets `unimplemented` for moderation — a brief functional gap on an internal tool, with NO security exposure (the consumer API simply no longer hosts those procedures)
- [ ] 5.3 Release frontend so the admin console targets `api.admin`; the gap closes. Verify approve/reject end-to-end against the admin host in prod
- [ ] 5.4 Follow-up cloud-provisioning: now that the admin console no longer calls the consumer API, drop the admin origin from the consumer `CORS_ALLOWED_ORIGINS`
- [ ] 5.5 Verify a non-admin token is rejected at the admin host, and that the consumer host returns `unimplemented` for the moderation procedures
