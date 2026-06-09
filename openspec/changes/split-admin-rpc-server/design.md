# Design: dedicated admin RPC server

## Context

Today everything is one Connect server on one port:

```
:Port ── CORS(consumer+admin origins merged) ── authn.Middleware (shared issuer)
   └─ one interceptor chain ─ one protectedMux
        ├─ User / Artist / Concert / Ticket … (consumer)
        └─ ConcertModerationService  ← only guarded by per-method RequireRole("admin")
```

A consumer fan's JWT is a valid token at this port (same Zitadel issuer), so it passes `authn`; only the in-handler `RequireRole` stops it. Precedent for splitting exists: `webhook` and `health` already run as separate `http.Server` listeners (`internal/infrastructure/server/{webhook,health}.go`).

## Goals

- An admin RPC cannot be served without admin authorization — make it structural, not per-method discipline.
- Govern the admin surface (origins, limits, host, future IAP) independently of the public API.
- Keep it one binary (no new deployment) — the isolation is network/governance, not process.
- Zero proto change; `ConcertModerationService` only moves.

## Decision 1 — Second in-process listener, not a new binary

Add a second `ConnectServer` (the *admin server*) bound to its own port in the **same** backend binary, built by the same factory as the consumer server. One Deployment exposes two container ports.

```
backend Pod (one binary)
 ├─ :PORT        consumer ConnectServer ── Service: server      ── HTTPRoute api.{env}
 └─ :ADMIN_PORT  admin ConnectServer    ── Service: admin-server ── HTTPRoute api.admin.{env}
```

Why not a separate binary (Opt 3)? The admin surface is low-traffic and shares the same domain logic/deps; a separate deployment buys independent scaling/blast-radius we don't need yet, at real CI/release cost. Two listeners in one binary give the governance split (host, CORS, authz boundary) cheaply. Opt 3 stays open as a later step if admin ever needs independent scaling.

## Decision 2 — Authorization at the server boundary

The admin server applies a **fixed admin-authorization interceptor** to every handler, as an inner layer of the shared chain (after the claims bridge, so it sees the bridged claims):

```
admin server chain: tracing → ratelimit → accesslog → error → recover → claimsBridge → REQUIRE-ADMIN → validation
```

Because the admin server hosts **only** admin services and the interceptor is server-wide, it is impossible to register an un-gated admin RPC. The per-method `auth.RequireRole(ctx, "admin")` calls are deleted from `ConcertModerationHandler` — the handler becomes pure mapping again.

Defense in depth (kept, not required): the admin server still runs the same `authn.Middleware` (valid-JWT, default-deny). A consumer token passes authn but fails REQUIRE-ADMIN. Optionally the admin `authFunc` could additionally pin the admin org id, but the role interceptor is the authoritative gate; pinning the org is a redundant nicety we can add without changing this contract.

### Why not just keep per-method checks (Opt 1)?

Opt 1 (an interceptor on the consumer server scoped to admin handlers) centralizes authz but still shares the port/CORS/host/limits — it does not give the governance split (independent origins, host, future IAP) that motivated this change. Opt 2 gets both the authz boundary **and** the governance split.

## Decision 3 — Separate CORS, shared everything-else via a factory

The admin server gets its own allowlist (`ADMIN_CORS_ALLOWED_ORIGINS` = `https://admin.{env}` + localhost in dev). The consumer `CORS_ALLOWED_ORIGINS` drops the admin origin that was merged in earlier.

To prevent the two interceptor chains from drifting, both servers are built from **one factory** that takes (port, CORS origins, extra interceptors, handler set). The consumer call passes no extra authz interceptor; the admin call passes the REQUIRE-ADMIN interceptor. The `interceptor-chain-ordering` invariants hold for both.

## Decision 4 — Ingress host `api.admin.{env}`

Naming mirrors the existing trio: consumer app `app`/root, consumer API `api.{env}`, admin app `admin.{env}` → admin API **`api.admin.{env}`**. It gets its own `Service` (ClusterIP, h2c, gRPC health), `HTTPRoute` on the shared external gateway, certmap + Cloud DNS, and `HealthCheckPolicy` — symmetric with the consumer backend exposure and with `admin-console-hosting`'s frontend host. Consumer routing is untouched.

The admin SPA runs in the developer's browser, so `api.admin.{env}` is a **public** host (not ClusterIP-only). The win is a *separately governed* public surface — its own CORS, its own route to hang IAP/Cloud Armor on later — not internal-only reachability.

## Decision 5 — Frontend resolves the admin API host from runtime config

The admin console already loads a per-host `/config.json` (`admin-console-hosting`). It gains the admin API base URL (`api.admin.{env}`); the admin `ConcertModerationService` client uses it. The consumer SPA keeps calling `api.{env}`. No code path conditionally rewrites hosts — each app reads its own config.

## Migration / sequencing

This moves a live, prod-shipped service. To avoid a window where the admin console can't reach moderation:
1. Ship backend serving `ConcertModerationService` on **both** the consumer and admin servers temporarily — OR sequence host+frontend so the admin client flips only after `api.admin` is live.
2. Preferred: stand up `api.admin` (cloud-provisioning) → release backend (admin server live, still also on consumer server) → flip the admin frontend config to `api.admin` → remove the service from the consumer server in a follow-up. Decide at apply time whether the brief dual-serve is worth avoiding a flip-day gap.

## Open questions

- **Host name**: `api.admin.{env}` vs `admin-api.{env}`? (proposal assumes `api.admin.{env}`.)
- **Dual-serve during cutover** vs a coordinated single-flip — pick per risk tolerance (admin is internal/low-traffic, so a short coordinated flip is likely fine).
- **Org pinning in the admin authFunc** — add now or leave the role interceptor as the sole gate?
