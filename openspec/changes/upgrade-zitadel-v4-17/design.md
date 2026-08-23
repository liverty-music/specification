## Context

See proposal.md — Why. The self-hosted Zitadel (capability
`zitadel-self-hosted-deployment`) is pinned to **v4.14.0**; target is **v4.17.1**
(upstream latest, 2026-08-14). The deployment is rendered from the official
`zitadel/zitadel-charts` chart (vendored `zitadel-9.34.1`) via Kustomize
`helmCharts:`, with the image tag overridden in `base/values.yaml`. Dev is
intentionally stopped, so this is prod-direct.

## Goals / Non-Goals

**Goals:** move the pinned Zitadel version to v4.17.1 (API + Login V2 images +
OTEL label together), run the boot-time schema migration safely against prod
Cloud SQL, verify the OIDC + Login V2 surface end-to-end, retain the `#10103`
watchdog, with a clear rollback.

**Non-Goals:** no chart-architecture change; no proto/backend/frontend change; no
fix for the organizer loginname bug (already fixed in be v1.39.0); no re-enabling
of dev.

## Decisions

**D1 — Bump the image tag, not (necessarily) the vendored chart.** The chart
`helmCharts:` integration overrides the image tag via `base/values.yaml`, which
decouples the running app version from the chart's `appVersion` (v4.13.1). So the
primary edit is the three `v4.14.0` values (API `tag`, `login.image.tag`, OTEL
`service.version`). The vendored `zitadel-9.34.1` chart is bumped **only if**
`kustomize build --enable-helm` on v4.17.1 surfaces a template/values
incompatibility. Verified: both overlays render clean with v4.17.1 and no chart
change.

**D2 — Boot-time migration is the risk; sequence and gate it.** Zitadel runs its
schema migration in the chart's init/setup job on boot; the API only serves
after it completes. Against the prod `POSTGRES_18` Cloud SQL instance this is a
**one-time, forward-only** schema change (v4.15.2 release notes reference setup
migration steps 40/64/70 — migrations DO run between v4.14 and v4.17).
Mitigations: (a) confirm a recent Cloud SQL automated backup / take an on-demand
backup before rollout; (b) watch the setup job to success before declaring done;
(c) rollback = re-pin v4.14.0 **only if** the migration has not advanced the
schema past v4.14.0's compatibility — since Zitadel migrations are forward-only,
a schema already migrated to v4.17 may not boot on v4.14, so the real safety net
is the backup. This is why the rollout is approval-gated.

**D3 — Prod-direct, approval-gated, staged.** Dev is stopped, so there is no dev
dry-run. Compensate with: local render + kustomize-lint (done), review of the
v4.15→v4.17.1 release notes for config deprecations (done — none), then apply to
prod in a controlled window. The operator performs the prod `pulumi up` / merge;
the agent prepares the PR and monitors, never triggers the prod rollout
unattended.

**D4 — Verify at the real surface, not just pod health.** Post-upgrade success =
OIDC discovery + a real hosted Login V2 sign-in (consumer AND organizer console)
+ no `Errors.Instance.NotFound` for internal Login V2 calls (the
`InstanceHostHeaders`/`x-zitadel-public-host` resolution from the existing spec
must still hold on v4.17.1). A green pod is necessary but not sufficient.

**D5 — Retain the `#10103` watchdog.** The notification/projection deadlock is
still unfixed upstream at v4.17.1, so `overlays/prod/cronjob-watchdog-zitadel.yaml`
stays. Only its comment's version reference is updated. Re-evaluate removal in a
future change if/when upstream ships a fix.

## Risks / Trade-offs

- **No dev dry-run** (dev stopped) → mitigate with local render + release-note
  review + backup-before-rollout + approval gate.
- **Forward-only migration** → a failed/partial migration is not cleanly
  reversible by re-pinning; the real safety net is the Cloud SQL backup. Confirm
  it exists before rollout.
- **Vendored-chart drift** → if v4.17.1 needed chart changes, the vendored
  `zitadel-9.34.1` tree would need re-vendoring; detected early via local render
  (none needed).
- **Instance-host-header regression** → v4.17.x could change instance resolution;
  D4's verification explicitly checks for `Errors.Instance.NotFound`.

## Migration Plan

1. Review v4.15.0 → v4.17.1 release notes for config deprecations / required
   changes; confirm no breaking API/config changes affect our values. (done)
2. Edit `base/values.yaml`: API `tag`, `login.image.tag`, OTEL `service.version`
   → `v4.17.1`; refresh stale `v4.14.0` comments. (done)
3. `kustomize build --enable-helm` both overlays; if it fails on v4.17.1, bump
   the vendored chart to a compatible `zitadel-charts` version and re-render.
   (done — renders clean, no chart change)
4. `make lint-k8s` (render + kube-linter) + `make lint-ts`; confirm no `src/**`
   change → no Pulumi diff. (done)
5. Confirm a current prod Cloud SQL backup exists (or take one).
6. **[approval gate]** Operator merges / runs prod `pulumi up`; ArgoCD syncs.
   Watch the setup/migration job to success, then the `zitadel-api` /
   `zitadel-api-login` rollout.
7. Verify (D4): OIDC discovery, hosted Login V2 sign-in (consumer + organizer),
   no `Errors.Instance.NotFound`; watchdog still active.
8. Rollback if needed: re-pin v4.14.0; restore from backup only if the migration
   advanced the schema and v4.14.0 will not boot.
