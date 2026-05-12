## 1. Pre-flight

- [x] 1.1 Confirm `self-hosted-zitadel` is archived — verified in `openspec/changes/archive/2026-05-11-self-hosted-zitadel/`
- [x] 1.2 Grep all four repos for unexpected consumers — findings recorded below; **3 artifact gaps surfaced** (see PR pause notes)
- [x] 1.3 Confirm dev ESO `ExternalSecret` `refreshInterval` — `1h` (only one ExternalSecret in `backend/`; consumer shares the same K8s Secret). 24h soak per transitional step (task 4.10) is appropriate (24× refresh interval)
- [ ] 1.4 Coordinate maintenance window scheduling (optional: align with `k8s-naming-cleanup` PR) — deferred to user

## 2. backend-app PR 1 (cp) — Add new GSM secret alongside old

- [x] 2.1 In `cloud-provisioning/src/gcp/index.ts`, add a second secret entry (`name: 'zitadel-machine-key-for-backend-app'`) populated from the same `zitadelMachineKey` output as the existing entry
- [ ] 2.2 Verify `pulumi preview` shows exactly one `+ create` for the new `SecretManagerSecret` and `SecretManagerSecretVersion`, no replacements
- [ ] 2.3 Open PR, description declares `Depends on: none — first step of backend-app migration`
- [ ] 2.4 After merge, monitor `pulumi-cloud-deployments` dev job until apply completes
- [ ] 2.5 Verify both GSM secrets exist: `gcloud secrets versions list zitadel-machine-key` and `gcloud secrets versions list zitadel-machine-key-for-backend-app`

## 3. backend-app PR 2 (be) — Backend reads NEW with fallback to OLD

- [ ] 3.1 In `backend/pkg/config/config.go` Server `Config`, add field `ZitadelMachineKeyForBackendAppPath` with `envconfig:"ZITADEL_MACHINE_KEY_FOR_BACKEND_APP_PATH"`; keep `ZitadelMachineKeyPath` field
- [ ] 3.2 In `backend/pkg/config/config.go` Consumer `Config`, mirror the addition
- [ ] 3.3 In `backend/internal/di/provider.go`, prefer `cfg.ZitadelMachineKeyForBackendAppPath` and fall back to `cfg.ZitadelMachineKeyPath` if the new one is empty
- [ ] 3.4 In `backend/internal/di/consumer.go`, mirror the fallback logic
- [ ] 3.5 Add unit tests covering: (a) new path set → uses new, (b) only old set → uses old, (c) both set → uses new
- [ ] 3.6 Run `make check` and confirm green
- [ ] 3.7 Open PR, description declares `Depends on: backend-app PR 1 (deployed in dev)`
- [ ] 3.8 After merge, verify ArgoCD sync completes and backend pods restart cleanly

## 4. backend-app PR 3 (cp) — Cutover deployment to new path + new env var

- [ ] 4.1 In `cloud-provisioning/k8s/namespaces/backend/base/server/external-secret.yaml`, add a second `data[]` entry mapping `secretKey: zitadel-machine-key-for-backend-app.json` to `remoteRef.key: zitadel-machine-key-for-backend-app`
- [ ] 4.2 In `cloud-provisioning/k8s/namespaces/backend/base/server/deployment.yaml`, add a second `volumes[]` entry + `volumeMounts[]` referencing the new K8s Secret data key; mount path resolves to `/secrets/zitadel/zitadel-machine-key-for-backend-app.json`
- [ ] 4.3 Mirror 4.2 for `k8s/namespaces/backend/base/consumer/deployment.yaml` only. The K8s Secret `backend-secrets` is shared between server and consumer (single `ExternalSecret` in `server/`); no second `ExternalSecret` to update
- [ ] 4.4 In `cloud-provisioning/k8s/namespaces/backend/base/server/configmap.env`, add `ZITADEL_MACHINE_KEY_FOR_BACKEND_APP_PATH=/secrets/zitadel/zitadel-machine-key-for-backend-app.json`; keep `ZITADEL_MACHINE_KEY_PATH` unchanged
- [ ] 4.5 Mirror 4.4 for `consumer/configmap.env`
- [ ] 4.6 Run `kubectl kustomize k8s/namespaces/backend/overlays/dev` and verify both volumes mount, both env vars set, no schema errors
- [ ] 4.7 Run `make lint-k8s` and confirm green
- [ ] 4.8 Open PR, description declares `Depends on: backend-app PR 2 (deployed in dev)`
- [ ] 4.9 After merge, watch ArgoCD sync; verify backend pods restart and logs show successful Zitadel API call (e.g., a sign-up smoke test or `ResendEmailVerification` against a dev user)
- [ ] 4.10 Soak ≥ 24h before progressing to PR 4

## 5. backend-app PR 4 (cp) — Remove old fallback (GSM + ESO + K8s + configmap)

- [ ] 5.1 In `cloud-provisioning/src/gcp/index.ts`, remove the old `name: 'zitadel-machine-key'` secret entry (this destroys the Pulumi-managed `SecretManagerSecretVersion` writer but **leaves the underlying GSM secret intact** until PR 6 removes the resource)
- [ ] 5.2 In `cloud-provisioning/src/index.ts`, leave the `zitadelMachineKey` variable wiring (still needed for the new secret); only remove if all consumers are gone
- [ ] 5.3 In `external-secret.yaml` (server + consumer), remove the old `data[]` entry for `zitadel-machine-key`
- [ ] 5.4 In `deployment.yaml` (server + consumer), remove the old `volumes[]`, `volumeMounts[]`, and `secret.items[]` for `zitadel-machine-key`
- [ ] 5.5 In `configmap.env` (server + consumer), remove `ZITADEL_MACHINE_KEY_PATH`
- [ ] 5.6 Verify `pulumi preview` shows only the expected old-secret-version writer removal (no MachineKey replacement, no destroy of the GSM secret resource itself yet)
- [ ] 5.7 Run `kubectl kustomize` + `make lint-k8s`; confirm green
- [ ] 5.8 Open PR, description declares `Depends on: backend-app PR 3 (deployed in dev ≥ 24h)`
- [ ] 5.9 After merge, monitor ArgoCD sync; verify backend pods restart with only the new env var + new mounted file
- [ ] 5.10 Start the **7-day soak clock**

## 6. backend-app PR 5 (be) — Drop old env var fallback from Go (post-soak)

- [ ] 6.1 Confirm ≥ 7 days have passed since PR 4 merged to dev and no incidents have occurred
- [ ] 6.2 In `backend/pkg/config/config.go`, remove `ZitadelMachineKeyPath` field from both Server `Config` and Consumer `Config`
- [ ] 6.3 In `backend/internal/di/provider.go` and `internal/di/consumer.go`, remove the fallback branch (read only `ZitadelMachineKeyForBackendAppPath`)
- [ ] 6.4 Remove/update tests that exercised the fallback path
- [ ] 6.5 Run `make check`; confirm green
- [ ] 6.6 Open PR, description declares `Depends on: backend-app PR 4 (deployed in dev ≥ 7 days)`
- [ ] 6.7 After merge, verify ArgoCD sync and that backend pods restart cleanly (env var still set, just no longer read as fallback)

## 7. backend-app PR 6 (cp) — Destroy old GSM secret

- [ ] 7.1 In `cloud-provisioning/src/gcp/index.ts`, remove the GSM `SecretManagerSecret` resource declaration for `zitadel-machine-key` entirely (no longer referenced by anyone)
- [ ] 7.2 Verify `pulumi preview` shows exactly one `- destroy` for the old `SecretManagerSecret` and its versions, no other changes
- [ ] 7.3 Open PR, description declares `Depends on: backend-app PR 5 (deployed in dev) — final destroy step, one-way`
- [ ] 7.4 After merge, monitor `pulumi-cloud-deployments` dev job; verify GSM secret no longer present via `gcloud secrets describe zitadel-machine-key` (expected: NOT_FOUND)

## 8. backend-app PR 7 (cp) — Pulumi MachineKey URN rename via aliases

- [ ] 8.1 In `cloud-provisioning/src/zitadel/components/machine-user.ts`, rename `new zitadel.MachineKey('backend-app-key', { ... })` to `new zitadel.MachineKey('machine-key-for-backend-app', { ... })`
- [ ] 8.2 In the same constructor's options object, add `aliases: [{ name: 'backend-app-key' }]` alongside `parent` / `dependsOn` so Pulumi maps the old URN onto the new one
- [ ] 8.3 Run `pulumi preview` and verify the diff shows **only a URN update** on the MachineKey resource — NO `create` / `replace` / `delete` lines on it. If the preview shows a replacement, abort: a misconfigured alias would re-mint the JWT key (§13.15 failure mode). Fix the alias spec before re-attempting
- [ ] 8.4 Open PR, description declares `Depends on: none — parallel-safe with the GSM rename arc`
- [ ] 8.5 After merge, monitor `pulumi-cloud-deployments` dev job; verify the apply completes with the MachineKey shown as an in-place URN update (no resource churn)
- [ ] 8.6 Run a backend → Zitadel API smoke test (e.g., `ResendEmailVerification` against a dev test user) to confirm no `Errors.AuthNKey.NotFound`
- [ ] 8.7 Start the **14-day alias soak clock**

## 9. backend-app PR 8 (cp) — Remove URN alias (post-soak)

- [ ] 9.1 Confirm ≥ 14 days have passed since PR 7 merged to dev and at least one subsequent `pulumi up` has run successfully on the stack
- [ ] 9.2 In `cloud-provisioning/src/zitadel/components/machine-user.ts`, remove the `aliases: [{ name: 'backend-app-key' }]` entry from the `MachineKey` constructor options
- [ ] 9.3 Run `pulumi preview` and verify NO changes to the MachineKey resource (alias removal is a no-op once state is already keyed on the new URN)
- [ ] 9.4 Open PR, description declares `Depends on: backend-app PR 7 (deployed in dev ≥ 14 days)`
- [ ] 9.5 After merge, confirm `pulumi-cloud-deployments` dev apply completes with no MachineKey-related changes

## 10. pulumi-admin PR 1 (cp) — bootstrap-uploader dual-write

- [ ] 10.1 Inspect the `bootstrap-uploader` sidecar in `cloud-provisioning/k8s/namespaces/zitadel/base/deployment-api.yaml` (line ~135: `SECRET_NAME=zitadel-admin-sa-key`). Determine the dual-write mechanism — either (a) change the upload command to write both names sequentially, or (b) add a second env var (e.g., `EXTRA_SECRET_NAME`) consumed by the sidecar script. Implement whichever fits the existing sidecar's command structure. Verify with `kubectl kustomize` that the rendered Pod manifest carries both writes
- [ ] 10.2 In `cloud-provisioning/src/gcp/index.ts` (or wherever the admin-sa GSM secret is declared), declare the new `zitadel-machine-key-for-pulumi-admin` `SecretManagerSecret` resource so Pulumi tracks the resource lifecycle (the value is written by the sidecar, but the resource itself exists in Pulumi state)
- [ ] 10.3 Verify `pulumi preview` shows `+ create` for the new SecretManagerSecret only
- [ ] 10.4 Open PR, description declares `Depends on: none — first step of pulumi-admin migration`
- [ ] 10.5 After merge, trigger a Zitadel pod restart in dev (or wait for natural rotation); verify `bootstrap-uploader` logs show successful write to both GSM names
- [ ] 10.6 Verify `gcloud secrets versions list zitadel-machine-key-for-pulumi-admin` returns at least one version

## 11. pulumi-admin PR 2 (cp) — Pulumi reads NEW GSM secret

- [ ] 11.1 In the `@pulumiverse/zitadel` provider configuration (likely `cloud-provisioning/src/zitadel/index.ts` or equivalent), switch the `jwtProfileJson` source from `zitadel-admin-sa-key` to `zitadel-machine-key-for-pulumi-admin`
- [ ] 11.2 Verify `pulumi preview` resolves the provider auth without error (the new GSM secret must be readable)
- [ ] 11.3 Open PR, description declares `Depends on: pulumi-admin PR 1 (deployed in dev)`
- [ ] 11.4 After merge, confirm `pulumi-cloud-deployments` dev apply completes successfully (proves Pulumi authenticated via the new GSM secret)
- [ ] 11.5 Soak ≥ one successful subsequent Pulumi apply cycle before progressing

## 12. pulumi-admin PR 3 (cp) — Cleanup

- [ ] 12.1 In `bootstrap-uploader` configuration (see 10.1 location), remove the dual-write — write only to `zitadel-machine-key-for-pulumi-admin`
- [ ] 12.2 In `cloud-provisioning/src/gcp/index.ts`, remove the GSM `SecretManagerSecret` resource for `zitadel-admin-sa-key` entirely
- [ ] 12.3 In `cloud-provisioning/src/zitadel/components/secrets.ts`, remove the legacy `zitadel-admin-sa-key` `SecretManagerSecret` declaration + ESO accessor / Zitadel writer IAM bindings (lines ~80, 82, 102, 116)
- [ ] 12.4 In `cloud-provisioning/docs/runbooks/zitadel-break-glass.md`, replace all 12 references to `zitadel-admin-sa-key` with `zitadel-machine-key-for-pulumi-admin` (in `gcloud secrets versions access --secret=...` commands and prose); verify example commands still resolve against the new GSM secret name
- [ ] 12.5 In `cloud-provisioning/src/zitadel/index.ts`, update the `@pulumiverse/zitadel` provider config `secret:` field (line ~162) and update doc comments (lines ~34, 86) to the new name. (If task 11.1 already updated 11.1 the provider config, skip the provider-config step and only update the comments.)
- [ ] 12.6 In `cloud-provisioning/src/zitadel/constants.ts` (line ~75) and `src/index.ts` (lines ~67, 113), update doc comments referencing the old GSM secret name
- [ ] 12.7 Verify `pulumi preview` shows `- destroy` for the old SecretManagerSecret only (no other resource churn)
- [ ] 12.8 Open PR, description declares `Depends on: pulumi-admin PR 2 (deployed in dev ≥ 1 apply cycle) — final destroy step, one-way`
- [ ] 12.9 After merge, verify `gcloud secrets describe zitadel-admin-sa-key` returns NOT_FOUND

## 13. Final verification + cleanup

- [ ] 13.1 Confirm both new GSM secrets exist: `zitadel-machine-key-for-backend-app`, `zitadel-machine-key-for-pulumi-admin`
- [ ] 13.2 Confirm both old GSM secrets are destroyed: `zitadel-machine-key`, `zitadel-admin-sa-key`
- [ ] 13.3 Run `git grep -i 'zitadel-machine-key[^-]'` and `git grep -i 'zitadel-admin-sa-key'` across all four repos; confirm no live references remain (test fixtures and archived docs OK)
- [ ] 13.4 Run a backend → Zitadel API smoke test in dev (e.g., trigger `ResendEmailVerification` against a test user) and confirm success
- [ ] 13.5 Run `pulumi preview` in dev; confirm no drift related to the renamed secrets
- [ ] 13.6 Update operator runbooks if any reference the old GSM secret names
- [ ] 13.7 Run `openspec validate rename-zitadel-machine-keys --strict` and `openspec verify rename-zitadel-machine-keys` before archive
