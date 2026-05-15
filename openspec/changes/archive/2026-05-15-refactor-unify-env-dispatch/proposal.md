## Why

The `cloud-provisioning` codebase has accumulated three classes of env-dispatch anti-patterns that compound maintenance cost:

1. **Parallel "prod-only" classes**: `ZitadelProdStackComponent` (from `complete-zitadel-prod-pulumi-stack`) and `BackendMachineKeyComponent` (from `enable-zitadel-prod-pulumi-provider`) each clone the dev `Zitadel` class with subset config. The 9-component instantiation block in each is almost byte-identical, drift-prone, and forces every future Zitadel-side change to be applied in two places.
2. **Inline `if (env === 'dev')` blocks where ternaries / env-keyed maps suffice**: scattered through `frontend.ts` (localhost redirect URIs), `kubernetes.ts` (places API), `gcp/index.ts` (billing budget + ZitadelMonitoring), `index.ts` (SecretsComponent), `zitadel/components/e2e-test-user.ts` (env guard). The leaf components already accept `env` and switch via `Record<Environment, T>` maps internally — the wrappers fight that grain.
3. **Stale staging code paths**: `staging` branches exist in `network.ts` (Cloud NAT), `kubernetes.ts` (staging cluster block), `constants.ts` (env-keyed maps), `smtp.ts` (sender address map). No staging stack exists today and none is planned in the near term, so the staging code is unreached and unreached-tested. The user-clarified policy: **staging is dropped from the near-term plan**; keep Cloud NAT only as commented-out scaffolding for likely future re-introduction.

Discovered during attempted operator-deploy of `complete-zitadel-prod-pulumi-stack`: the parallel-class pattern blocked us via two separate problems — (a) Pulumi `pulumi import` CLI required a pre-existing provider URN that didn't exist for the wrapped prod component (hotfix #261 worked around with `import:` resource option), and (b) the duplicated 9-component instantiation made the divergence between dev and prod hard to reason about and led to a runaway-spec-divergence cluster (redirect URI mismatch, ESC entries fabricated, etc.). The user's pre-launch directive — *"破壊的な変更をするのはサービスイン前のこのタイミングが最適です"* — makes this the right moment for a destructive cleanup.

This change supersedes `complete-zitadel-prod-pulumi-stack` (which was merged but has never been deployed to prod state). The prod Zitadel application stack will be delivered by THIS change instead, with the unified `Zitadel` class as the single source of truth.

## What Changes

### Code deletions

- **DELETE** `cloud-provisioning/src/zitadel/components/zitadel-prod-stack.ts` (~370 lines)
- **DELETE** `cloud-provisioning/src/zitadel/components/backend-machine-key.ts` (~210 lines)
- **DELETE** staging-specific cluster block in `cloud-provisioning/src/gcp/components/kubernetes.ts` (lines 725-776)
- **COMMENT OUT** (not delete) the staging-only Cloud NAT block in `cloud-provisioning/src/gcp/components/network.ts` (lines 193-228) — re-introduction is planned in the near future when private nodes return to prod or when staging stack is created. Inline TODO with re-enable instructions.

### Code modifications

- **MODIFY** `cloud-provisioning/src/config.ts`: `Environment = 'dev' | 'prod'` (drop `'staging'`).
- **MODIFY** `cloud-provisioning/src/zitadel/index.ts`: remove the `if (env !== 'dev')` throw guard; `Zitadel` class supports all envs. Inline ternary for the `adminOrg.import` value (`adminOrgIdMap[env]`). Conditional create of `E2eTestUserComponent` only when `env === 'dev'`.
- **MODIFY** `cloud-provisioning/src/zitadel/constants.ts`: drop `staging` entry from `baseDomainMap` and `zitadelDomainMap`; replace scalar `ZITADEL_DEV_ADMIN_ORG_ID` with `adminOrgIdMap: Record<Environment, string>` covering both dev and prod admin-org-ids.
- **MODIFY** `cloud-provisioning/src/zitadel/components/frontend.ts`: localhost redirect URIs via ternary spread (`...(env === 'dev' ? ['http://localhost:9000/auth/callback'] : [])`), not `if` push.
- **MODIFY** `cloud-provisioning/src/zitadel/components/e2e-test-user.ts`: remove the `if (env !== 'dev')` throw guard and docstring "Dev-only" callout — the caller (`Zitadel` class) gates instantiation via `if (env === 'dev')`, the component itself is env-agnostic.
- **MODIFY** `cloud-provisioning/src/zitadel/components/smtp.ts`: drop `staging` from `senderAddressMap`.
- **MODIFY** `cloud-provisioning/src/zitadel/components/zitadel-monitoring.ts`: docstring update — remove "Dev-only" callout; the component now runs in all envs.
- **MODIFY** `cloud-provisioning/src/gcp/components/network.ts`: comment out staging Cloud NAT block (re-enable instructions in comment); simplify `buildZoneTopology` to `prod` vs `dev` 2-way branch (was `prod` vs `dev/staging`); update comments throughout.
- **MODIFY** `cloud-provisioning/src/gcp/components/kubernetes.ts`: delete staging cluster block; extract `sharedClusterConfig` (network, subnet, ipAllocationPolicy, workloadIdentityConfig, releaseChannel, costManagementConfig, gatewayApiConfig) and `sharedAutopilotConfig` (extends `sharedClusterConfig` with Autopilot-specific shared fields) into module-level consts; spread into each cluster declaration. Places API enabled for all envs via ternary spread (was `if (env === 'dev')`). Drop stale "gcp-cost-guardrails" comment.
- **MODIFY** `cloud-provisioning/src/gcp/components/postgres.ts`, `src/gcp/components/project.ts`: standardize inline `'dev' | 'staging' | 'prod'` type annotations to import `Environment` from `config.ts`.
- **MODIFY** `cloud-provisioning/src/gcp/index.ts`: remove `if (environment === 'dev')` guard around `ZitadelMonitoringComponent`; remove the same guard around billing budget (rename resource from `dev-cost-budget` to `cost-budget` — name is naturally env-scoped via Pulumi stack). Parameterize `MonitoringComponent` instantiation: `clusterName` + `clusterLocation` driven by env-keyed map (`clusterNameByEnv`, `clusterLocationByEnv`) so log-based alerts target the correct cluster in each env.
- **MODIFY** `cloud-provisioning/src/index.ts`: collapse the dev/prod Zitadel dispatch into a single `new Zitadel('liverty-music', { env, ... })` line; remove the explicit `if (env === 'dev' || env === 'prod')` allowlist on `SecretsComponent` (apply to all envs — there are only dev and prod now); both `zitadelMachineKey` and `zitadelLoginPat` flow through `Gcp` for both envs (the prod path's `BackendMachineKeyComponent`-owned GSM Secret is replaced by `Gcp.KubernetesComponent.esoOnlySecrets`, matching the dev pattern).

### Pulumi state migration: destroy + recreate (no aliases)

The currently-deployed prod state from `enable-zitadel-prod-pulumi-provider` (commit `47b1b47`, deployed 2026-05-14) places the backend MachineKey subtree under `BackendMachineKeyComponent`. After this refactor it lives under the unified `Zitadel` class with dev-style naming (`liverty-music-provider`, `MachineUserComponent("liverty-music")`). Per the user's explicit guidance — *"alias については、一度、削除して作り直すのでもOK。コードがシンプルになってメンテナンス性が高い方法を優先して"* — this change does NOT carry Pulumi `aliases` to preserve the old URNs. The 9 prod-side resources are destroyed and recreated under the new URNs on the first `pulumi up --stack prod` of this change.

Practical impact: a 2-5 minute window during the prod apply where backend → Zitadel JWT auth fails (old `MachineKey.kid` invalidated before the new one propagates through GSM → ESO → K8s Secret → Reloader → Pod restart). Pre-launch prod has zero real users; the impact is bounded to error logs.

### Operator pre-flight (out of scope for code, in scope for tasks.md)

Prod ESC must be seeded with two additional values before the first `pulumi up --stack prod` of this change unlocks `MonitoringComponent` + `ZitadelMonitoringComponent` end-to-end:

- `pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend` — Slack channel ID (created out-of-band in GCP Console because the API requires Slack OAuth; same pattern as `liverty-music-dev` already uses).
- `pulumiConfig.gcp.billingAlertEmail` — recipient for Cloud Billing Budget alerts (decide threshold; recommend not seeding `dev` either, since current `dev` ESC also lacks this and the dev budget is currently dormant — so the refactor is no-op until ESC is seeded).

These are documented as pre-flight tasks. The code change without them produces a clean preview (the inner `if (gcpConfig.monitoring?.slackNotificationChannels)` and `if (gcpConfig.billingAlertEmail)` guards remain).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `zitadel-self-hosted-deployment`: **REMOVE** the requirement "Prod Backend MachineKey Component Authenticates with Bootstrap-Uploaded Admin JWT" — its content is absorbed into a unified requirement covering both envs. **REMOVE** the requirement "Backend MachineUser Placed in Product Org, Not the First-Boot Admin Org" — superseded by a unified product-org requirement applied to all envs. **MODIFY** several existing requirements to drop "dev only" / "prod scope" language and reflect dev-prod parity. **ADD** a requirement establishing the "unified `Zitadel` class for all envs" pattern as the canonical implementation.

## Impact

- **`cloud-provisioning/src/` net diff**: ~580 lines deleted, ~250 lines modified, ~50 lines added (sharedClusterConfig, adminOrgIdMap, env-keyed monitoring maps).
- **Dev Pulumi state**: zero churn. The unified `Zitadel` class is byte-identical to today's dev class with the `env !== 'dev'` throw removed. Dev URNs do not change.
- **Prod Pulumi state**: 9 `BackendMachineKey$...` resources destroyed; ~30 new `Zitadel$...` resources created (the 9 originals re-created under new URNs + Project + Frontend + Smtp + ActionsV2 + LoginClient + GoogleAdminIdp + AdminOrgConfig + HumanAdmin + admin-org import + GSM `zitadel-login-pat` Secret bundle). The admin org is imported via `import:` resource option (same id `372892288692584603` already discovered).
- **Operational unblocks** after deploy: prod SPA OIDC sign-in, sign-up email verification, operator Google IdP Console access, JWT `email` claim, prod ZitadelMonitoring (latency p99 + JWT error rate alerts), prod billing budget (once ESC seeded).
- **Operator-attended window**: 2-5 minutes prod backend ↔ Zitadel auth failure during destroy-recreate; pre-launch prod is no-traffic, impact is bounded to error logs.
- **Supersession bookkeeping**: `openspec/changes/complete-zitadel-prod-pulumi-stack/` (active, never deployed) is archived as part of this change's archive step with a clear `superseded by refactor-unify-env-dispatch` note. The redirect-URI doc errors and `pulumi import` CLI workaround in that change become historical context; this change's spec delta is the new source of truth.
- **Out of scope**: backend Atlas migration prod overlay, frontend `.env.prod`, Cloudflare apex `liverty-music.app` A record (carried forward from `complete-zitadel-prod-pulumi-stack` proposal — same separate-PR follow-ups). E2eTestUserComponent for prod (still deferred per the original `enable-zitadel-prod-e2e-user` plan). Staging stack adoption (out of near-term plan; Cloud NAT scaffolding preserved as commented-out for easy re-introduction).
