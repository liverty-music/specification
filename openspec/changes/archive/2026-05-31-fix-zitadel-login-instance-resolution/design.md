## Context

Prod interactive auth via the hosted Login V2 UI is down: every load of `https://auth.liverty-music.app/ui/v2/login/login?authRequest=...` returns HTTP 504. The `zitadel-api` Pod (v4.14.0) has 10d uptime and 0 restarts; the instance record exists (`instance_id 372892288692519067`) and resolves correctly for browser→Gateway traffic (verified: a `SettingsService/GetGeneralSettings` call at 01:30:09 returned HTTP 200 with `instance_host: auth.liverty-music.app`). The failures are confined to the Login V2 Pod's server-side (SSR) calls to the API.

The decisive evidence (Cloud Logging, prod, `instance_interceptor.go:100`):

```
error: "unable to get instance by domain: instanceDomain zitadel-api,
        publicHostname auth.liverty-music.app: ID=QUERY-1kIjX
        Message=Errors.Instance.NotFound"
```

Two facts established from the official Zitadel sources combine to produce this:

1. **v4.7.1+ host-resolution change** (`zitadel/zitadel#11163`): instance lookup is driven by `InstanceHostHeaders`, whose default is `[x-zitadel-instance-host]` only (`cmd/defaults.yaml`). The `Host` header is no longer read for instance resolution; `HTTP1HostHeader: host` / `HTTP2HostHeader: ":authority"` remain only as deprecated fallbacks. `PublicHostHeaders` default is `[x-zitadel-public-host]`.
2. **h2c transport**: our API Service is `protocol: http2` / `appProtocol: kubernetes.io/h2c`. On HTTP/2 the `:authority` equals the dial target (`zitadel-api`); a custom `Host` header does not override it. So the chart-generated `Host:<ExternalDomain>` is inert for instance lookup, and with no `x-zitadel-instance-host` sent, lookup falls back to `:authority` = `zitadel-api` → `NotFound` → SSR render fails → Gateway 504.

The Login Pod already sends `X-Zitadel-Public-Host:<ExternalDomain>` (the error line confirms `publicHostname auth.liverty-music.app` resolved). That header is the available signal to drive instance lookup.

Current config: `zitadel.configmapConfig` sets only `ExternalDomain/ExternalPort/ExternalSecure`; no host-header overrides. Delivery is GitOps via `cloud-provisioning` → ArgoCD. Dev (`standard-cluster-osaka`) is intentionally stopped for cost; prod (`autopilot-cluster-osaka`) is the live target.

## Goals / Non-Goals

**Goals:**
- Restore interactive sign-in/sign-up on the prod hosted login UI (no 504, no `Errors.Instance.NotFound`).
- Fix declaratively in `cloud-provisioning`, domain-independently, in the Helm base values so both envs are covered.
- Correct the `zitadel-self-hosted-deployment` spec's incorrect "resolves by Host header / chart defaults sufficient" rationale.
- Keep browser→Gateway resolution behavior unchanged.

**Non-Goals:**
- No change to `ExternalDomain/ExternalPort/ExternalSecure` (would force a setup re-run; not needed).
- No per-instance domain registration, System User, JWT pipeline, or instance-id discovery.
- No override of the chart-generated login `CUSTOM_REQUEST_HEADERS` / `ZITADEL_API_URL` (the `customConfigmapConfig` full-dotenv replacement is explicitly rejected — see Decisions).
- No Zitadel version change, no application/proto/backend change.
- Not collapsing the `/ui/v2/login/login` path redundancy (tracked separately).

## Decisions

### Decision: Add `x-zitadel-public-host` to the API's `InstanceHostHeaders` (chosen)

Set in `zitadel.configmapConfig` (base values):

```yaml
zitadel:
  configmapConfig:
    InstanceHostHeaders:
      - x-zitadel-instance-host   # preserve the v4.14 default (evaluated first)
      - x-zitadel-public-host     # NEW: resolve internal Login V2 calls via the header they already send
```

Zitadel overrides (not merges) the default list, so the `x-zitadel-instance-host` default must be restated explicitly. For internal Login calls, `x-zitadel-public-host` = `<ExternalDomain>` now drives instance lookup → resolves. For browser calls, neither header is present, so resolution falls through to the `:authority` fallback (`<ExternalDomain>`) exactly as today.

**Why over the alternatives:**
- **Alternative A — `login.customConfigmapConfig` to add `X-Zitadel-Instance-Host`** (the maintainer-prescribed header): requires replacing the *entire* chart-generated login dotenv (`ZITADEL_SERVICE_USER_TOKEN_FILE`, `ZITADEL_API_URL`, `CUSTOM_REQUEST_HEADERS`), re-stating the prod domain, and is exactly the inline override the existing spec warns against (drift risk if the chart's dotenv schema changes). Rejected as higher-footprint and more fragile.
- **Alternative B — route Login V2 via the public host (`ZITADEL_API_URL=https://auth.liverty-music.app`)**: reintroduces the GCP HTTPS LB hairpin that the in-cluster routing was adopted to eliminate (latency, cost, the original 30s-timeout shape). Rejected.
- **Alternative C — register `zitadel-api` as an instance/trusted domain**: pollutes instance domains with a non-public cluster name and is imperative (console/API), not GitOps. Rejected.

The chosen option is a single declarative key in the file we already maintain, reuses a header that is already on the wire, and is the lowest-risk change to browser traffic.

### Decision: Place the setting in base, not the overlays

Header *names* are environment-independent; only the values they carry (`<ExternalDomain>`) differ, and those already differ via the existing per-overlay `ExternalDomain`. Putting `InstanceHostHeaders` in `base/values.yaml` keeps dev and prod consistent and avoids overlay drift.

## Risks / Trade-offs

- **[Overloading instance-host chain with the public-host header could blur instance vs public host in a multi-tenant setup]** → We run a single virtual instance; instance host and public host are the same domain. No tenant-confusion surface. If multi-tenancy is ever introduced, revisit by switching to an explicit `X-Zitadel-Instance-Host` on the Login side.
- **[Overriding `InstanceHostHeaders` drops the default list, silently removing `x-zitadel-instance-host`]** → Mitigated by restating `x-zitadel-instance-host` explicitly as the first entry.
- **[Browser path regression if the `:authority` fallback is not actually consulted when the configured headers are absent]** → The fallback is what makes browser traffic work *today* (the 01:30 success had no instance-host header). Verify post-deploy with a real browser load and a known-good API call; the spec includes an explicit "browser traffic still resolves" scenario.
- **[ConfigMap change not picked up without a restart]** → Zitadel reads config at startup. Migration step includes `kubectl -n zitadel rollout restart deploy/zitadel-api`.
- **[Setting mistaken for a stored-instance change requiring setup re-run]** → It is request-parse config only; no `FirstInstance`/setup Job involvement. Called out so no one re-runs bootstrap.

## Migration Plan

1. Edit `k8s/namespaces/zitadel/base/values.yaml`: add `InstanceHostHeaders` under `zitadel.configmapConfig`.
2. `make lint-k8s` (render + kube-linter) in `cloud-provisioning`; confirm the key lands in the rendered `zitadel-api-config-yaml`.
3. PR → review → merge to `main`.
4. ArgoCD syncs the `zitadel` Application (prod overlay).
5. `kubectl -n zitadel rollout restart deploy/zitadel-api`; wait for the new pod to be `2/2 Ready`.
6. **Verify**: load `https://auth.liverty-music.app/ui/v2/login/login` → expect non-5xx. Then `gcloud logging read 'resource.labels.namespace_name="zitadel" AND jsonPayload.msg="unable to set instance"' --freshness=1h` → expect zero new entries.
7. Resume the signup → PostHog `user.created` verification path that the 504 was blocking.

**Rollback**: revert the base-values change → ArgoCD sync → rollout restart. Pre-change resolution behavior returns immediately (the change only *adds* a header to the lookup chain).

## Open Questions

- None blocking. (Optional follow-up: if Zitadel publishes a dedicated chart value for extra login headers, reconsider whether the API-side `InstanceHostHeaders` or a login-side `X-Zitadel-Instance-Host` is the more idiomatic long-term home — both are valid; the API-side change is chosen now for footprint and to reuse the already-present header.)
