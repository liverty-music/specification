## Why

In prod, every call to `/ui/v2/login/login?authRequest=...` returns `504 upstream request timeout` after exactly 30 seconds, so neither sign-in nor sign-up can complete. The Login V2 UI's server-side Connect-RPC call to `getAuthRequest` is the await that hangs; the call traverses the public Gateway hairpin (`zitadel-web` Pod → public LB IP `34.110.151.208` → same Gateway → `zitadel-api`) per the current `Login V2 UI Calls Zitadel API via Public URL` requirement. Direct `wget` from the same Pod to the same URL responds in ~120 ms, isolating the failure to the Node.js HTTP client + GCP HTTPS LB hairpin combination — a known issue documented in upstream Zitadel PR #12022 ("intermittent SSL routines::record layer failure errors that were tenant-consistent" on Cloud Run). The "Gateway round-trip adds ~10ms" assumption in the rationale of that requirement does not hold in practice.

## What Changes

- **BREAKING**: Login V2 UI calls Zitadel API via the cluster-internal Service URL (`http://zitadel-api.zitadel.svc.cluster.local:8080`), not the public issuer URL. Removes the hairpin entirely.
- Register the cluster-internal hostname as an `InstanceCustomDomain` on the Zitadel instance so the API accepts the new `Host` header without HTTP 404.
- Provision a dedicated Zitadel **System API user** declaratively via the `ZITADEL_SYSTEMAPIUSERS` env var (public-key reference, no Console action), because `instance.v2.AddCustomDomain` requires `system.domain.write` permission which `IAM_OWNER` (`pulumi-admin`) cannot satisfy.
- Generate the System User RSA key pair with `tls.PrivateKey` in Pulumi; store the private key in GSM (`zitadel-system-api-key`), inject the public key into the `zitadel-api` Deployment via ESO+ConfigMap.
- Add a second `zitadel.Provider` instance configured with the System User credentials (`system_api` block) so `zitadel.InstanceCustomDomain` resources can be declared and applied.
- Reuse the existing PreservedTier secret pattern + Reloader auto-restart so the entire chain is `pulumi up`-managed; no imperative Console step in any environment.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `zitadel-self-hosted-deployment`:
  - The `Login V2 UI Calls Zitadel API via Public URL` requirement flips: the URL becomes cluster-internal, and the new behaviour is that the API must accept the cluster-internal `Host` header via a registered `InstanceCustomDomain`.
  - A new requirement covers the System API user bootstrap (RSA key generation, GSM storage, `ZITADEL_SYSTEMAPIUSERS` injection, Pulumi `system_api` provider configuration).
  - A new requirement covers the declarative `InstanceCustomDomain` registration for the cluster-internal hostname per environment.

## Impact

- **`cloud-provisioning/k8s/namespaces/zitadel/base/deployment-web.yaml`** — `ZITADEL_API_URL` env value flips from `https://auth.dev.liverty-music.app` to `http://zitadel-api.zitadel.svc.cluster.local:8080`; prod overlay [`deployment-web-patch.yaml`](cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/deployment-web-patch.yaml) becomes a no-op for this env var (cluster-internal hostname is environment-agnostic).
- **`cloud-provisioning/k8s/namespaces/zitadel/base/deployment-api.yaml`** — new `ZITADEL_SYSTEMAPIUSERS` env (from a ConfigMap or projected Secret) referencing the System User public key file.
- **`cloud-provisioning/src/zitadel/components/secrets.ts`** — new GSM Secret `zitadel-system-api-key` (PreservedTier, mirrors the existing `zitadel-machine-key-for-pulumi-admin` pattern).
- **`cloud-provisioning/src/zitadel/components/`** — new component (or extension of an existing one) that generates an RSA key pair via `tls.PrivateKey`, writes private key into the new GSM Secret, materialises the public key into a K8s Secret/ConfigMap via ESO for mounting into `zitadel-api`.
- **`cloud-provisioning/src/zitadel/`** — second `zitadel.Provider` instance configured with `system_api` block (user, audience, private key from GSM); a new `zitadel.InstanceCustomDomain` resource per environment binding `zitadel-api.zitadel.svc.cluster.local` to the bootstrapped instance.
- **Boot order** — `zitadel-api` must boot with `ZITADEL_SYSTEMAPIUSERS` env BEFORE the System User-authenticated Pulumi provider can call `AddCustomDomain`. Same `--first-instance` bootstrap ordering risk as the existing `pulumi-admin` Machine Key shell pattern; mitigated identically by Reloader-driven rollouts and Pulumi `dependsOn` ordering.
- No user-visible API change for end users. End-user `auth.liverty-music.app` traffic unchanged; only intra-cluster traffic from `zitadel-web` to `zitadel-api` is rerouted.
- The base manifest comment block at [`deployment-web.yaml:60-82`](cloud-provisioning/k8s/namespaces/zitadel/base/deployment-web.yaml#L60-L82) describing the prior public-URL design is rewritten to reflect the new internal path and to record the hairpin incident root cause.
