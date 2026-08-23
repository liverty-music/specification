## Why

The self-hosted Zitadel is pinned to **v4.14.0**; upstream latest is **v4.17.1**
(2026-08-14). Staying current keeps us on a patched, supported release and picks
up **#12453 — "allow invite codes for users whose auth methods were all
removed"** (v4.17.0), which directly hardens the organizer operator invite flow
we just shipped. There are **no breaking API changes** in the v4.15→v4.17.1
release notes. Because the dev env is intentionally stopped for cost, this is a
**prod-direct** upgrade — so it is scoped as its own change with the prod
rollout gated on explicit approval.

## What Changes

- Bump the Zitadel image pin **v4.14.0 → v4.17.1** in
  `k8s/namespaces/zitadel/base/values.yaml`:
  - the API server image `tag:` (line 15),
  - the Login V2 UI image `login.image.tag:` (line 219),
  - the OTEL `service.version=v4.14.0` resource-attribute label (line 203).
- Update the stale `v4.14.0` references in explanatory comments (the OTEL-path
  404 note, the watchdog cronjob header, the login-image build note) to reflect
  the new version where the behavior still holds, or re-verify and correct them.
- Confirm the **vendored** Helm chart `zitadel-9.34.1`
  (`overlays/{dev,prod}/charts/zitadel-9.34.1/`) renders cleanly with the
  v4.17.1 images; bump the vendored chart **only if** v4.17.1 requires chart
  template/values changes (image-tag override normally decouples app version
  from chart version).
- Apply to **prod** via `pulumi up` / ArgoCD sync (dev stays stopped). Zitadel
  runs its **boot-time Cloud SQL schema migrations** (the chart `init`/`setup`
  job) against the prod `POSTGRES_18` instance on first boot of the new image —
  ensure the migration job completes before the API Deployment becomes ready,
  with a documented rollback (re-pin v4.14.0) path.
- The `#10103` notification-deadlock watchdog cronjob was **already removed** on
  `main` (commit `c29837f`, deemed ineffective — the CronJob restarted both
  replicas at once and the sidecar liveness probe restarted the wrong
  container); recovery is now `kubectl rollout restart deploy/zitadel-api`. This
  upgrade does **not** reintroduce it. `#10103` remains unfixed in v4.17.1, so
  the manual-restart posture carries forward.
- Post-upgrade **verification** in prod: OIDC discovery document, hosted Login V2
  UI, and a real end-to-end sign-in (consumer + organizer console) succeed on the
  new image; the instance-host-header resolution and health endpoints are intact.

Explicit non-goals: no proto/backend/frontend changes; no chart-architecture
change (still the official chart via `helmCharts:`); this does NOT address the
organizer loginname bug (already fixed in backend v1.39.0) — it is an
independent version bump.

## Capabilities

### Modified Capabilities
- `zitadel-self-hosted-deployment`: the pinned Zitadel runtime version moves to
  v4.17.1, and the deployment requirement gains an explicit **version-upgrade
  procedure** (pinned-tag edit → boot-time migration → post-upgrade
  verification, prod-direct while dev is stopped).

## Impact

- **cloud-provisioning**: `k8s/namespaces/zitadel/base/values.yaml` image tags +
  OTEL version label; comment refresh; possible vendored-chart bump under
  `overlays/{dev,prod}/charts/` only if required. No Pulumi resource changes
  expected (image tag is a manifest value).
- **prod runtime**: a rolling replace of the `zitadel-api` and `zitadel-api-login`
  Deployments; a **one-time boot-time schema migration** on the prod Cloud SQL
  `postgres-osaka` instance. Brief control-plane blip possible during rollout.
- No proto changes; backend/frontend unaffected (no OIDC/API contract change).
