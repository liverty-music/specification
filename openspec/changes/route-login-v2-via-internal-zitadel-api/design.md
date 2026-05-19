## Context

Login V2 UI in prod hangs for exactly 30 seconds on `/ui/v2/login/login?authRequest=...`, returning `504 upstream request timeout`. Root cause established empirically:

```
Pod (zitadel-web)
  ├─ wget https://auth.liverty-music.app/zitadel.settings.v2.SettingsService/...
  │  → 200 in ~120ms                                       ✓
  └─ Node.js Connect-RPC (httpVersion: "1.1") to same URL
     → never resolves; GFE returns 504 at 30s              ✗
```

Direct Pod-side HTTP/1.1 traffic to the public LB hairpin works; Node's HTTP client through the same hairpin does not. The upstream Zitadel PR #12022 documented an analogous Cloud Run failure as "intermittent SSL routines::record layer failure errors that were tenant-consistent" and fixed the middleware case by inlining a helper, but the `/login` dispatcher's `getAuthRequest` call in [`apps/login/src/lib/server/flow-initiation.ts`](https://github.com/zitadel/zitadel/blob/v4.14.0/apps/login/src/lib/server/flow-initiation.ts) still goes through `ZITADEL_API_URL` = the public LB hairpin.

The current spec [`zitadel-self-hosted-deployment`](../../specs/zitadel-self-hosted-deployment/spec.md) ("Login V2 UI Calls Zitadel API via Public URL") encodes the hairpin design choice with the rationale "Gateway round-trip adds ~10ms versus a direct Service hop, acceptable for dev". Empirically this is not ~10ms in prod — it is 30s and infinite — so the requirement needs to flip.

The alternative the existing rationale rejected ("registering the internal hostname as an `InstanceDomain` via the API; deferred because that adds an imperative bootstrap step outside of Pulumi/Kustomize") is in fact achievable declaratively via Zitadel's `SystemAPIUsers` config, which the original analysis missed.

**Stakeholders:** all end users (sign-in / sign-up flows blocked), [`pannpers`](https://github.com/pannpers) as Pulumi/cloud-provisioning owner, future operators consuming `zitadel-self-hosted-deployment` spec.

**Constraints:**

- GKE Autopilot prod cluster uses `kube-dns` (not CoreDNS) and disallows arbitrary `kube-system` ConfigMap mutation, ruling out DNS-layer rewrites.
- Pod `hostAliases.ip` accepts only IP addresses (verified against Kubernetes v1.32 API reference), so the alternative "host-aliases with pinned `clusterIP`" is a fragile hack that couples Service lifecycle to Pod spec.
- Zitadel `instance.v2.AddCustomDomain` requires `system.domain.write` (System level), which `IAM_OWNER` cannot satisfy.
- `pulumi up` runs through Pulumi Cloud Deployments on merge to `main` for dev; prod is manual from the Pulumi Cloud console.

## Goals / Non-Goals

**Goals:**

- Login V2 UI's server-side Connect-RPC calls reach `zitadel-api` without traversing the public LB. End users can complete sign-in and sign-up.
- The fix is declarative — `pulumi up` reproduces the state in any new environment with no Console clicks.
- Reuse existing PreservedTier + ESO + Reloader patterns; no new operational primitives.
- The flipped spec requirement records the hairpin incident root cause so the design choice cannot regress silently.

**Non-Goals:**

- Forking the upstream zitadel-login image to patch the Host header interceptor. The internal-domain route avoids the need to change application code.
- Editing `kube-system` DNS (kube-dns/CoreDNS/NodeLocalDNS). The internal-domain route avoids cluster-wide DNS surgery.
- Rolling back the `2026-05-15-consolidate-public-dns-on-cloudflare` change. Public traffic remains unchanged; only intra-cluster traffic from `zitadel-web` to `zitadel-api` is rerouted.
- Removing or migrating the existing `pulumi-admin` Machine User. It remains the Admin API caller for org/user/policy resources; the new System User has a disjoint role.
- Solving the same hairpin for other in-cluster callers of `auth.<env>.liverty-music.app` (e.g. `backend`). Those flows do not currently hang because they are over time, not over the synchronous `/login` request path. Out of scope here but the pattern established by this change is reusable.

## Decisions

### D1: Use cluster-internal Service URL for `ZITADEL_API_URL`, registered as an InstanceCustomDomain

`zitadel-web` will set `ZITADEL_API_URL=http://zitadel-api.zitadel.svc.cluster.local:8080` (plaintext HTTP; intra-cluster). The hostname `zitadel-api.zitadel.svc.cluster.local` is registered with the Zitadel instance as an `InstanceCustomDomain` so the API matches the request's `Host` header to a known instance and routes the call internally.

**Why not alternatives:**

- **Keep public URL, add timeout knob**: there is no upstream-supported Connect-RPC timeout that converts the hang into a fast failure, and even if there were, every login flow would still fail.
- **`hostAliases` + pinned `Service.clusterIP`**: requires hardcoding an IP from the cluster Service CIDR in Pod spec, coupling Service lifecycle to Pod template. Service recreation would require coordinated `hostAliases` updates. Rejected as a structural hack despite low immediate cost.
- **CoreDNS rewrite via `coredns-custom` ConfigMap**: prod cluster runs `kube-dns`, not CoreDNS. NodeLocal DNS Cache is CoreDNS-based and could in principle be customised, but Autopilot does not officially support editing the `node-local-dns` ConfigMap.
- **Migrate cluster DNS to Cloud DNS for GKE + Response Policy**: cluster-level change with significant blast radius for a single application bug.
- **Fork `zitadel-login` image to add a Host-header-overriding Connect-RPC interceptor**: maintenance overhead each Zitadel version bump; defeats the value of running upstream images.
- **Cluster-internal hostname but no InstanceCustomDomain (Host header reset by interceptor)**: same fork problem; not possible declaratively from manifests alone.

### D2: Declare the System API user via `SystemAPIUsers` env, with RSA key pair generated by Pulumi

Generate an RSA-2048 key pair using the `@pulumi/tls.PrivateKey` resource (analogous to how `@pulumi/random.RandomString` provides the masterkey: Pulumi-state-persisted, deterministically idempotent across `pulumi up` runs). Store the private key as a version of a new GSM Secret `zitadel-system-api-key` (PreservedTier — survives `workloadEnabled=false` shutdown, mirroring `zitadel-masterkey`); store the public key as a sibling GSM Secret `zitadel-system-api-pub` so ESO can sync it into the cluster without the private half ever leaving GSM. Materialise the public key into a K8s Secret via ESO; project the key file into the `zitadel-api` Pod and reference it from the `ZITADEL_SYSTEMAPIUSERS` env.

(Node `crypto.generateKeyPairSync` was considered but rejected: wrapping it in `pulumi.output(...)` is non-idempotent — Pulumi would regenerate the keypair on every preview/up, churning the SecretVersion. The serialization constraint that motivated Node-built-ins for `dynamic/api-client.ts` does not apply to the keygen side, which is top-level Pulumi program code, not a Dynamic Resource closure.)

Zitadel's `SystemAPIUsers` config accepts a list of `{ name, Path | KeyData, Memberships }`. When `Memberships` is omitted, the user is granted `MemberType: System, Role: SYSTEM_OWNER` by default — exactly what `instance.v2.AddCustomDomain` requires. The user identity in JWT `iss` / `sub` claims must match the config key name (e.g. `pulumi-system`).

**Why not alternatives:**

- **Create the System User via Zitadel Console after bootstrap**: imperative; doesn't reproduce in `pulumi up`; per-environment toil.
- **Reuse `pulumi-admin` (IAM_OWNER)**: `instance.v2.AddCustomDomain`'s proto annotation requires `system.domain.write` and its docstring explicitly says "cannot be called from an instance context". The Zitadel permission model has no escalation from `IAM_OWNER` to `SYSTEM_OWNER`; they are disjoint scopes by design.
- **Use the deprecated `AdminService.AddInstanceDomain`**: not present on v4 — Admin proto only exposes `AddInstanceTrustedDomain` (which is routing-irrelevant: trusted domains appear in OIDC discovery and email templates but are not matched against `Host`).
- **Use `AddTrustedDomain` instead of `AddCustomDomain`**: does not satisfy the routing requirement. The internal hostname needs to be the matched-`Host` target, not just a referenced URL.
- **Pre-register via `ZITADEL_FIRSTINSTANCE_VERIFIEDDOMAINS`**: only consulted on first-instance bootstrap with an empty DB. Prod is already bootstrapped, so this would do nothing without a Cloud SQL wipe.
- **Node `crypto.generateKeyPairSync` inside `pulumi.output(...)`**: non-idempotent — fresh keypair per `pulumi up` would churn the SecretVersion and cascade-rotate the System User on every apply. Rejected. (`@pulumi/tls` is the idiomatic Pulumi-stateful option chosen instead.)

### D3: Provision the `InstanceCustomDomain` via a Pulumi Dynamic Resource, not a typed provider resource

`@pulumiverse/zitadel@0.2.0` (the latest published version of the Pulumi Zitadel wrapper) does **not** expose `InstanceCustomDomain` as a resource, and the `Provider` does **not** accept a `system_api { user, audience, private_key }` block — both exist only in the upstream `terraform-provider-zitadel@v2.x`. The Pulumi wrapper has been lagging. Rather than fork the wrapper or wait, register the domain via a Pulumi **Dynamic Resource** that calls Zitadel's `instance.v2.InstanceService/AddCustomDomain` Connect-RPC endpoint directly with a System User-signed JWT.

The repo already established this pattern: [`src/zitadel/dynamic/`](cloud-provisioning/src/zitadel/dynamic/) contains `permanent-password.ts`, `target.ts`, `execution.ts`, `smtp-activation.ts`, `user-idp-link.ts` — all filling the same gap. [`src/zitadel/dynamic/api-client.ts`](cloud-provisioning/src/zitadel/dynamic/api-client.ts) already provides Node `crypto`-based JWT signing, an OAuth `jwt-bearer` token exchange, and an HTTPS request helper.

For this change, `api-client.ts` gains one new function:

```ts
buildSystemAssertion(profile: SystemUserProfile, audience: string): string
```

It signs a JWT with `iss = sub = profile.userName` (e.g. `pulumi-system`) and `aud = audience`, using the System User's RSA private key. Unlike `buildAssertion` for `pulumi-admin`, the JWT is sent **directly as `Authorization: Bearer <JWT>`** — there is no `/oauth/v2/token` exchange step. Zitadel verifies the signature against the public key declared in `SystemAPIUsers` and grants `SYSTEM_OWNER`.

A new file `dynamic/instance-custom-domain.ts` exports a `ZitadelInstanceCustomDomain` Dynamic Resource with `create`, `read`, `delete` callbacks calling `AddCustomDomain` / `ListCustomDomains` / `RemoveCustomDomain` respectively. The resource's `inputs` shape: `{ domain, customDomain, instanceId, systemUserName, systemUserPrivateKey }`. State persists `{ instanceId, customDomain }` as the identifying tuple.

**Why not alternatives:**

- **Fork `@pulumiverse/zitadel`**: high maintenance overhead; a transient fork pinned to a fork URL is operationally fragile compared to a local Dynamic Resource that uses only Node built-ins.
- **One-shot K8s Job to call `AddCustomDomain`**: no Pulumi-graph awareness of the registration, no drift detection on `pulumi preview`, separate rollback path. Out-of-band imperative steps were specifically the constraint this change set out to eliminate.
- **Pulumi `command` provider invoking `curl`**: works but obscures the API call in shell, makes drift detection brittle, and offers no type safety.

### D4: Encode private-key delivery via the existing GSM → ESO → file-mount pattern (public key) and GSM → Pulumi read (private key)

The Dynamic Resource needs the private key to sign JWTs at `create` time. Pulumi reads the private key directly from GSM (`gcp.secretmanager.getSecretVersionOutput`) at preview/up time and threads it as a secret-marked input to the Dynamic Resource. Public key delivery to the Zitadel API Pod follows the existing `external-secret-postgres-admin.yaml` shape: GSM → ESO → K8s Secret → file projection at `/var/run/zitadel/system-api/pulumi-system.pem`.

This separates the two consumers cleanly: Pulumi reads private (sign), Zitadel API reads public (verify). Neither key ever leaves its intended boundary. The private-key value is wrapped in `pulumi.secret(...)` so it appears as `[secret]` in preview output and state — mirroring how the existing `pulumi-admin` JWT-profile JSON is handled.

### D5: Reuse `bootstrap-uploader` shape, not the existing `pulumi-admin` Machine Key lifecycle

The existing `bootstrap-uploader` sidecar copies Zitadel-emitted admin machine keys *out* to GSM. The System User goes the opposite direction: Pulumi generates the key and pushes the public half *in* via env. No sidecar is needed; standard ESO + ConfigMap suffices. This keeps the two boot-time chicken-and-egg situations independent.

**Why not alternatives:**

- **Have Zitadel generate the System User key**: there is no upstream mechanism — `SystemAPIUsers` is read-only at runtime; Zitadel does not emit a key file on first boot for system users.
- **Run a one-shot Job inside the cluster that calls a System API bootstrap endpoint**: no such endpoint exists; System Users are config-only.

### D6: Migration order — System User must exist before the Dynamic Resource's first `create` runs

Pulumi resource graph (declarative `dependsOn`):

1. `gcp.secretmanager.Secret` `zitadel-system-api-key` + `SecretVersion` carrying the Pulumi-generated private key.
2. `kubernetes.ExternalSecret` `zitadel-system-api-pub` syncing the **public** key into a K8s Secret (mounted into the API Pod).
3. Kustomize patch on `zitadel-api` Deployment: `ZITADEL_SYSTEMAPIUSERS` env + volume mount referencing the projected public key file. Reloader rolls Pods on Secret change.
4. The `ZitadelInstanceCustomDomain` Dynamic Resource. `dependsOn` the SecretVersion (private key) AND the rendered Deployment (a `kubernetes.apps.v1.Deployment` Pulumi resource that waits for `availableReplicas == replicas`).
5. The base-manifest patch flipping `zitadel-web`'s `ZITADEL_API_URL` to the cluster-internal URL.

Step 5 is a manifest-only change in `k8s/`; it lands via the same `pulumi up` as steps 1–4 because Pulumi orchestrates Kustomize-rendered Kubernetes resources. The race we must avoid is "ZITADEL_API_URL is flipped before the InstanceCustomDomain is accepted by the API". The `dependsOn` chain above prevents that within a single `pulumi up`. For the cross-PR case (rare — only if a human stages the manifest change separately), tasks.md 5.4 documents the gate.

If `dependsOn` proves insufficient in practice (e.g. Reloader-triggered rollout finishes after the Dynamic Resource's create call), the fallback is a two-pass `pulumi up`: first run produces the env-var + uploaded key + rolled Pod with no Dynamic Resource declared; second run adds the Dynamic Resource.

## Risks / Trade-offs

- **Risk:** First `pulumi up` after merging the change runs the `ZitadelInstanceCustomDomain` Dynamic Resource's `create` before the API Pod has the new `ZITADEL_SYSTEMAPIUSERS` env loaded, because Pulumi's resource graph is not aware of which Pod runtime config has actually propagated. → **Mitigation**: explicit `dependsOn` between the Dynamic Resource and both the SecretVersion (private key) and the rendered `kubernetes.apps.v1.Deployment` Pulumi resource for `zitadel-api` (which waits for `availableReplicas == replicas`). Reloader will have rolled the Pod by the time the Deployment resource reaches the ready state. If still racy in practice, fall back to a two-pass `pulumi up` per D6 fallback.

- **Risk:** Dynamic Resource serialization. Pulumi ships the dynamic provider's CRUD callbacks to a worker process by serializing the enclosing function's closure. Adding external imports (e.g. `@connectrpc/connect-node`, `jose`, `axios`) into `dynamic/instance-custom-domain.ts` can break that contract — symptoms include "Cannot find module" at apply time. → **Mitigation**: use only Node built-ins (`crypto`, `https`, `url`) just like the existing `dynamic/api-client.ts`. The Connect-RPC call format is just `POST <baseUrl>/zitadel.instance.v2.InstanceService/AddCustomDomain` with JSON body and Bearer JWT — no Connect client library needed.

- **Risk:** Plaintext HTTP from `zitadel-web` to `zitadel-api` inside the cluster. → **Mitigation**: traffic stays inside the GKE cluster network; Cloud SQL Auth Proxy already uses plaintext on `127.0.0.1` for similar reasons. Cluster network policies (when introduced) will still apply. Switching to TLS would require the Zitadel API to serve TLS on the Service port, which it does not today (`ZITADEL_TLS_ENABLED=false`).

- **Risk:** The Connect-RPC error message on `Host` mismatch is opaque — if `InstanceCustomDomain` registration silently fails or has the wrong domain string, Login UI would 404 with no actionable message in pod logs. → **Mitigation**: Pulumi readback on the `InstanceCustomDomain` resource verifies the registration after create. Add a startup-time smoke test in tasks.md to `curl` the API via the internal hostname with the new Host header and confirm 200 from `/debug/ready`.

- **Risk:** Same Zitadel hairpin pattern exists for other in-cluster callers (`backend`, future workloads) that hit `auth.<env>.liverty-music.app`. They don't hang today because they use async paths or fewer connections, but the underlying GFE behaviour persists. → **Mitigation**: out of scope for this change. The internal-URL pattern established here is the template for those callers to adopt later. Document in the spec's rationale block so future migrations can reference it.

- **Risk:** The `2026-04-30-optimize-dev-kube-dns-replicas` change reduced dev kube-dns replicas; adding more dependency on kube-dns from `zitadel-web` (resolving `zitadel-api.zitadel.svc.cluster.local`) is marginal but worth noting. → **Mitigation**: each Login UI Pod caches the DNS result for the lifetime of the connection (Node `http.Agent` keep-alive). Steady-state lookups are negligible. NodeLocal DNS Cache also fronts kube-dns on each node.

- **Risk:** The new `zitadel-system-api-key` GSM Secret is a new key class to rotate. → **Mitigation**: Pulumi `tls.PrivateKey` regeneration on Pulumi config change rotates both halves atomically; Zitadel `SystemAPIUsers` will accept the new public key on next Pod rollout. Document rotation procedure in a runbook follow-up.

- **Trade-off:** This change widens `cloud-provisioning`'s Pulumi dependency on Zitadel (two providers instead of one). The blast radius of a misconfigured System User credential is now also higher — `SYSTEM_OWNER` can manipulate every instance and every org. → **Accepted**. Privileges are necessary for `AddCustomDomain`; minimised by the System User having no human-facing surface and its private key living only in GSM with IAM-scoped access.
