## 1. Pre-flight

- [x] 1.1 Reviewed release notes v4.15.0 → v4.17.1: **no breaking API/config change** affects our `values.yaml`. Relevant: v4.15.2 fixed setup connection handling after migration steps 40/64/70 (confirms forward-only schema migrations run between v4.14 and v4.17); v4.17.0 DB "skip CREATE USER when role exists" (harmless for our IAM-auth/pre-provisioned users); v4.17.0 #12453 invite-codes-for-auth-method-removed (onboarding benefit).
- [x] 1.2 Vendored chart `zitadel-9.34.1` (appVersion v4.13.1) already renders our v4.14.0 image-tag override; v4.17.1 uses the same decoupling → **no chart bump needed** (confirmed by clean render in 2.5).

## 2. Manifest edit (cloud-provisioning)

- [x] 2.1 `base/values.yaml`: API server image `tag` v4.14.0 → **v4.17.1** (line 15)
- [x] 2.2 Same file: Login V2 UI `login.image.tag` → **v4.17.1** (line 219)
- [x] 2.3 Same file: OTEL `service.version` → **v4.17.1** (line 203)
- [x] 2.4 Refreshed version-reference comments (OTEL capability/404 notes + login-image build note in base; OTEL-404 note in prod `kustomization.yaml`) — restamped to v4.17.1 as version-range/current-pin notes, keeping empirical-on-v4.14.0 facts honest. NOTE: the `#10103` watchdog CronJob was already removed on `main` (c29837f), so there is no watchdog file/comment to edit — the upgrade does not reintroduce it
- [x] 2.5 `kubectl kustomize --enable-helm` renders **prod AND dev** cleanly; both `zitadel` and `zitadel-login` images render at `v4.17.1`, OTEL label `service.version=v4.17.1`. No chart change required

## 3. Local validation

- [x] 3.1 `make lint-k8s` (render + kube-linter + spot check) passes — "No lint errors found", all workloads have Spot nodeSelector
- [x] 3.2 `make lint-ts` passes (biome + tsc clean; no TS touched)
- [x] 3.3 No `src/**` changes → **zero Pulumi resource diff** (image tag is an ArgoCD-deployed manifest value, not a Pulumi resource). The prod PR's CI runs `pulumi preview` to confirm no diff

## 4. Prod rollout (approval-gated — dev is stopped, so prod-direct)

- [x] 4.1 Pre-upgrade **on-demand Cloud SQL backup taken** for `postgres-osaka` (backup id `1787455349519`, 2026-08-23T03:22:29Z, SUCCESSFUL; latest automated 2026-08-22T18:00 also present)
- [x] 4.2 Merged cloud-provisioning **PR #444** (`568c899`) after operator approval → ArgoCD (auto-sync) synced the prod overlay to `568c899`
- [x] 4.3 The chart `zitadel-api-setup` **schema-migration job re-ran and completed** (13s; log `setup completed version=v4.17.1`) before `zitadel-api` became ready; `zitadel-api-init` + `zitadel-db-grant` also Complete
- [x] 4.4 `zitadel-api` (2/2) and `zitadel-api-login` (1/1) Deployments rolled to **`v4.17.1`**, pods Running, old pods terminated; `rollout status` successful

## 5. Post-upgrade verification (prod)

- [x] 5.1 `…/.well-known/openid-configuration` returns `issuer=https://auth.liverty-music.app` ✅; `/debug/healthz` HTTP 200
- [x] 5.2 Hosted Login V2 real end-to-end sign-in **confirmed** for the **consumer** app (user-verified 2026-08-23 on v4.17.1)
- [x] 5.3 Hosted Login V2 real end-to-end sign-in **confirmed** for the **organizer console** (org-pinned passkey → `/welcome`, user-verified 2026-08-23 on v4.17.1)
- [x] 5.4 API logs show **0** `Errors.Instance.NotFound` for cluster-internal Login V2 calls on the new pods (the `x-zitadel-public-host` resolution holds on v4.17.1 — the old prod-504 risk is clear)
- [x] 5.5 Confirmed the upgrade did **not** reintroduce the `#10103` watchdog CronJob (none present); wedge recovery remains `kubectl rollout restart deploy/zitadel-api`
- [x] 5.6 Rollback path validated on paper: re-pin v4.14.0 (+ restore from backup `1787455349519` only if the schema advanced and v4.14.0 will not boot)

## 6. Close-out

- [x] 6.1 Updated memory: prod upgraded v4.14.0→v4.17.1 2026-08-23; corrected the stale "watchdog stays" index line (watchdog was removed cp#429, not retained)
- [x] 6.2 Archive the change once prod is verified (verify-before-archive → `/opsx:archive`)
