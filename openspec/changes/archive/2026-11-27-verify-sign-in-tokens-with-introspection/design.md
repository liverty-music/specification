## Context

See proposal.md. Facts (2026-11-27):

- `auth.JWTValidator.ValidateToken` checks the signature against the issuer's public keys, expiry, issuer, `sub` and `email`. Only the organizer API checks `aud` (`OrgScopedInterceptor`).
- Expired prod test tokens: access and ID token carry the same `aud`, `email` and roles, and both have header `typ: JWT`. The access token has `jti` and `nbf`; the ID token has `at_hash`, `sid`, `auth_time`, `amr` and lives 12 hours. The apps send access tokens.
- ZITADEL emits no `typ: at+jwt` (RFC 9068) and documents no way to tell the two apart locally; it documents introspection (RFC 7662) for APIs.
- The backend reaches ZITADEL at `https://auth.liverty-music.app`, which resolves to the external load balancer: key fetches arrive from node public IPs. The login app already calls `http://zitadel-api:80` with the public host in headers; ZITADEL resolves the instance from `x-zitadel-instance-host` or `x-zitadel-public-host` (values.yaml `InstanceHostHeaders`).
- ZITADEL serves one replica; measured inside it, simple calls take tens to hundreds of ms (`/oauth/v2/keys` p50 146 ms, p95 223 ms over 7 days of sparse traffic). Introspection has not been measured.

### Measurement (task 2.1, prod, 2026-11-27)

The backend's own clients ran on a laptop against `zitadel-api` through a port-forward, with `ZITADEL_INTERNAL_URL` pointing at it.

- Instance resolution: keys, discovery, token, introspection and the gRPC call (`GetUserByID` of a throwaway fan) work at the internal address with the headers; discovery still answers the public issuer.
- Fan app and organizer console: the access token is active, the ID token is not. A token asked about with another project's key is not active. The admin console key is accepted; no admin console token was asked about (Google sign-in only).
- A fan deleted in the app: its access token, with 28 minutes left, and its ID token are not active one second after the deletion.
- Introspection through the port-forward: p50 250 ms, p95 341 ms (100 asks). The port-forward alone costs about as much: 200 paired asks gave `/debug/healthz` p50 235 ms, p95 271 ms and introspection p50 264 ms, p95 329 ms, so ZITADEL spends about 30 ms (p50) to 60 ms (p95) on an introspection. The p95 inside the cluster is measured after the release (task 6.3). The owner decided on 2026-11-27 to go on although the measured p95 exceeds 300 ms.

### Production check (task 6.3, 2026-11-27, v1.155.0 and v1.155.1)

- Signed-in calls succeed in the fan app (`delete-my-account` E2E, 2 passed), the organizer API and the admin console. Since the release no backend request has reached `auth.liverty-music.app` through the load balancer.
- The two identities removed after the release are forgotten, and `workflow.needs_admin` is 0. One row older than the release remains in `deleted_user_identities`: `401420940820349201`, removed under the old code at 06:40.
- Introspection in the cluster: the 5 asks that reached Cloud Monitoring all took less than 50 ms. Only 5 arrived because every backend Pod writes the same metric series (the telemetry resource names no instance), so Cloud Monitoring drops most points. This predates the change.

### Production check (task 7.1, 2026-11-27)

- Each API refuses its own app's ID token with Unauthenticated (fan, organizer, admin console) and another app's access token with PermissionDenied (admin with a fan or organizer token, fan and organizer with each other's). A call with a garbage token or none is Unauthenticated, a public call carrying an ID token succeeds, and each app's own calls succeed. The admin console case was run by the owner in the console's DevTools (ID token 401, access token 200).

Two unchanged scenarios of the modified requirement are about the cluster network, which no automated test reaches. Read in prod on 2026-11-27 after the identity port was renamed:

@spec-manual components/infrastructure/backend/process/identity-provider-credentials "Process with no access" -- NetworkPolicy `identity-ingress` admits only workflow-worker (9100), admin-console-api (9101) and fan-api with its candidate (9102), besides the health port
@spec-manual components/infrastructure/backend/process/identity-provider-credentials "Request from outside the cluster" -- Service `identity` is ClusterIP, no HTTPRoute names it and the cluster has no Ingress

## Goals / Non-Goals

**Goals:** only an access token for the API's own app signs a call in; no backend call to ZITADEL leaves the cluster network.

**Non-Goals:** the reception API (device calls, no token); webhook verification and the fresh sign-in proof of account deletion (an ID token by design), which keep local key verification; scaling ZITADEL.

## Decisions

- **Local checks first, then introspection.** In order: signature, issuer and expiry as today; `aud` contains the API's project id, else PermissionDenied (what the organizer API answers today); then introspection, `active: false` → Unauthenticated. Claims (`sub`, `email`, `name`, `email_verified`, roles) keep being read from the verified JWT, so nothing depends on which claims introspection returns. Garbage, foreign and expired tokens never reach ZITADEL, so they cannot be used to load it. Alternatives: local rules only (`jti` required), rejected because it rests on undocumented claim differences and ignores revocation; claims from the introspection answer, rejected as an unneeded second source.
- **Cache active answers for 60 seconds**, keyed by the SHA-256 of the token, expiring 60 seconds after the ask was sent and no later than the token, bounded in entries, with concurrent asks for one token joined (`singleflight`). Inactive answers and errors are not cached. One ask has a 5-second deadline: the authentication layer runs before the server's handler timeout, so nothing else bounds it when the sign-in service accepts a connection and does not answer. RFC 7662 section 4 allows caching at the price of liveness.
- **Errors.** A transport failure or server error of introspection is Unavailable; the authentication layer keeps codes instead of turning every failure into Unauthenticated. A refused client assertion is Internal: it is our configuration.
- **One API application and private-key JWT per audience project** (product, admin-console, organizer-console; the organizer's existing BASIC `backend-api` application changes method). Pulumi creates application and `ApplicationKey`; the key goes to Secret Manager with ESO-only access and is mounted only into that API's Deployment (`fan-api` and its candidate share one). ZITADEL introspects only tokens whose `aud` names the asking application's project, which repeats the audience check.
- **Cluster-internal calls.** A required setting (outside local) names the internal base URL `http://zitadel-api.zitadel.svc.cluster.local:80`; the issuer stays the public URL for `iss`, JWT assertion audiences and links. HTTP calls (keys, token, introspection) and the gRPC clients of the identity service send `x-zitadel-instance-host` and `x-zitadel-public-host`. The traffic is plain HTTP inside the cluster, as the login app's and the gateway's already is.
- **Forgetting a removed identity.** `delete-user` starts a `forget-removed-identity` run delayed 90 seconds after `remove-identity` (a request is admitted at latest 60 seconds after an ask that preceded the removal, and its handler is bounded at 30 seconds), so `Delete` still ends its wait at once; the new start is under `Patched`. `User.ForgetRemovedIdentity` deletes the row of `deleted_user_identities`. No condition is checked before the write, so no lock is needed: after 90 seconds no request of that identity is accepted or running. This rests on ZITADEL reporting a removed identity's unexpired access token inactive, which task 2.1 verifies before any code relies on it.
- **Leftover names.** `IDENTITY_EVENT_CONSUMER_PORT` becomes `IDENTITY_WORKFLOW_WORKER_PORT` (unset in every manifest), the identity Service port `event-consumer` becomes `workflow-worker` (callers use the number), and the `fan-passkey-recovery` machine user's description names the identity service.

## Risks / Trade-offs

- [ZITADEL down or wedged] → after at most 60 seconds every signed-in call fails with Unavailable (today it keeps working until tokens expire). Accepted: no users yet; the `zitadel-hang` runbook restarts it. Add that effect to the runbook.
- [Introspection is slow] → measured first (task 2.1) and in prod. A p95 above 300 ms on a cache miss stops the work for the owner's decision.
- [The internal headers do not work for introspection, token, key or gRPC calls] → each is tried through a port-forward in the measurement, before any code depends on them.
- [A removed identity's token is accepted from a cache] → at most 60 seconds, and Create stays refused for 90.

## Migration Plan

1. cloud-provisioning Pulumi: applications, keys, secrets, description. The owner runs the prod `pulumi up`.
2. Measure introspection and the internal headers.
3. cloud-provisioning manifests: settings, secret mounts, port name. The running backend ignores them.
4. Backend release.

Rollback: revert the backend release; the manifests and applications stay. The older code accepts a removed identity's ID token for up to 12 hours, so before reverting, read the provider user ids of the `forget-removed-identity` runs of the last 12 hours from their recorded inputs and insert them into `deleted_user_identities` again (a one-time write).
