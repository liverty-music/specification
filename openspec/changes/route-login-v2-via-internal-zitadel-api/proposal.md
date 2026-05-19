## Why

In prod, every call to `/ui/v2/login/login?authRequest=...` returns `504 upstream request timeout` after exactly 30 seconds, so neither sign-in nor sign-up can complete. The Login V2 UI's server-side Connect-RPC call to `getAuthRequest` is the await that hangs; the call traverses the public Gateway hairpin (`zitadel-web` Pod → public LB IP `34.110.151.208` → same Gateway → `zitadel-api`) per the current `Login V2 UI Calls Zitadel API via Public URL` requirement. Direct `wget` from the same Pod to the same URL responds in ~120 ms, isolating the failure to the Node.js HTTP client + GCP HTTPS LB hairpin combination — a known issue documented in upstream Zitadel PR #12022 ("intermittent SSL routines::record layer failure errors that were tenant-consistent" on Cloud Run). The "Gateway round-trip adds ~10ms" assumption in the rationale of that requirement does not hold in practice.

## What Changes

- **Behavior change** (intra-cluster routing only; no external API contract change): Login V2 UI calls Zitadel API via the cluster-internal Service URL (`http://zitadel-api.zitadel.svc.cluster.local`), not the public issuer URL. Removes the hairpin entirely.
- Register the cluster-internal hostname as an `InstanceCustomDomain` on the Zitadel instance so the API accepts the new `Host` header without HTTP 404.
- Provision a dedicated Zitadel **System API user** declaratively via the `ZITADEL_SYSTEMAPIUSERS` env var (public-key reference, no Console action), because `instance.v2.AddCustomDomain` requires `system.domain.write` permission which `IAM_OWNER` (`pulumi-admin`) cannot satisfy.
- Generate the System User RSA key pair with `@pulumi/tls.PrivateKey` in Pulumi; store the private key in GSM (`zitadel-system-api-key`), inject the public key into the `zitadel-api` Deployment via ESO+ConfigMap.
- Add a Pulumi **Dynamic Resource** (`ZitadelInstanceCustomDomain`) that signs a System User JWT with the private key (Node `crypto`) and POSTs to `instance.v2.InstanceService/AddCustomDomain` directly. `@pulumiverse/zitadel@0.2.0` exposes neither this resource nor a `system_api` provider auth block, so the Dynamic Resource pattern (already used by `permanent-password.ts`, `target.ts`, etc.) closes the gap. See `design.md` D3 for the full decision and the rejected alternatives.
- Reuse the existing PreservedTier secret pattern + Reloader auto-restart so the entire chain is `pulumi up`-managed; no imperative Console step in any environment.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `zitadel-self-hosted-deployment`:
  - The `Login V2 UI Calls Zitadel API via Public URL` requirement flips: the URL becomes cluster-internal, and the new behaviour is that the API must accept the cluster-internal `Host` header via a registered `InstanceCustomDomain`.
  - A new requirement covers the System API user bootstrap (RSA key generation via `@pulumi/tls`, GSM storage, `ZITADEL_SYSTEMAPIUSERS` injection, and the Pulumi Dynamic Resource that consumes the private key for JWT signing).
  - A new requirement covers the declarative `InstanceCustomDomain` registration for the cluster-internal hostname per environment.

## Impact

- **`cloud-provisioning/k8s/namespaces/zitadel/base/deployment-web.yaml`** — `ZITADEL_API_URL` env value flips from `https://auth.dev.liverty-music.app` to `http://zitadel-api.zitadel.svc.cluster.local`; prod overlay [`deployment-web-patch.yaml`](cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/deployment-web-patch.yaml) becomes a no-op for this env var (cluster-internal hostname is environment-agnostic).
- **`cloud-provisioning/k8s/namespaces/zitadel/base/deployment-api.yaml`** — new `ZITADEL_SYSTEMAPIUSERS` env (from a ConfigMap or projected Secret) referencing the System User public key file.
- **`cloud-provisioning/src/zitadel/components/secrets.ts`** — new GSM Secret `zitadel-system-api-key` (PreservedTier, mirrors the existing `zitadel-machine-key-for-pulumi-admin` pattern).
- **`cloud-provisioning/src/zitadel/components/secrets.ts`** — extended with a `@pulumi/tls.PrivateKey` resource that generates the RSA-2048 key pair, plus sibling GSM Secrets `zitadel-system-api-key` (private) and `zitadel-system-api-pub` (public); the private key is consumed by Pulumi directly while ESO syncs the public key into the cluster.
- **`cloud-provisioning/src/zitadel/dynamic/instance-custom-domain.ts`** — new Pulumi Dynamic Resource `ZitadelInstanceCustomDomain` with `create` / `read` / `update` / `diff` / `delete` callbacks that sign System User JWTs via Node `crypto` (mirroring the existing `dynamic/api-client.ts` pattern) and POST to `instance.v2.InstanceService/AddCustomDomain` / `ListCustomDomains` / `RemoveCustomDomain`.
- **Boot order** — `zitadel-api` must boot with `ZITADEL_SYSTEMAPIUSERS` env BEFORE the System User-authenticated Pulumi provider can call `AddCustomDomain`. Same `--first-instance` bootstrap ordering risk as the existing `pulumi-admin` Machine Key shell pattern; mitigated identically by Reloader-driven rollouts and Pulumi `dependsOn` ordering.
- No user-visible API change for end users. End-user `auth.liverty-music.app` traffic unchanged; only intra-cluster traffic from `zitadel-web` to `zitadel-api` is rerouted.
- The base manifest comment block at [`deployment-web.yaml:60-82`](cloud-provisioning/k8s/namespaces/zitadel/base/deployment-web.yaml#L60-L82) describing the prior public-URL design is rewritten to reflect the new internal path and to record the hairpin incident root cause.
