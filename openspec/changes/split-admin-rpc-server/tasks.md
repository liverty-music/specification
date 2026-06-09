## 1. Backend — server factory + admin authorization

- [ ] 1.1 Extract a shared server/interceptor factory from `NewConnectServer` so the consumer and admin servers are built identically except for (port, CORS origins, extra interceptors, handler set); preserve the `interceptor-chain-ordering` invariants
- [ ] 1.2 Implement an admin-authorization interceptor that reads the bridged claims and requires the `admin` role, rejecting others with `PERMISSION_DENIED`; place it after the claims bridge, before validation
- [ ] 1.3 Remove the per-method `auth.RequireRole(ctx, "admin")` calls from `ConcertModerationHandler` (the handler returns to pure mapping)
- [ ] 1.4 Add config for the admin server: `ADMIN_SERVER_PORT` and `ADMIN_CORS_ALLOWED_ORIGINS` (and wire defaults for local dev)
- [ ] 1.5 Unit tests: admin server denies a valid non-admin JWT with `PERMISSION_DENIED`; allows an admin JWT; consumer server has no admin service registered; both chains preserve ordering

## 2. Backend — DI wiring of two servers

- [ ] 2.1 In DI, build the consumer server (existing services, minus admin) and the admin server (admin services only) via the factory; give the admin server its own health handler
- [ ] 2.2 Register BOTH servers with the shutdown Drain phase so both drain on signal
- [ ] 2.3 Move `ConcertModerationService` registration to the admin server; (cutover option) optionally keep it ALSO on the consumer server behind the per-method check during the migration window — decide per design "Migration / sequencing"
- [ ] 2.4 `make check` green

## 3. cloud-provisioning — admin API ingress

- [ ] 3.1 Expose a second container port on the backend Deployment for the admin server
- [ ] 3.2 Add an admin backend `Service` (ClusterIP, `appProtocol: kubernetes.io/h2c`) targeting the admin port
- [ ] 3.3 Add an `HTTPRoute` for `api.admin.{env}` on the shared external gateway → admin Service; leave the consumer API route unchanged
- [ ] 3.4 Add certmap + Cloud DNS entries for `api.admin.{env}` and a gRPC `HealthCheckPolicy` for the admin Service
- [ ] 3.5 Backend config/env: add `ADMIN_SERVER_PORT` + `ADMIN_CORS_ALLOWED_ORIGINS` (admin origins); REMOVE the admin origin from the consumer `CORS_ALLOWED_ORIGINS`
- [ ] 3.6 `make lint` / kustomize render green; `pulumi preview` clean for dev and prod

## 4. Frontend — admin client base URL

- [ ] 4.1 Add the admin API base URL (`api.admin.{env}`) to the admin per-host runtime config (`/config.json`) and its env ConfigMaps
- [ ] 4.2 Point the admin `ConcertModerationService` client at the admin API base URL from runtime config; leave the consumer client unchanged
- [ ] 4.3 Tests + `make check` green

## 5. Ship to production (coordinated cutover)

- [ ] 5.1 Merge + apply cloud-provisioning so `api.admin.{env}` is live (Service + route + cert + DNS + health) BEFORE the frontend flips
- [ ] 5.2 Release backend so the admin server is live (per design, optionally still dual-serving on the consumer server during the window)
- [ ] 5.3 Release frontend so the admin console targets `api.admin`; verify approve/reject works end-to-end against the admin host in prod
- [ ] 5.4 Follow-up: remove `ConcertModerationService` from the consumer server (if dual-served) and drop the admin origin from the consumer CORS; confirm the consumer API no longer serves admin RPCs
- [ ] 5.5 Verify a non-admin token is rejected at the admin host, and that the consumer host returns not-found/unimplemented for the moderation procedures
