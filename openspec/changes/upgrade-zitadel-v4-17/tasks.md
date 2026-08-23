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

- [ ] 4.1 Confirm a current prod Cloud SQL automated backup exists for `liverty-music-prod:asia-northeast2:postgres-osaka` (or take an on-demand backup) BEFORE rollout
- [ ] 4.2 **[operator approval]** Merge the cloud-provisioning PR → ArgoCD syncs the prod overlay (operator performs the merge; do not trigger unattended)
- [ ] 4.3 Watch the chart init/setup **schema-migration job** to success against prod Cloud SQL; confirm `zitadel-api` becomes ready only after it completes
- [ ] 4.4 Confirm the `zitadel-api` and `zitadel-api-login` Deployments roll to `v4.17.1` (pods Running, images updated)

## 5. Post-upgrade verification (prod)

- [ ] 5.1 `https://auth.liverty-music.app/.well-known/openid-configuration` returns the discovery document with `issuer=https://auth.liverty-music.app`
- [ ] 5.2 Hosted Login V2 real end-to-end sign-in succeeds for the **consumer** app
- [ ] 5.3 Hosted Login V2 real end-to-end sign-in succeeds for the **organizer console** (org-pinned passkey login → `/welcome`)
- [ ] 5.4 API logs show NO `Errors.Instance.NotFound` for cluster-internal Login V2 calls (the `InstanceHostHeaders` / `x-zitadel-public-host` resolution still holds on v4.17.1)
- [ ] 5.5 Confirm the upgrade did not reintroduce the (previously-removed) `#10103` watchdog CronJob; the documented wedge recovery remains `kubectl rollout restart deploy/zitadel-api`
- [ ] 5.6 Rollback path validated on paper: re-pin v4.14.0 (+ restore-from-backup only if the schema advanced and v4.14.0 will not boot)

## 6. Close-out

- [ ] 6.1 Update memory / notes with the shipped version + any config deltas found
- [ ] 6.2 Archive the change once prod is verified (verify-before-archive → `/opsx:archive`)
