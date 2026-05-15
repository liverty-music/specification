## 1. Type + Constants Refactor

- [ ] 1.1 `src/config.ts`: narrow `Environment = 'dev' | 'prod' | 'staging'` to `Environment = 'dev' | 'prod'`.
- [ ] 1.2 `src/zitadel/constants.ts`: drop `staging` entry from `baseDomainMap` and `zitadelDomainMap`.
- [ ] 1.3 `src/zitadel/constants.ts`: add `adminOrgIdMap: Record<Environment, string>` exporting `{ dev: '371280364565496672', prod: '372892288692584603' }` (values discovered post-bootstrap via Zitadel admin API, documented in earlier archived changes). Remove the now-superseded `ZITADEL_DEV_ADMIN_ORG_ID` scalar.
- [ ] 1.4 `src/zitadel/components/smtp.ts`: drop `staging` entry from `senderAddressMap`.
- [ ] 1.5 Across `src/gcp/components/postgres.ts`, `src/gcp/components/project.ts`, `src/gcp/components/kubernetes.ts`, `src/gcp/index.ts`: replace inline `'dev' | 'staging' | 'prod'` type annotations with `Environment` imported from `config.ts`.

## 2. Delete Parallel Zitadel Wrapper Classes

- [ ] 2.1 Delete `src/zitadel/components/zitadel-prod-stack.ts` (entire file).
- [ ] 2.2 Delete `src/zitadel/components/backend-machine-key.ts` (entire file).
- [ ] 2.3 Verify no other source files reference the deleted symbols: `grep -rn "ZitadelProdStackComponent\|BackendMachineKeyComponent" src/ test/` returns empty (modulo comments / migration notes if any are retained).

## 3. Refactor the Unified Zitadel Class

- [ ] 3.1 `src/zitadel/index.ts`: remove the `if (env !== 'dev')` throw guard in the constructor.
- [ ] 3.2 `src/zitadel/index.ts`: change `this.adminOrg = new zitadel.Org('admin', ...)` to include `import: adminOrgIdMap[env]` in the resource options.
- [ ] 3.3 `src/zitadel/index.ts`: change `this.e2eTestUser = new E2eTestUserComponent(...)` to be gated by `if (env === 'dev')` (or equivalent ternary if the property type allows `undefined`). Document the gate as "E2E test user is dev-only by product decision, not env-dispatch anti-pattern".
- [ ] 3.4 `src/zitadel/components/e2e-test-user.ts`: remove the `if (env !== 'dev')` throw guard and update the docstring to remove the "Dev-only: the caller must guard..." callout.
- [ ] 3.5 `src/zitadel/components/zitadel-monitoring.ts`: update the docstring to remove "Dev-only" language; document that the component runs in all envs and threshold tuning is a future operational concern.

## 4. Refactor Inline Env-Conditional Blocks

- [ ] 4.1 `src/zitadel/components/frontend.ts`: replace the `if (env === 'dev') redirectUris.push(...)` block with a ternary spread inside the initializer: `const redirectUris = [\`https://${domain}/auth/callback\`, ...(env === 'dev' ? ['http://localhost:9000/auth/callback'] : [])]`. Same for `postLogoutRedirectUris`.
- [ ] 4.2 `src/gcp/components/kubernetes.ts`: replace `if (environment === 'dev') apisToEnable.push('places.googleapis.com')` with unconditional inclusion: `const apisToEnable: GoogleApis[] = ['container.googleapis.com', 'places.googleapis.com']`. Remove the stale "gcp-cost-guardrails" comment.
- [ ] 4.3 `src/index.ts`: collapse the dev/prod Zitadel dispatch (lines 78-125) to a single `const zitadel = new Zitadel('liverty-music', { env, gcpProjectId: \`${brandId}-${env}\`, ... })`. Drop the `let zitadelMachineKey / zitadelLoginPat` declarations — assign directly: `const zitadelMachineKey = zitadel.machineKeyDetails; const zitadelLoginPat = zitadel.loginClientToken`.
- [ ] 4.4 `src/index.ts`: remove the explicit `if (env === 'dev' || env === 'prod')` allowlist on `SecretsComponent` (only two envs exist now after Phase 1; the guard is no-op).

## 5. Remove Dev-Only Resource Guards in gcp/index.ts

- [ ] 5.1 `src/gcp/index.ts`: remove the `if (environment === 'dev')` guard around `ZitadelMonitoringComponent` instantiation. The component runs in any env that has Slack channel ESC seeded.
- [ ] 5.2 `src/gcp/index.ts`: remove the `if (environment === 'dev')` guard around the billing budget. Rename the resource from `dev-cost-budget` to `cost-budget` and `dev-billing-alert-email` to `billing-alert-email`. Add a new optional field `gcpConfig.budgetAmountJpy` (string, e.g., `'3000'`); replace the hardcoded `units: '3000'` with `units: gcpConfig.budgetAmountJpy ?? '3000'` so dev's existing budget shape stays the same.
- [ ] 5.3 `src/gcp/index.ts`: parameterize `MonitoringComponent` cluster targeting. Add inline ternaries (or module-level `Record<Environment, string>` maps) for `clusterName` (dev: `standard-cluster-osaka`, prod: `autopilot-cluster-osaka`) and `clusterLocation` (dev: `asia-northeast2-a` zonal, prod: `asia-northeast2` regional). Pass the env-resolved values into `new MonitoringComponent({...})`.
- [ ] 5.4 `src/gcp/components/project.ts` (GcpConfig interface): add `budgetAmountJpy?: string` field per task 5.2.

## 6. K8s Cluster Refactor (shared config extraction + staging removal)

- [ ] 6.1 `src/gcp/components/kubernetes.ts`: delete the trailing staging cluster block (lines 725-776). The new constructor falls through `if (env === 'dev') { ...Standard... } else { ...Autopilot prod... }`.
- [ ] 6.2 `src/gcp/components/kubernetes.ts`: extract `sharedClusterConfig` as a const inside the constructor (after `this.subnet` is created so it can reference `this.subnet.id`). Fields: `network: networkId`, `subnetwork: this.subnet.id`, `ipAllocationPolicy: { clusterSecondaryRangeName: 'pods-range', servicesSecondaryRangeName: 'services-range' }`, `workloadIdentityConfig: { workloadPool: pulumi.interpolate\`${project.projectId}.svc.id.goog\` }`, `releaseChannel: { channel: 'REGULAR' }`, `costManagementConfig: { enabled: true }`, `gatewayApiConfig: { channel: 'CHANNEL_STANDARD' }`.
- [ ] 6.3 `src/gcp/components/kubernetes.ts`: extract `sharedAutopilotConfig` as a const that spreads `sharedClusterConfig` and adds Autopilot-specific shared fields: `enableAutopilot: true`, `location: region`, `deletionProtection: true`, `clusterAutoscaling: { autoProvisioningDefaults: { serviceAccount: gkeNodeSa.email } }`, `monitoringConfig: { enableComponents: ['SYSTEM_COMPONENTS'], managedPrometheus: { enabled: true } }`.
- [ ] 6.4 `src/gcp/components/kubernetes.ts`: rewrite the prod Autopilot cluster declaration to spread `sharedAutopilotConfig` and add only the prod-specific `databaseEncryption: { state: 'ENCRYPTED', keyName: etcdCmekKeyName }`. The 50-line block of explicit field assignments shrinks to a ~10-line block.
- [ ] 6.5 `src/gcp/components/kubernetes.ts`: rewrite the dev Standard cluster declaration to spread `sharedClusterConfig` and add only the Standard-specific fields (`location: \`${region}-a\``, `deletionProtection: false`, `removeDefaultNodePool: true`, `initialNodeCount: 1`, `privateClusterConfig: { enablePrivateNodes: false, enablePrivateEndpoint: false }`, `monitoringConfig: { enableComponents: ['SYSTEM_COMPONENTS'], managedPrometheus: { enabled: false } }`, `loggingConfig: { enableComponents: ['SYSTEM_COMPONENTS', 'WORKLOADS'] }`). The separate `gcp.container.NodePool` spot pool resource stays unchanged.

## 7. Network Refactor

- [ ] 7.1 `src/gcp/components/network.ts`: **comment out** the staging Cloud NAT block (lines 200-228) with a TODO comment explaining the re-enable conditions: (a) prod migrates to `enablePrivateNodes: true` (NAT becomes mandatory), or (b) staging stack is reintroduced. Include re-enable instructions: uncomment, restore `staging` to `Environment` type, repopulate `senderAddressMap.staging` etc.
- [ ] 7.2 `src/gcp/components/network.ts`: simplify `buildZoneTopology` from `prod` vs `dev/staging` 2-branch to `prod` vs `dev` 2-branch. Update the surrounding comments to remove "dev/staging" references.
- [ ] 7.3 `src/gcp/components/network.ts`: update the `if (environment !== 'prod')` blocks (Postmark Cloud DNS records) — the logic stays the same (only one non-prod env now, `dev`), but the comments can be tightened.

## 8. Verify + Lint

- [ ] 8.1 In `cloud-provisioning/`, run `make lint-ts` — biome + tsc must pass clean.
- [ ] 8.2 `grep -rn "staging" src/` returns only the commented-out Cloud NAT TODO + docstring references documenting why it's commented out. No active code path references `staging`.
- [ ] 8.3 `grep -rn "BackendMachineKeyComponent\|ZitadelProdStackComponent" src/` returns empty.
- [ ] 8.4 `grep -rEn "if \(env" src/` review remaining results: each `if` SHALL be either a structurally-justified branch (cluster mode, DNS provider, folder create vs StackReference, GitHub org-level resources) or the documented `if (env === 'dev')` for `E2eTestUserComponent` instantiation.

## 9. Operator Pre-flight (out-of-band, optional; can defer)

- [ ] 9.1 (Optional) Create a Slack channel for prod backend ERROR log alerts; complete the Slack OAuth flow in GCP Console; record the channel ID.
- [ ] 9.2 (Optional) `esc env set liverty-music/prod pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend "<channel-id>"`. Without this seed, `MonitoringComponent` + `ZitadelMonitoringComponent` stay unmaterialized in prod (same as today; the refactor is no-op for these resources until ESC is seeded).
- [ ] 9.3 (Optional) Decide budget alert email + per-env amount; `esc env set liverty-music/dev pulumiConfig.gcp.billingAlertEmail "<email>"`, `esc env set liverty-music/dev pulumiConfig.gcp.budgetAmountJpy "3000"`; same for prod with a higher amount (recommend 10000 JPY).

## 10. Pulumi Preview + Deploy

- [ ] 10.1 In `cloud-provisioning/`, push the feature branch. Wait for CI: Pulumi preview runs on both dev and prod.
- [ ] 10.2 **Dev preview**: expected = ZERO Zitadel resource changes (the unified class is byte-equivalent to today's dev Zitadel class). Any monitoring/budget changes only appear if §9 ESC seeds were applied to dev.
- [ ] 10.3 **Prod preview**: expected = 9 destroys (`BackendMachineKey$...` subtree) + ~30 creates (unified Zitadel stack + GSM `zitadel-login-pat` + admin org via `import:`) + 1 update on `kubernetes-cluster` (esoOnlySecrets adding `zitadel-login-pat`). NO replaces on backend-app's GSM Secret (it's destroy+create with a new resource name — actually with destroy+create at the SAME GSM Secret name, the underlying GSM hard-deletes and recreates).
- [ ] 10.4 Operator reviews the prod preview output. Highlight the 9 destroys — ensure the backend MachineKey is among them (this triggers the 2-5 min auth outage on apply).
- [ ] 10.5 Merge the PR. The dev `pulumi up` runs automatically via Pulumi Cloud Deployments.
- [ ] 10.6 **Dev verify**: `pulumi stack output --stack dev` shows no Zitadel changes. Backend auth in dev unchanged.
- [ ] 10.7 **Prod manual deploy**: trigger `pulumi up --stack prod` from Pulumi Cloud console (https://app.pulumi.com/pannpers/liverty-music/prod/deployments). Watch the destroy + recreate sequence.
- [ ] 10.8 During prod apply: expect backend → Zitadel auth errors (`Errors.AuthNKey.NotFound`) for 2-5 min. ESO syncs new GSM Secret (~1 min); Reloader rolls backend Deployment (~1 min); new Pods boot with new JWT (~30 sec); auth resumes.

## 11. Smoke Tests (prod post-deploy)

- [ ] 11.1 SPA OIDC sign-in: open `https://liverty-music.app` in a fresh browser, complete OIDC redirect, verify the prod Login V2 UI presents passkey + username/password.
- [ ] 11.2 Sign-up email verification: complete a test sign-up with a disposable inbox; verify the verification email arrives via Postmark within 60s.
- [ ] 11.3 Operator Console: open `https://auth.liverty-music.app/ui/console`, click "Sign in with Google", complete OAuth as `pannpers@pannpers.dev`, verify Console resolves with IAM_OWNER.
- [ ] 11.4 JWT email claim: capture an SPA-issued access token (`localStorage.getItem('access_token')` via DevTools), decode JWT payload, verify `email` claim is present.
- [ ] 11.5 ESO sync: `kubectl get externalsecret -n zitadel zitadel-web-secrets -o yaml --context prod` → `Status=Ready`; `kubectl get secret -n zitadel zitadel-web-pat --context prod` returns non-empty data.
- [ ] 11.6 `zitadel-web` Pod: `kubectl get pods -n zitadel --context prod` → `Running` (1/1 Ready), transitioning out of any prior `ContainerCreating` state.
- [ ] 11.7 Backend Pod auth: `kubectl logs -n backend deployment/server --context prod` shows no recent `Errors.AuthNKey.NotFound`; backend Connect-RPC calls succeed.

## 12. Documentation + Archive

- [ ] 12.1 If §9 was deferred, update `cloud-provisioning/CLAUDE.md` with a note that prod observability + budget are not yet enabled (require ESC seeding when ready).
- [ ] 12.2 Mark all remaining tasks in `openspec/changes/complete-zitadel-prod-pulumi-stack/tasks.md` as `[x]` with the comment `# superseded by refactor-unify-env-dispatch`. (Required because `/opsx:archive` validates `isComplete: true`.)
- [ ] 12.3 Run `openspec validate complete-zitadel-prod-pulumi-stack --strict`. Should pass with all tasks marked done.
- [ ] 12.4 Run `/opsx:archive complete-zitadel-prod-pulumi-stack` (decline the delta→main spec sync prompt — its requirements are superseded; do NOT propagate to main spec).
- [ ] 12.5 Run `openspec validate refactor-unify-env-dispatch --strict`.
- [ ] 12.6 Run `/opsx:archive refactor-unify-env-dispatch`. Accept the delta→main spec sync prompt — this change's delta IS the new source of truth for the affected requirements.
- [ ] 12.7 Bundle both archives + main spec sync into the archive PR per memory `reference_openspec_archive_pattern.md`.
