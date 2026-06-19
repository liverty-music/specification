## Why

The admin moderation RPCs (`ConcertModerationService`) are served by the **same** Connect server, port, CORS allowlist, authn middleware, and interceptor chain as the consumer-facing RPCs. The only thing separating the admin surface from the public one is a per-method `auth.RequireRole(ctx, "admin")` call inside each handler method. This has two problems:

- **Authorization is easy to get wrong.** Every new admin method must remember `RequireRole`; a single omission silently exposes an admin operation to any authenticated consumer (a fan's valid JWT already passes the shared authn — only the in-handler check stops them). There is no structural guarantee.
- **The admin surface shares the consumer's blast radius and governance.** Admin and consumer traffic share one public host, one CORS list (the admin origin was merged into the consumer backend's `CORS_ALLOWED_ORIGINS`), one rate limiter, and one route — so the admin API cannot be governed (origins, limits, and a future IAP/Cloud Armor layer) independently of the public API.

The codebase already runs multiple `http.Server` listeners on separate ports (the webhook and health servers), so a dedicated admin RPC server is consistent with the established topology — and symmetric with `admin-console-hosting`, which already isolates the admin **frontend** onto its own image, host, and config.

## What Changes

- **Add a dedicated admin Connect server** (a second listener in the same backend binary, on its own port) that serves **only** admin-scoped services. The consumer Connect server **stops serving** `ConcertModerationService`.
- **Enforce admin authorization at the server boundary, not per method.** Every RPC on the admin server passes through a fixed admin-authorization interceptor that requires the `admin` role; non-admin (and unauthenticated) callers are rejected with `PERMISSION_DENIED` before any handler runs. The per-method `RequireRole` calls are removed — the admin server cannot host a non-admin-gated RPC by construction.
- **Give the admin server its own CORS allowlist** (admin origins only). The consumer server's `CORS_ALLOWED_ORIGINS` no longer needs the admin origin.
- **Expose the admin server on its own ingress host** — `api.admin.{env-base-domain}` (mirroring `admin.{env-base-domain}` + the consumer `api.{env-base-domain}`) — via its own Service + HTTPRoute + cert + DNS + health-check, leaving the consumer routing untouched.
- **Point the admin console's RPC client at the admin host** via its per-host runtime config; the consumer SPA continues to call the consumer API.

This is purely a relocation + hardening of an **existing** service. `ConcertModerationService` and its proto are unchanged — there is **no specification/proto/BSR change**.

## Capabilities

### New Capabilities
- `admin-rpc-server`: A dedicated backend Connect server for admin-scoped RPCs — a separate in-process listener on its own port, serving only admin services, with boundary-level admin-role authorization (replacing per-method checks), an admin-only CORS allowlist, its own ingress host/Service/cert/DNS/health, and the consumer server's exclusion of admin services. The admin console's RPC client resolves the admin API host from its runtime config.

## Impact

- **backend**: Build a second `ConnectServer` (admin) in DI alongside the consumer one, sharing a server/interceptor factory to avoid drift; register both with the shutdown Drain phase. Add the admin-authorization interceptor as a fixed layer on the admin server and remove the per-method `RequireRole` from `ConcertModerationHandler`. Move `ConcertModerationService` registration from the consumer mux to the admin mux. New config: admin server port + admin CORS origins; drop the admin origin from the consumer CORS list.
- **cloud-provisioning**: Expose a second container port on the backend Deployment; add an admin backend `Service` (h2c, gRPC health), an `HTTPRoute` for `api.admin.{env}` on the shared external gateway, certmap + Cloud DNS entries, and a `HealthCheckPolicy`. Add the admin CORS origins + admin port to the backend config/env; remove the admin origin from the consumer `CORS_ALLOWED_ORIGINS`.
- **frontend**: The admin app's `ConcertModerationService` client base URL comes from the admin runtime config (`api.admin.{env}`) rather than the shared consumer API base. Consumer client unchanged.
- **specification**: None — no proto change.
- **Out of scope (later)**: putting Google IAP / Cloud Armor in front of the `api.admin` route (the split *enables* this defense-in-depth, but the IAP-vs-Zitadel interplay is a separate change); migrating other future admin services (this change establishes the server; later admin services simply register on the admin mux).
