## 1. Type + Constants Refactor

- [x] 1.1 `src/config.ts`: narrow `Environment = 'dev' | 'prod' | 'staging'` to `Environment = 'dev' | 'prod'`.
- [x] 1.2 `src/zitadel/constants.ts`: drop `staging` entry from `baseDomainMap` and `zitadelDomainMap`.
- [x] 1.3 `src/zitadel/constants.ts`: add `adminOrgIdMap: Record<Environment, string>` exporting `{ dev: '371280364565496672', prod: '372892288692584603' }` (values discovered post-bootstrap via Zitadel admin API, documented in earlier archived changes). Remove the now-superseded `ZITADEL_DEV_ADMIN_ORG_ID` scalar.
- [x] 1.4 `src/zitadel/components/smtp.ts`: drop `staging` entry from `senderAddressMap`.
- [x] 1.5 Across `src/gcp/components/postgres.ts`, `src/gcp/components/project.ts`, `src/gcp/components/kubernetes.ts`, `src/gcp/index.ts`: replace inline `'dev' | 'staging' | 'prod'` type annotations with `Environment` imported from `config.ts`.

## 2. Delete Parallel Zitadel Wrapper Classes

- [x] 2.1 Delete `src/zitadel/components/zitadel-prod-stack.ts` (entire file).
- [x] 2.2 Delete `src/zitadel/components/backend-machine-key.ts` (entire file).
- [x] 2.3 Verify no other source files reference the deleted symbols: `grep -rn "ZitadelProdStackComponent\|BackendMachineKeyComponent" src/ test/` returns empty (modulo comments / migration notes if any are retained).

## 3. Refactor the Unified Zitadel Class

- [x] 3.1 `src/zitadel/index.ts`: remove the `if (env !== 'dev')` throw guard in the constructor.
- [x] 3.2 `src/zitadel/index.ts`: change `this.adminOrg = new zitadel.Org('admin', ...)` to include `import: adminOrgIdMap[env]` in the resource options.
- [x] 3.3 `src/zitadel/index.ts`: change `this.e2eTestUser = new E2eTestUserComponent(...)` to be gated by `if (env === 'dev')` (or equivalent ternary if the property type allows `undefined`). Document the gate as "E2E test user is dev-only by product decision, not env-dispatch anti-pattern".
- [x] 3.4 `src/zitadel/components/e2e-test-user.ts`: remove the `if (env !== 'dev')` throw guard and update the docstring to remove the "Dev-only: the caller must guard..." callout.
- [x] 3.5 `src/zitadel/components/zitadel-monitoring.ts`: update the docstring to remove "Dev-only" language; document that the component runs in all envs and threshold tuning is a future operational concern.

## 4. Refactor Inline Env-Conditional Blocks

- [x] 4.1 `src/zitadel/components/frontend.ts`: replace the `if (env === 'dev') redirectUris.push(...)` block with a ternary spread inside the initializer: `const redirectUris = [\`https://${domain}/auth/callback\`, ...(env === 'dev' ? ['http://localhost:9000/auth/callback'] : [])]`. Same for `postLogoutRedirectUris`.
- [x] 4.2 `src/gcp/components/kubernetes.ts`: replace `if (environment === 'dev') apisToEnable.push('places.googleapis.com')` with unconditional inclusion: `const apisToEnable: GoogleApis[] = ['container.googleapis.com', 'places.googleapis.com']`. Remove the stale "gcp-cost-guardrails" comment.
- [x] 4.3 `src/index.ts`: collapse the dev/prod Zitadel dispatch (lines 78-125) to a single `const zitadel = new Zitadel('liverty-music', { env, gcpProjectId: \`${brandId}-${env}\`, ... })`. Drop the `let zitadelMachineKey / zitadelLoginPat` declarations — assign directly: `const zitadelMachineKey = zitadel.machineKeyDetails; const zitadelLoginPat = zitadel.loginClientToken`.
- [x] 4.4 `src/index.ts`: remove the explicit `if (env === 'dev' || env === 'prod')` allowlist on `SecretsComponent` (only two envs exist now after Phase 1; the guard is no-op).

## 5. Remove Dev-Only Resource Guards in gcp/index.ts

- [x] 5.1 `src/gcp/index.ts`: remove the `if (environment === 'dev')` guard around `ZitadelMonitoringComponent` instantiation. The component runs in any env that has Slack channel ESC seeded.
- [x] 5.2 `src/gcp/index.ts`: remove the `if (environment === 'dev')` guard around the billing budget. Rename the resource from `dev-cost-budget` to `cost-budget` and `dev-billing-alert-email` to `billing-alert-email`. Add a new optional field `gcpConfig.budgetAmountJpy` (string, e.g., `'3000'`); replace the hardcoded `units: '3000'` with `units: gcpConfig.budgetAmountJpy ?? '3000'` so dev's existing budget shape stays the same.
- [x] 5.3 `src/gcp/index.ts`: parameterize `MonitoringComponent` cluster targeting. Add inline ternaries (or module-level `Record<Environment, string>` maps) for `clusterName` (dev: `standard-cluster-osaka`, prod: `autopilot-cluster-osaka`) and `clusterLocation` (dev: `asia-northeast2-a` zonal, prod: `asia-northeast2` regional). Pass the env-resolved values into `new MonitoringComponent({...})`.
- [x] 5.4 `src/gcp/components/project.ts` (GcpConfig interface): add `budgetAmountJpy?: string` field per task 5.2.

## 6. K8s Cluster Refactor (shared config extraction + staging removal)

- [x] 6.1 `src/gcp/components/kubernetes.ts`: delete the trailing staging cluster block (lines 725-776). The new constructor falls through `if (env === 'dev') { ...Standard... } else { ...Autopilot prod... }`.
- [x] 6.2 `src/gcp/components/kubernetes.ts`: extract `sharedClusterConfig` as a const inside the constructor (after `this.subnet` is created so it can reference `this.subnet.id`). Fields: `network: networkId`, `subnetwork: this.subnet.id`, `ipAllocationPolicy: { clusterSecondaryRangeName: 'pods-range', servicesSecondaryRangeName: 'services-range' }`, `workloadIdentityConfig: { workloadPool: pulumi.interpolate\`${project.projectId}.svc.id.goog\` }`, `releaseChannel: { channel: 'REGULAR' }`, `costManagementConfig: { enabled: true }`, `gatewayApiConfig: { channel: 'CHANNEL_STANDARD' }`.
- [x] 6.3 `src/gcp/components/kubernetes.ts`: extract `sharedAutopilotConfig` as a const that spreads `sharedClusterConfig` and adds Autopilot-specific shared fields: `enableAutopilot: true`, `location: region`, `deletionProtection: true`, `clusterAutoscaling: { autoProvisioningDefaults: { serviceAccount: gkeNodeSa.email } }`, `monitoringConfig: { enableComponents: ['SYSTEM_COMPONENTS'], managedPrometheus: { enabled: true } }`.
- [x] 6.4 `src/gcp/components/kubernetes.ts`: rewrite the prod Autopilot cluster declaration to spread `sharedAutopilotConfig` and add only the prod-specific `databaseEncryption: { state: 'ENCRYPTED', keyName: etcdCmekKeyName }`. The 50-line block of explicit field assignments shrinks to a ~10-line block.
- [x] 6.5 `src/gcp/components/kubernetes.ts`: rewrite the dev Standard cluster declaration to spread `sharedClusterConfig` and add only the Standard-specific fields (`location: \`${region}-a\``, `deletionProtection: false`, `removeDefaultNodePool: true`, `initialNodeCount: 1`, `privateClusterConfig: { enablePrivateNodes: false, enablePrivateEndpoint: false }`, `monitoringConfig: { enableComponents: ['SYSTEM_COMPONENTS'], managedPrometheus: { enabled: false } }`, `loggingConfig: { enableComponents: ['SYSTEM_COMPONENTS', 'WORKLOADS'] }`). The separate `gcp.container.NodePool` spot pool resource stays unchanged.

## 7. Network Refactor

- [x] 7.1 `src/gcp/components/network.ts`: **comment out** the staging Cloud NAT block (lines 193-228, including the leading explanatory comment at line 193 so the commented-out block stays self-documenting) with a TODO comment explaining the re-enable conditions: (a) prod migrates to `enablePrivateNodes: true` (NAT becomes mandatory), or (b) staging stack is reintroduced. Include re-enable instructions: uncomment, restore `staging` to `Environment` type, repopulate `senderAddressMap.staging` etc.
- [x] 7.2 `src/gcp/components/network.ts`: simplify `buildZoneTopology` from `prod` vs `dev/staging` 2-branch to `prod` vs `dev` 2-branch. Update the surrounding comments to remove "dev/staging" references.
- [x] 7.3 `src/gcp/components/network.ts`: update the `if (environment !== 'prod')` blocks (Postmark Cloud DNS records) — the logic stays the same (only one non-prod env now, `dev`), but the comments can be tightened.

## 8. Verify + Lint

- [x] 8.1 In `cloud-provisioning/`, run `make lint-ts` — biome + tsc must pass clean.
- [x] 8.2 `grep -rn "staging" src/` returns only the commented-out Cloud NAT TODO + docstring references documenting why it's commented out. No active code path references `staging`.
- [x] 8.3 `grep -rn "BackendMachineKeyComponent\|ZitadelProdStackComponent" src/` returns empty.
- [x] 8.4 `grep -rEn "if \(env" src/` review remaining results: each `if` SHALL be either a structurally-justified branch (cluster mode, DNS provider, folder create vs StackReference, GitHub org-level resources) or the documented `if (env === 'dev')` for `E2eTestUserComponent` instantiation.
- [x] 8.5 **Invariant: `pulumi.secret()` wrap on GSM admin JWT read**: verify the unified `Zitadel` class's GSM `getSecretVersionAccessOutput(...).apply(v => v.secretData)` result is wrapped in `pulumi.secret(...)` BEFORE being passed to `new zitadel.Provider(...).jwtProfileJson`. `grep -A2 "getSecretVersionAccessOutput" src/zitadel/index.ts` must show `pulumi.secret(...)` on the surrounding lines.
- [x] 8.6 **Verify ExternalSecret deletion policy for backend GSM Secret**: read `cloud-provisioning/k8s/namespaces/backend/base/server/external-secret.yaml` (or the equivalent overlay). The `spec.target.deletionPolicy` field controls what ESO does to the K8s Secret if the upstream GSM Secret becomes briefly unavailable during destroy/recreate. If `deletionPolicy: Delete`, the K8s Secret is deleted on upstream-not-found → backend Pod loses its mounted JWT file → backend boot fails. If `deletionPolicy: Retain` (default), the K8s Secret persists with stale-but-valid data through the destroy window → safer. Document the actual value in the PR description before the prod apply. If `Delete`, halt the prod apply and switch to `Retain` in a preceding K8s manifest PR.

## 9. Operator Pre-flight (out-of-band, optional; intentionally deferred)

Tracked as a separate operational follow-up — not part of this archive cycle. The
refactor's code change is no-op for these resources until ESC is seeded, so leaving
them deferred has zero blast radius (gated by `gcpConfig.monitoring?.slackNotificationChannels`
and `gcpConfig.billingAlertEmail` outer guards).

- [ ] 9.1 (Optional, deferred) Create a Slack channel for prod backend ERROR log alerts; complete the Slack OAuth flow in GCP Console; record the channel ID.
- [ ] 9.2 (Optional, deferred) `esc env set liverty-music/prod pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend "<channel-id>"`. Without this seed, `MonitoringComponent` + `ZitadelMonitoringComponent` stay unmaterialized in prod.
- [ ] 9.3 (Optional, deferred) Decide budget alert email + per-env amount; `esc env set liverty-music/dev pulumiConfig.gcp.billingAlertEmail "<email>"`, `esc env set liverty-music/dev pulumiConfig.gcp.budgetAmountJpy "3000"`; same for prod with a higher amount (recommend 10000 JPY).

## 10. Pulumi Preview + Deploy

- [x] 10.1 In `cloud-provisioning/`, push the feature branch. Wait for CI: Pulumi preview runs on both dev and prod.
- [x] 10.2 **Dev preview verification** (claim: zero Zitadel resource changes): the dev preview output SHALL show zero `+ create`, `~ update`, `- delete`, or `+- replace` on any `zitadel:*` or `gcp:secretmanager/*::zitadel-*` URN. Quote the full preview's Resource Changes block in the PR description (or attach as a comment). If the dev preview shows ANY Zitadel-side changes, halt — investigate before any prod apply. The unified class is supposed to be byte-equivalent to today's dev Zitadel class modulo the env guard removal + e2eTestUser conditional + adminOrg `import:` resource option (the last of which is a *one-time hint* that Pulumi ignores once the resource is in state, but a fresh preview against unchanged state should NOT show drift).
- [x] 10.3 **Prod preview verification** (claim: 9 destroys + ~30 creates + 1 update). Specifically check:
  - The 9 `BackendMachineKey$...` URNs are marked `- delete` (not `+- replace`).
  - The new admin org line MUST show `+ create (import)` with the prod admin-org-id `372892288692584603`. If it shows plain `+ create` without `(import)`, Pulumi will attempt to create a NEW admin org named `admin` in Zitadel — abort, fix the `import:` option resolution, re-preview.
  - `kubernetes-cluster` shows a single `~ update` (esoOnlySecrets list grows by 1 entry for `zitadel-login-pat`).
  - No backend-app GSM SecretVersion shows `+- replace` — should be plain `- delete` (under the old Pulumi URN `BackendMachineKey$...`) then `+ create` (under the new Pulumi URN `Zitadel$...`). Two distinct naming layers: (a) the Pulumi logical resource URN CHANGES (new parent type, no `aliases` per D3); (b) the underlying GCP Secret Manager `secretId` stays the SAME (`zitadel-machine-key-for-backend-app`), so the GSM secret is hard-deleted from GCP and immediately recreated with the same GCP identifier in the same apply.
- [x] 10.4 Operator reviews the prod preview output and quotes the full Resource Changes block in the PR description before approving the apply.
- [x] 10.5 Merge the PR. The dev `pulumi up` runs automatically via Pulumi Cloud Deployments.
- [x] 10.6 **Dev verify**: `pulumi stack output --stack dev` shows no Zitadel changes. Backend auth in dev unchanged.
- [x] 10.7 **Prod manual deploy — staged target-apply for safety** (per devil's advocate review C3): instead of a single open-ended `pulumi up --stack prod`, the operator MAY target the destroy phase first via `pulumi destroy --target 'urn:pulumi:prod::liverty-music::zitadel:liverty-music:BackendMachineKey$**' --target-dependents` (or equivalent URN glob in the Pulumi Cloud console's targeted-update UI). Then re-preview to confirm the destroy is clean. Then run an untargeted `pulumi up --stack prod` to create the new unified `Zitadel$...` subtree.
  - **Alternative**: single untargeted apply if the dev preview was clean and the prod preview shows no surprises. The single-apply path saves operator time but couples the two halves into one transaction — if the destroy half partially fails, the create half does not run and the operator must `pulumi up` again from the partially-destroyed state.
- [x] 10.8 **During prod apply**: expect backend → Zitadel auth errors (`Errors.AuthNKey.NotFound`) for 2-5 min. ESO syncs new GSM Secret (~1 min — depends on ExternalSecret `refreshInterval`; verify in §8.6); Reloader rolls backend Deployment (~1 min); new Pods boot with new JWT (~30 sec); auth resumes.
- [x] 10.9 **Rollback plan if Phase 10.7 fails partway** (per devil's advocate review C3): If destroy-phase fails (e.g., Zitadel admin API rejects an OrgMember delete), the old MachineKey may already be invalidated but the new one not yet created. Operator actions:
  - Re-run `pulumi up --stack prod`. Pulumi's destroy+create is idempotent — destroyed resources stay destroyed, missing creates are added.
  - If the new admin org `import:` fails because the previous admin org `protect: true` flag from the deleted state lingers in the Zitadel-side state (unlikely; `protect` is a Pulumi-side flag, not Zitadel-side), unblock by re-running with `--target` exclusion of the admin org until the rest of the stack settles.
  - **Zitadel-side data loss risk**: destroying `zitadel.Org('liverty-music')` cascade-deletes the contained productOrg's projects, machine users, applications inside the Zitadel DB. In current prod state, the productOrg contains only the backend-app MachineUser trio (PR #260's planned additions were never deployed). The cascade is bounded. The new productOrg's resources are recreated by the same apply, with fresh internal Zitadel ids — backend Pod's JWT references the new MachineUser+MachineKey via the GSM Secret. No external system caches productOrg ids.

## 11. Smoke Tests (prod post-deploy)

Verified items as of 2026-05-15 (Pulumi update v157):

- [x] 11.1 Operator Console: opened `https://auth.liverty-music.app/ui/console`, clicked "Sign in with Google", completed OAuth as `pannpers@pannpers.dev`, Console resolved with IAM_OWNER role.
- [x] 11.2 ESO sync: `kubectl get externalsecret -n zitadel zitadel-web-pat` → `Status=Ready`; `kubectl get externalsecret -n backend server-backend-secrets` → `Status=Ready` (both refresh-synced via `force-sync` annotation post-deploy at 07:37:58Z / 07:38:23Z UTC).
- [x] 11.3 `zitadel-web` Pod: `kubectl get pods -n zitadel --context prod` → `Running` (1/1 Ready); transitioned out of the prior 20h `ContainerCreating` state once GSM `zitadel-login-pat` materialized + ESO synced.
- [x] 11.4 Backend Pod auth: backend `server-app` Pod re-rolled by Reloader after K8s Secret update; new Pod booted at 07:38:29Z UTC with the new JWT-profile JSON; recent logs show no `Errors.AuthNKey.NotFound`.
- [x] 11.5 Backend ↔ Zitadel API path: backend `/healthz` HTTPS endpoint at `https://api.liverty-music.app/healthz` returns 401 (auth middleware reachable), proving Gateway + HTTPRoute + JWT-validating middleware all wire through end-to-end.

Items **NOT verified** in this archive cycle (out-of-scope for `refactor-unify-env-dispatch` — blocked on the pre-existing `prod-environment-bootstrap` design D2 follow-up):

- ⏸ SPA OIDC sign-in via `https://liverty-music.app` — blocked because the Cloudflare apex DNS `liverty-music.app` A record is not yet configured. Frontend Pod + HTTPRoute + Gateway are deployed and reachable at the prod static IP `34.110.151.208`; only the apex DNS pointer is missing. Tracked under the `prod-environment-bootstrap` D2 follow-up (Cloudflare apex DNS handled out-of-band, never in Pulumi scope).
- ⏸ Sign-up email verification — blocked on the same apex DNS gap (the SPA is the entry point for sign-up). When the apex resolves, the email path will be verified independently via Postmark dashboard.
- ⏸ JWT `email` claim in SPA-issued access tokens — blocked on the same apex DNS gap. The webhook ActionsV2 wiring + backend `/pre-access-token` endpoint are deployed; the claim path is verifiable via OIDC client flow once the apex resolves.

These deferred items are tracked in [docs/PROD_BOOTSTRAP_DECISIONS.md](docs/PROD_BOOTSTRAP_DECISIONS.md) D2 (apex A record at Cloudflare) and do not affect the success of `refactor-unify-env-dispatch` — the refactor's claim was Pulumi-state correctness + dev parity for prod's Zitadel application stack, all of which is verified post-deploy.

## 12. Documentation + Archive

- [x] 12.1 If §9 was deferred, update `cloud-provisioning/CLAUDE.md` with a note that prod observability + budget are not yet enabled (require ESC seeding when ready).
- [x] 12.2 **Supersession bookkeeping for `complete-zitadel-prod-pulumi-stack`** (per devil's advocate review C9 — do NOT fake-check the unfinished `[ ]` tasks because that pollutes the audit trail with false "done" claims). Approach:
  - Create a new file `openspec/changes/complete-zitadel-prod-pulumi-stack/SUPERSEDED.md` at the change root, stating:
    - This change was merged (spec PR #468) but never deployed to prod Pulumi state.
    - It is **abandoned**, not completed. Tasks marked `[ ]` were not performed.
    - The intent of those tasks (close the 9-component prod Zitadel gap) is realized by `refactor-unify-env-dispatch` via a different implementation shape (unified `Zitadel` class instead of `ZitadelProdStackComponent` wrapper).
    - Date of supersession + commit SHA reference.
  - In `openspec/changes/complete-zitadel-prod-pulumi-stack/tasks.md`, add a header note (under the top-level `## 1.` heading) pointing to `SUPERSEDED.md`. Do NOT change task `[ ]` markers.
- [x] 12.3 `/opsx:archive complete-zitadel-prod-pulumi-stack` may fail `isComplete: true` check because tasks are still `[ ]`. Workaround options (pick one in order of preference):
  - **(a) Use `--force` flag** if `openspec archive` supports it.
  - **(b) Move the change directory manually**: `mv openspec/changes/complete-zitadel-prod-pulumi-stack openspec/changes/archive/YYYY-MM-DD-complete-zitadel-prod-pulumi-stack` (preserving `.openspec.yaml` and `SUPERSEDED.md`). Skip the openspec CLI archive flow for this change.
  - **(c) If neither works**, file a `/opsx:openspec-cli-feature-request` issue for "supersede a change without marking tasks done" and use option (b) in the meantime.
- [x] 12.4 **Do NOT sync `complete-zitadel-prod-pulumi-stack`'s delta to main spec**. Its requirements (4 ADDED, 1 MODIFIED) are superseded by THIS change's spec delta. Syncing would propagate now-incorrect prod-specific requirements into main spec.
- [x] 12.5 Run `openspec validate refactor-unify-env-dispatch --strict`.
- [x] 12.6 Run `/opsx:archive refactor-unify-env-dispatch`. Accept the delta→main spec sync prompt — this change's delta IS the new source of truth for the affected requirements.
- [x] 12.7 Bundle both archive moves + the SUPERSEDED.md creation + the THIS-change main spec sync into one archive PR per memory `reference_openspec_archive_pattern.md`.
