## Why

The prod hosted-login UI (`https://auth.liverty-music.app/ui/v2/login/login`) returns HTTP 504 on every interactive sign-in / sign-up attempt. Cloud Logging shows the Zitadel API rejecting the Login V2 Pod's server-side calls with `Errors.Instance.NotFound` (`instance_interceptor.go:100`, error ID `QUERY-1kIjX`): `instanceDomain zitadel-api, publicHostname auth.liverty-music.app`. The instance record exists and resolves fine for browser→Gateway traffic, so this is not DB loss or a missing Custom Domain — it is an instance-host header-resolution gap introduced by Zitadel's v4.7.1+ host-resolution change, which our spec's current rationale documents incorrectly.

Root cause: Zitadel v4.14.0's default `InstanceHostHeaders` is `[x-zitadel-instance-host]` only — it no longer reads the `Host` header for instance lookup. The Login V2 Pod calls `zitadel-api:80` over h2c, so on the wire `:authority` = the dial target `zitadel-api` (the `Host:<ExternalDomain>` custom header does not survive HTTP/2), and no `x-zitadel-instance-host` is sent. Instance lookup therefore falls back to `:authority` = `zitadel-api`, which matches no instance → `NotFound` → the SSR render fails → Gateway 504. The Login Pod already sends `X-Zitadel-Public-Host:<ExternalDomain>` (the public host resolves correctly in the same error line), so the public-host header is the available, already-present signal to drive instance lookup.

## What Changes

- Add `InstanceHostHeaders: [x-zitadel-instance-host, x-zitadel-public-host]` to `zitadel.configmapConfig` in the Zitadel Helm base values (`k8s/namespaces/zitadel/base/values.yaml`), so the API resolves the instance from the `X-Zitadel-Public-Host` header the Login V2 Pod already sends. Header names are domain-independent, so the setting lives in base and covers both dev and prod.
- Browser→Gateway traffic is unaffected: it sends neither `x-zitadel-instance-host` nor `x-zitadel-public-host`, so it continues to fall back to `:authority` = `<ExternalDomain>` and resolve as before.
- Correct the `zitadel-self-hosted-deployment` spec's "Login V2 UI Routes Outbound Calls…" requirement, whose rationale wrongly claims the interceptor "resolves the instance by the `Host` header" and that the chart-generated `Host` + `X-Zitadel-Public-Host` pair is sufficient. Capture the v4.7.1+ `InstanceHostHeaders` behavior and the h2c `:authority` override as the operative invariant.
- No application code, proto, or backend change. No `FirstInstance`/setup re-run (this is request-parse config). Requires a `zitadel-api` rollout restart after ArgoCD sync to reload the ConfigMap.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `zitadel-self-hosted-deployment`: The "Login V2 UI Routes Outbound Calls Via Cluster-Internal Service Using CUSTOM_REQUEST_HEADERS" requirement is corrected — the API SHALL set `InstanceHostHeaders` to include `x-zitadel-public-host` so cluster-internal Login V2 SSR calls (which reach the API as `:authority=zitadel-api` over h2c and carry no `x-zitadel-instance-host`) resolve to the correct virtual instance. The incorrect "resolves by `Host` header / chart defaults are sufficient" rationale is replaced with the v4.7.1+ header-resolution facts.

## Impact

- **Repo**: `cloud-provisioning` only. `k8s/namespaces/zitadel/base/values.yaml` (`zitadel.configmapConfig.InstanceHostHeaders`). Rendered into the `zitadel-api-config-yaml` ConfigMap for both overlays.
- **Runtime**: prod (`autopilot-cluster-osaka`) and dev (`standard-cluster-osaka`, currently intentionally stopped). Delivery via PR → merge → ArgoCD sync → `kubectl -n zitadel rollout restart deploy/zitadel-api`.
- **Blast radius**: instance/request resolution for all inbound Zitadel API traffic. Browser path verified unaffected (relies on the still-present `:authority` fallback). Single-instance deployment, so overloading the instance-host chain with the public-host header carries no tenant-confusion risk.
- **Unblocks**: interactive sign-in/sign-up via the hosted login UI, and the downstream PostHog `user.created` signup-verification path that is currently blocked by the 504.
- **Spec**: `openspec/specs/zitadel-self-hosted-deployment/spec.md` (delta).
