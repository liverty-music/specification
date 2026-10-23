## Context

See proposal.md - Why. Facts this design rests on (checked on 2026-10-23):

- **Where the identity-provider (ZITADEL) clients are built today** (`backend/internal/di`):
  - The event consumer builds three, behind the entity interfaces:
    - `EmailVerifier` (`SendVerification` at sign-up through `event.NewUserConsumer`, `ResendVerification` through `UserUseCase.ReissueEmailVerification`), with the `backend-app` key (`consumer.go:238-245`);
    - `PasskeyRegistrationLinkIssuer`, with the `fan-passkey-recovery` key (`consumer.go:453`).
  - The admin console API builds two:
    - `IdentityRemover.DeleteIdentity` and an `EmailVerifier`, with `backend-app` (`provider.go:126-145`). The admin's `EmailVerifier` appears unused: the only resend caller is the consumer's `ReissueEmailVerification`, `user_uc.go:550`.
    - `OrganizationRepository` (`Create`, `GetByName`, `Provision`, `DeactivateIdentities`, `Delete`), with `organizer-provisioner` (`provider.go:305-323`, `cfg.ProvisionsOrganizers()`).
  - Every client shares the JWT-profile token source in `infrastructure/zitadel/token_source.go`.
- **Keys and pods in cloud-provisioning**: the keys reach `event-consumer` through `event-consumer-secrets` and `admin-console-api` through its own secrets. Pods are labelled `app=<workload>` (kustomize `labels`), run as KSA `backend-app` (Workload Identity) and expose gRPC health on port 8080.
- **The cluster** has no NetworkPolicy today (`kubectl get networkpolicies -A`: none). Autopilot runs Dataplane V2, which enforces NetworkPolicy (`src/gcp/components/kubernetes.ts:822`).
- **Images**: the backend images are `gcr.io/distroless/static:nonroot` (`Dockerfile:56`). The dev push path builds eight images with Bake (`deploy.yml` `IMAGES`), and the release copies them to prod and pins them in cloud-provisioning.
- **The `event-consumer`** is pinned to one replica in prod (`overlays/prod/kustomization.yaml:285-305`).
- **Checked during exploration** (zitadel v4.19.5):
  - The user v2 RPCs declare only `authenticated` at the interceptor and check `user.write`, `user.delete` or `user.passkey.write` in the command. So every management call needs one of the three keys, and a key's role is its whole privilege.
  - The BSR module `buf.build/liverty-music/schema` is public.

## Goals / Non-Goals

**Goals:**
- One process holds the identity-provider keys. It is not reachable from outside the cluster. Each caller reaches only the operations it uses.
- No change in what a fan, member or admin sees: the entity operations keep their promises and errors.

**Non-Goals:**
- `VerifyEmail` and the fan-API caller. Change #1228 adds them on a third listener.
- Service-to-service tokens (D3). Mutual TLS or a service mesh.
- Splitting the three keys into narrower ZITADEL roles. ZITADEL role mappings can only be replaced as a whole (`fan-passkey-recovery-and-management` D2).

## Decisions

### D1. A separate `identity` binary and workload, with no database

The new binary `cmd/identity` wires only the four ZITADEL clients, their token sources and the internal listeners. It has no database, no NATS and no public listener. It ships as image `backend/identity` (distroless, like the others) and runs as Deployment `identity` with one replica.

Alternatives:

| Option | Rejected because |
|---|---|
| Run the API binary with `WORKLOAD=identity` | That binary wires the database and starts the fan, admin, organizer and reception listeners in every pod. The identity pod would load database credentials and code it never uses. |
| An RPC listener on the event consumer | The consumer keeps both keys while it processes external data (Gemini results, official-site pages). The risk the proposal removes would stay, and the consumer would take two roles. |
| A role-less key on the fan API for #1228 | It still puts an identity-provider credential on an internet-facing pod, and leaves the consumer and admin keys as they are. |

### D2. Internal API: `liverty_music.rpc.internal.<entity>.v1`, entity-named services

Packages name the caller (`rpc-design` skill: "Packages name the caller"). `internal` is a new caller, meaning a backend workload inside the cluster. Services are named after the entity they act on, not after the hosting workload, so a later move or split of the identity workload renames nothing.

| Today (entity interface) | Internal RPC | Caller |
|---|---|---|
| `EmailVerifier.SendVerification` | `rpc.internal.user.v1.UserService.SendEmailVerification` | event consumer |
| `EmailVerifier.ResendVerification` | `UserService.ResendEmailVerification` | event consumer |
| `PasskeyRegistrationLinkIssuer` (verified email + link) | `UserService.IssuePasskeyRegistrationLink` | event consumer |
| `IdentityRemover.DeleteIdentity` | `UserService.DeleteIdentity` | admin console API |
| `OrganizationRepository.Create`, `GetByName`, `Provision`, `DeactivateIdentities`, `Delete` | `rpc.internal.organization.v1.OrganizationService.*` (names fixed against the `rpc-design` skill in task 1.1) | admin console API |

Requests name the provider user id or provider organization id, because the caller is a workload, not the subject. Errors keep today's codes: NotFound, FailedPrecondition (unverified email), Unavailable. The caller's client maps them back to the same `apperr` codes, so the usecases do not change.

The protos go on BSR with the rest. The module is public, which is acceptable because no protection depends on hiding the names (D3).

Alternative: protos only inside the backend repo, which avoids a Release. Rejected: the specification repo is the single place for contracts, and buf lint, breaking checks and `rpc-design` review apply only there.

### D3. Per-caller listeners, a procedure allowlist on each, and NetworkPolicy per port

The identity process serves one Connect listener per caller. Each listener has an interceptor that allows a fixed set of procedures and answers PermissionDenied to anything else, so the default is deny.

| Port | Caller (`app=`) | Allowed procedures |
|---|---|---|
| 9100 | `event-consumer` | `SendEmailVerification`, `ResendEmailVerification`, `IssuePasskeyRegistrationLink` |
| 9101 | `admin-console-api` | `DeleteIdentity`, the `OrganizationService` procedures |
| 8080 | kubelet | gRPC health only |

NetworkPolicy `identity-ingress` selects `app=identity` and allows:
- TCP 9100 from `app=event-consumer`;
- TCP 9101 from `app=admin-console-api`;
- 8080 for the probes.

All other ingress is denied. Service `identity` is ClusterIP with no Gateway route.

The threat analysis from exploration:
- **Distroless** leaves no shell or tools after a compromise.
- **The NetworkPolicy** stops lateral movement from any other pod.
- **The per-listener allowlist** means a fully compromised caller can still use only its own procedures.
- **SSRF** in the consumer (it fetches external pages) is mostly blunted: Connect procedures need a POST with a body unless marked side-effect-free, and none here is.

Rejected for now: verifying a caller token (Workload Identity Google ID token, audience `identity`). It adds an interceptor on both sides. Its extra protection covers only SSRF that can send a POST, and a misconfigured label or route. Revisit when a caller can be made to send arbitrary POSTs or when callers multiply.

### D4. Callers keep their entity interfaces; a Connect client replaces the Zitadel client

New package `backend/internal/infrastructure/identity` implements `EmailVerifier`, `PasskeyRegistrationLinkIssuer`, `IdentityRemover` and `OrganizationRepository` over the internal RPCs. It uses h2c inside the cluster.

The Zitadel implementations move behind the identity binary unchanged.

`IDENTITY_SERVICE_URL` selects the client on the consumer and the admin console API:
- set → the identity client;
- unset in local → the current no-op and unavailable fallbacks;
- unset outside local → the current direct Zitadel client.

The last case exists only for the migration (Migration Plan step 5 removes it).

### D5. Keys: one `identity-secrets` ExternalSecret, mounted only on `identity`

The GSM secrets keep their names:
- `zitadel-machine-key-for-backend-app`
- `zitadel-machine-key-for-fan-passkey-recovery`
- `zitadel-machine-key-for-organizer-provisioner`

ESO syncs them into `identity-secrets`. The three `*_PATH` variables move to the identity config. `event-consumer` and `admin-console-api` lose the mounts and the variables, and gain `IDENTITY_SERVICE_URL`.

### D6. Availability: one replica; callers keep their retry paths

The identity service is on the path of sign-up verification, passkey recovery, fan deletion and Organizer provisioning.
- With one replica, a restart makes those calls fail with Unavailable for seconds.
- The consumer's handlers already treat Unavailable as retryable (JetStream redelivery).
- The admin console shows the failure and the admin retries.

This is accepted at current scale, with no users.

ZITADEL is reached on first use. The token source is lazy, so the process starts and reports ready without it (spec `health-probes`).

### D7. Pipeline

`identity` joins:
- `docker-bake.hcl` and the `IMAGES` list in `deploy.yml`;
- the release copy matrix;
- `dispatch-prod-pin`;
- the prod overlay image pin.

The Dockerfile gains an `identity` stage like `consumer`.

## Risks / Trade-offs

- **[Risk]** The first NetworkPolicy in the cluster could block the probes or a caller. → Render it with `kubectl kustomize` in CI. In prod, check that the probes pass and that a sign-up verification, a passkey recovery and an admin action succeed. Dataplane V2 allows node-to-pod probe traffic; this is verified in prod, not assumed.
- **[Risk]** Any pod that can be created with label `app=event-consumer` passes the NetworkPolicy. → Creating pods in the `backend` namespace already allows mounting the secrets, so this adds no new privilege. Caller tokens (D3) would close it.
- **[Risk]** `IssuePasskeyRegistrationLink` returns the one-time code to the consumer over in-cluster h2c without TLS. → It never leaves the cluster network, it is not logged, and the code is single-use and expires in 1 h. Dataplane V2 transparent encryption could be enabled later.
- **[Trade-off]** One more always-on pod. Today's pods request about `10m` CPU and `64Mi` memory, and the cost of an Autopilot spot pod at that size is not measured.
- **[Trade-off]** The identity service is a single point for the identity-provider operations (D6).

## Migration Plan

1. **specification**: the protos, the `rpc-design` rule, a Release and BSR generation.
2. **backend PR 1**: the `identity` binary and image, the identity client, and the `IDENTITY_SERVICE_URL` switch with the direct client kept as the fallback (D4). Release it; the pipeline produces `backend/identity`.
3. **cloud-provisioning PR 1**:
   - add `identity-secrets`, Deployment `identity`, Service `identity` and NetworkPolicy `identity-ingress`, pinned to that release;
   - set `IDENTITY_SERVICE_URL` on `event-consumer` and `admin-console-api`, which keep their keys for now.
   - Merging starts the identity service. The callers move to it on their next rollout.
4. **Verify in prod**:
   - the probes pass;
   - the consumer and admin calls go through identity, seen in identity's logs;
   - a pod without an allowed label cannot connect to 9100 or 9101 (an ephemeral `kubectl run` client).
5. **backend PR 2** removes the direct-client fallback and the key path settings from the consumer and admin configs. **cloud-provisioning PR 2**, after that release, unmounts the keys from `event-consumer` and `admin-console-api`.

**Rollback**: before step 5, unset `IDENTITY_SERVICE_URL`. The callers return to their direct clients with the keys still mounted.

## Open Questions

- Exact `OrganizationService` method names under the `rpc-design` rules, e.g. how `GetByName` reads. This is settled in task 1.1 and does not change the approach.
