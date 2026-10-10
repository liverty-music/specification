## Context

See proposal.md - Why. Current hosting, as of backend `a656ceb`, cloud-provisioning and frontend `main` on 2026-10-09:

```
 staff phone                                  operator browser
 organizer.liverty-music.app/reception#tok   organizer.liverty-music.app/*
       |   same origin, same app bundle             |  OIDC tokens in localStorage
       v                                            v
 api.organizer.liverty-music.app ------> organizer-console-api (image: server, x2)
                                          port 8091: Organizer, Concert, Lottery,
                                          PayoutOnboarding, ReceptionLink,
                                          + ReceptionService (public procedures)
                                                   |
                                          Cloud SQL user organizer-console-api@...iam
```

- **One binary, one listener per surface.** `cmd/api/main.go` starts the fan, admin, organizer and webhook servers in every pod. A workload is isolated by the port its Service exposes, its Kubernetes service account (Workload Identity → its own GSA) and that GSA's Cloud SQL IAM user, whose grants bound what the process can do in the database. `split-admin-rpc-server`, `organizer-rpc-server` and `organizer-console` established this pattern; this change applies it a third time.
- **Reception today.** `OrganizerPublicProcedures()` (`internal/infrastructure/auth/public_procedures.go`) lists Open and Admit; the organizer server's auth func, `OrgScopedInterceptor` and the unknown-token interceptor use it (`internal/di/provider.go:425-428, 598-663`). The unknown-token throttle is in-memory per process (`ratelimit/unknown_token.go`).
- **Reception grants.** `20261008010000_grant_organizer_console_api_reception.sql` and `20261008020000_restrict_...` give `organizer-console-api` the reception writes (`reception_links` UPDATE of the bind columns, `tickets.admitted_at`, INSERT on `admissions` and `rejected_scans`) next to the console writes; `migration_grants_integration_test.go` pins the set.
- **Frontend.** The organizer console is a separate entry (`organizer.html`, `Dockerfile.organizer`, `Caddyfile.organizer`) with its own web workload, but not a separate build: one `vite build` emits every entry (`vite.config.ts:48-58`), isolation is per chunk (`assets/organizer/`, checked by `verify:bundle-isolation`), and `Dockerfile.organizer` copies all of `dist/assets/`, so the organizer image also serves the consumer and admin chunks. The reception route (`organizer/reception/*`, `organizer/services/reception-*.ts`) is registered in `organizer/organizer-shell/organizer-shell.ts` with `auth: false` and calls the organizer API base URL without a token. Console tokens are kept in `localStorage` (`shared/services/auth-service.ts:30`).

## Goals / Non-Goals

**Goals:**
- The reception page and the console never share an origin, a bundle or browser storage.
- The organizer API serves only signed-in operators; no procedure on it is public.
- The reception API runs as its own workload whose database role can do the reception reads and writes and nothing else.

**Non-Goals:**
- Changing the reception protocol, the proto or any screen behavior.
- An edge rate limit (Cloud Armor) in front of the reception API; the process-level unknown-token throttle stays the protection, as today.
- A separate binary for reception.

## Decisions

### D1 — A reception listener in the same binary, exposed only by `reception-api`

The backend gains a fifth server, the reception server, on its own port (`RECEPTION_SERVER_PORT`, default 8092) with its own CORS allowlist (`RECEPTION_CORS_ALLOWED_ORIGINS`). It mounts only `ReceptionService`, uses an auth func whose public procedures are Open and Admit (renamed `ReceptionPublicProcedures()`), and carries the unknown-token interceptor. A new `reception-api` Deployment exposes only that port; `organizer-console-api` keeps exposing only 8091.

- *Why not a separate binary*: the fan, admin and organizer surfaces already isolate by listener + service account + DB role; a second binary adds a build, an image and a release path for no extra isolation, since the database role is what bounds the process.
- *Why not only a new hostname routed to the existing pods*: it would split the entry point but keep the shared process and database role, which is the part that bends the console's privileges.

### D2 — The organizer server has no public procedures

`ReceptionService` is removed from the organizer handlers and `OrganizerPublicProcedures()` disappears; the organizer server's auth func and `OrgScopedInterceptor` take no exemptions, and the unknown-token interceptor leaves the organizer server. `ReceptionLinkService` (Issue, List, Revoke) stays on the organizer server: it is an operator action in the console.

### D3 — `reception-api` database role, reception-only

A new GSA `reception-api` with Workload Identity on `ns/backend/sa/reception-api`, a Cloud SQL IAM user for it, and the same operational project roles the shared binary needs to boot as `organizer-console-api` (log, metric, trace writer, Cloud SQL client and instance user, service usage consumer), without the storage signing binding and the provisioner key. `roles/aiplatform.user` is mirrored only if the binary fails to boot without it; this is checked when the workload first starts.

A grant migration gives `reception-api@%.iam`:
- SELECT on the tables the reception path reads (reception links, events and what the reception window reads, wallet public keys, tickets, admissions);
- UPDATE on the `reception_links` bind columns (`status`, `bound_public_key`, `bound_at`, `token`), which also covers the row locks Open and Admit take;
- UPDATE (`admitted_at`) on `tickets`;
- INSERT on `admissions` and `rejected_scans`.

The same migration revokes from `organizer-console-api` the writes only reception performed: the bind columns of `reception_links` (keeping INSERT and UPDATE of `status`, `token` and `revoked_at` for Issue and Revoke), `tickets.admitted_at`, and INSERT on `admissions` and `rejected_scans`. The exact SELECT set is pinned by extending `migration_grants_integration_test.go` with a `receptionWrites` list next to `organizerWrites`, and the reception integration test runs against a database where the reception path connects as the new role, so a missing grant fails in CI rather than at the door.

- *Alternative*: keep reception on the organizer role and widen it. Rejected: it is the co-location this change removes.

### D4 — Reception web as its own build and origin

The reception screen becomes a lightweight web app built on its own, in the frontend repository:

- **Its own build.** A dedicated Vite configuration (`vite.reception.config.ts`) with `reception.html` as its only input and its own output directory (`dist-reception/`). It is not an input of the main build. Shared code (the QR decoder and its worker, the call-signing helpers, design tokens) is imported from source, so the output holds only what the reception screen reaches.
- **Its own image.** `Dockerfile.reception` copies only the reception output and its own `config.json` (`apiBaseUrl` = `api.reception.liverty-music.app`); `Caddyfile.reception` serves it from a `reception-web` workload at `reception.liverty-music.app`.
- **Checked on every build.** A dependency-cruiser rule forbids `reception/` from importing the console, the consumer app or `shared/services/auth-service`, and a post-build check fails when the reception output contains the OIDC client or console code. The output size is reported by the build.
- The route moves out of `organizer/` into `reception/`; the reception client, transport and key store move with it. The entry has no OIDC client and no sign-in code, so it cannot touch console tokens even by mistake. The reception guide (`ticket-wallet-and-checkin` 7.2) is a static page of this build.

- *Alternative*: another input of the main build, packaged like the organizer image. Rejected: the image would ship every entry's assets on the reception origin.
- *Alternative*: a separate web repository. Rejected for now: the reception code shares the decoder, the signing helpers and the design system; a separate build already gives a separate bundle, image and origin.
- The organizer and admin images shipping all entries' assets is an existing issue, tracked in liverty-music/frontend#700 and not changed here.
- The link URL becomes `https://reception.liverty-music.app/#<token>` (the token stays in the fragment, never sent to a server). The reception-links screen builds it from a configured reception origin.

### D5 — DNS, certificates and routes follow the existing service list

`reception` and `api.reception` are added to the service list in `src/gcp/components/network.ts`, which already creates the Cloudflare records and the gateway certificates for `api.organizer` and `organizer`. Two HTTPRoutes on the shared external gateway point at `reception-api-svc` and `reception-web-svc`.

## Risks / Trade-offs

- **[Risk] A grant missing on the new role surfaces only at the door.** → The reception integration test runs as the `reception-api` role (D3), and the production E2E of `ticket-wallet-and-checkin` (7.3) runs after this change.
- **[Risk] The unknown-token throttle counts per pod.** → Same as today; `reception-api` starts with 2 replicas, so a client gets at most twice the limit. An edge limit is a non-goal.
- **[Trade-off] Two more workloads.** → Small static and API pods; the cost is accepted for the isolation. Replicas can drop to 1 outside events once usage is known.
- **[Risk] Links issued before the switch stop working.** → None is used by a live event; the runbook says to reissue.

## Migration Plan

The product has no live events using reception, so this is a single cut, not a dual-serving period:

1. cloud-provisioning (`pulumi up`): GSA, Workload Identity, Cloud SQL IAM user, DNS and certificates for `reception` and `api.reception`.
2. backend: the reception server and the grant migration (Atlas applies it before the backend rollout); reception leaves the organizer server in the same release.
3. cloud-provisioning (k8s): `reception-api` and `reception-web` workloads and routes; the backend config for the reception port and CORS.
4. frontend: the reception entry, image and release; the console without the reception route; reception-links URLs on the new origin.
5. Verify on production: Open and Admit through `api.reception` from `reception.liverty-music.app`; a call to `api.organizer` for ReceptionService fails with Unauthenticated; the console role has no reception writes (`\dp` read-only check).

Rollback: revert the backend and frontend releases; the grant migration's revocations are re-granted by a follow-up migration if the old hosting must come back. Links issued on the new origin are reissued.
