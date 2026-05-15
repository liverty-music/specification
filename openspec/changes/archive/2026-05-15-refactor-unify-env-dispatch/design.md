## Context

`cloud-provisioning` has three architectural debts that compound each other:

1. **Two parallel "prod-only" Zitadel wrapper classes**: `BackendMachineKeyComponent` (one-component prod wrapper from `enable-zitadel-prod-pulumi-provider`, archived 2026-05-14) and `ZitadelProdStackComponent` (nine-component prod wrapper from `complete-zitadel-prod-pulumi-stack`, merged but never deployed). Each clones the dev `Zitadel` class with a subset of components. The 9-component instantiation block is almost byte-identical between dev's `Zitadel` and prod's `ZitadelProdStackComponent` — every Zitadel-side change must be applied in two places, with no compiler-level guarantee they stay in sync. The pattern was an over-application of "BackendMachineKeyComponent is a parallel class" to a 9-component context where the duplication cost crossed acceptable threshold.

2. **`if (env === 'dev') { ... }` blocks where ternary / env-keyed map would suffice**: scattered through `frontend.ts`, `kubernetes.ts`, `gcp/index.ts`, `index.ts`, `e2e-test-user.ts`. The leaf components already accept `env` and switch internally via `Record<Environment, T>` maps (`baseDomainMap`, `zitadelDomainMap`, `senderAddressMap`). The wrappers fight that grain by re-doing env-dispatch at the call-site.

3. **Stale staging code paths**: `staging` branches exist in `network.ts` (Cloud NAT block), `kubernetes.ts` (staging cluster block), env-keyed maps. No staging stack exists today; the staging code has never been exercised by `pulumi up`. Per the user's clarification, **staging is dropped from the near-term plan**.

The trigger for this cleanup: while operator-deploying `complete-zitadel-prod-pulumi-stack` for prod, two compound problems surfaced — (a) `pulumi import` CLI required a pre-existing provider URN that the wrapper class hadn't yet materialized (hotfix #261 worked around with `import:` resource option), and (b) the parallel-class pattern made the divergence between dev and prod hard to reason about, leading to a runaway-spec-divergence cluster (redirect URI mismatch, fabricated ESC entries, etc.). The user's explicit pre-launch directive — *"破壊的な変更をするのはサービスイン前のこのタイミングが最適です"* — makes this the right moment for a destructive cleanup.

Stakeholders:
- **Operator** (`pannpers@pannpers.dev`): wants a clean codebase to maintain going forward; tolerates a 2-5 min prod auth outage pre-launch in exchange.
- **Future contributors**: benefit from a single source of truth for Zitadel topology (the unified `Zitadel` class) and the principle "`if (env === ...)` only for fundamental structural differences like DNS".
- **Pulumi state**: prod loses 9 URNs and gains ~30 new URNs in a single apply. Dev is byte-identical.

## Goals / Non-Goals

**Goals:**

- Delete `BackendMachineKeyComponent` and `ZitadelProdStackComponent`. Unify into the existing `Zitadel` class with env guards relaxed.
- Drop `staging` from the `Environment` type and all code paths. Cloud NAT block in `network.ts` is **commented out** (not deleted) because near-future re-introduction is anticipated.
- Establish the **canonical pattern**: env-driven differences expressed via ternary or env-keyed `Record<Environment, T>` map. `if (env === ...)` is reserved for *structural* differences — fundamentally different resource types (Autopilot vs Standard cluster, DNS-provider routing, folder-create vs StackReference-import).
- Apply dev-only observability + cost-guardrail resources to all envs by removing the inner `if (env === 'dev')` guards. The outer guards (`gcpConfig.monitoring?.slackNotificationChannels`, `gcpConfig.billingAlertEmail`) still control whether the resources materialize — ESC seeding is the gate, not a code branch.
- Extract `sharedClusterConfig` from the K8s cluster blocks to eliminate copy-paste of network/IAM/Gateway config across Autopilot and Standard.
- Fix discovered bugs: `MonitoringComponent` clusterName hardcoded to dev's `standard-cluster-osaka` (prod would target the wrong cluster); staging cluster missing `gatewayApiConfig` + `monitoringConfig` (dormant bug since staging is never deployed, but worth fixing on the way out).

**Non-Goals:**

- Carry Pulumi `aliases` to preserve old prod URNs. Per user direction, simpler code is preferred over zero-downtime migration. The 2-5 min prod auth outage is acceptable pre-launch.
- Refactor the dev `Zitadel` class's internal structure. Other than removing the `env !== 'dev'` guard and adding the `e2eTestUser` conditional, the class stays as-is. Dev URNs remain byte-identical.
- ESC seeding (Slack channel ID, billing alert email). Operator-attended pre-flight; documented in tasks.md.
- Cross-repo follow-ups carried forward from `complete-zitadel-prod-pulumi-stack`: backend Atlas migration prod overlay, frontend `.env.prod`, Cloudflare apex A record.
- E2eTestUserComponent for prod (still deferred per `enable-zitadel-prod-e2e-user` plan).

## Decisions

### D1 — Drop `staging` from the `Environment` type; comment out the Cloud NAT block for future re-introduction

**Decision:** `Environment = 'dev' | 'staging' | 'prod'` → `Environment = 'dev' | 'prod'`. All `if (env === 'staging')` blocks deleted (or commented out where re-introduction is anticipated). The `staging` cluster block in `kubernetes.ts:725-776` is **deleted** outright (staging cluster has never been deployed and its code has dormant bugs). The Cloud NAT block in `network.ts:193-228` (including the leading explanatory comment at line 193 so the commented-out block stays self-documenting) is **commented out** with a TODO referencing the conditions under which it should be re-enabled (private nodes returning to prod, or staging stack adoption).

**Rationale:**

- No staging stack exists today and no near-term plan to add one.
- Keeping unreached staging branches with subtle bugs (missing `gatewayApiConfig`, missing `monitoringConfig`, etc.) is worse than deleting them — the next dev to add staging will fix them anyway and may be confused by the partially-broken existing code.
- Cloud NAT specifically is anticipated to return when (a) prod migrates to private nodes (currently public for cost reasons; flip "when real users arrive" per `docs/PROD_BOOTSTRAP_DECISIONS.md` D6), or (b) staging is reintroduced. Commenting it out — rather than deleting — preserves the block as ready-to-uncomment scaffolding while keeping the active codebase env-clean.
- **Alternative considered (rejected): keep `Environment` union as-is, only delete the if-branches.** Cost: `Record<Environment, T>` maps still need `staging` entries (drift risk). TypeScript exhaustiveness checks still surface `staging` cases. The user explicitly asked for "条件分岐を一緒に削除", which only works if the type is also tightened. Net: tighten the type.

### D2 — Delete the two parallel Zitadel wrapper classes; unify into the existing `Zitadel` class

**Decision:** Delete `BackendMachineKeyComponent` and `ZitadelProdStackComponent` files. Remove the `if (env !== 'dev')` throw from `Zitadel`'s constructor. Move the prod-side `adminOrg` import-id from a class-specific hardcode to a shared `adminOrgIdMap: Record<Environment, string>` consumed via ternary inside the unified class.

**Rationale:**

- The 9 components instantiated in `ZitadelProdStackComponent` are byte-identical (modulo arg names) to those instantiated in `Zitadel`. The duplication has no functional benefit and creates drift risk on every future Zitadel-side change.
- The `if (env !== 'dev')` throw was a defensive guard from when `Zitadel` was the dev-only cutover artifact (per `add-zitadel-console-admin-via-google-idp`, archived 2026-05-08). Post-cutover, dev's component leaves are all env-parameterized via maps and component args — removing the guard surfaces no behavioral risk.
- The `BackendMachineKeyComponent` justification ("prod needs only backend-app, parallel class keeps it minimal") was a reasonable judgment when prod needed 1 component. It does not scale to 9 components, and the precedent it set ("parallel class for env") propagated to `ZitadelProdStackComponent`'s anti-pattern.
- **Alternative considered (rejected): keep `BackendMachineKeyComponent` as a "compose-over-inline" sub-component inside `Zitadel`.** This was the original `complete-zitadel-prod-pulumi-stack` D9 decision. Cost: still requires `parent: this` + `aliases: [{ parent: pulumi.rootStackResource }]` plumbing on the inner class, plus a `backendMachineKey.adminJwt` re-export hack to share the GSM read. Benefit: would preserve some prod state URNs. Net: rejected because the user explicitly preferred simpler code (D3 below) over state preservation.

### D3 — Destroy + recreate prod state (no `aliases`); accept 2-5 min auth outage

**Decision:** Do not carry Pulumi `aliases: [{ parent: pulumi.rootStackResource }, { name: 'old-name' }]` to preserve the 9 prod URNs currently deployed under `BackendMachineKeyComponent`. The first `pulumi up --stack prod` of this change destroys those 9 resources and recreates them under the unified `Zitadel` class's URNs (with dev-style naming: provider `liverty-music-provider`, machine-user-component `liverty-music`).

**Rationale:**

- Per user explicit direction: *"alias については、一度、削除して作り直すのでもOK。コードがシンプルになってメンテナンス性が高い方法を優先して"* — simpler code is preferred over state preservation.
- The alias-based approach would have required ~9 alias entries scattered through `Zitadel` class plumbing, plus careful handling of name changes that don't fit Pulumi's alias-on-parent-propagation model (provider name change `zitadel-prod` → `liverty-music-provider`, MachineUserComponent name change `backend-app-prod` → `liverty-music` — both require explicit `name` aliases that do not propagate to children).
- **Pre-launch traffic shape**: prod has zero real users today. The 2-5 min window where the `backend` Pod's mounted JWT-profile JSON points at an invalidated `MachineKey.kid` produces error logs but no user-facing impact. ESO re-syncs the new GSM SecretVersion (~1 min), Reloader rolls the backend Deployment (~1 min), Pods boot with the new JWT (~30 sec).
- **Risk if accepted post-launch**: would NOT be acceptable. This is the destructive-pre-launch window working in our favor.
- **Alternative considered (rejected): preserve URNs via aliases.** Cost: ~50 lines of alias plumbing in the unified `Zitadel` class, fragile to future Pulumi version changes, has to be removed in a follow-up PR after the first apply lands (per Pulumi guidance). Benefit: zero prod auth outage. Net: rejected on the user's explicit code-simplicity preference.

### D4 — Apply dev-only resources to all envs by removing inner `if (env === 'dev')` guards; outer ESC presence checks remain

**Decision:** Three resources currently dev-only inside `gcp/index.ts` lose their `if (environment === 'dev')` guards:

- `ZitadelMonitoringComponent` (latency p99 + JWT error rate alerts + connection-pool dashboard)
- `gcp.billing.Budget` (`dev-cost-budget` → renamed `cost-budget`)
- `MonitoringComponent`'s `ZitadelMonitoringComponent` sub-instantiation

Plus one in `src/index.ts`: `SecretsComponent` instantiation loses its `if (env === 'dev' || env === 'prod')` allowlist (only two envs exist now, so the guard is no-op anyway — drop it for clarity).

The OUTER guards remain:
- `if (gcpConfig.monitoring?.slackNotificationChannels)` — gates the whole `MonitoringComponent` chain on Slack ESC seeding
- `if (gcpConfig.billingAlertEmail)` — gates the `gcp.billing.Budget` on the alert-email ESC seeding

These outer guards now serve a single purpose: "is this env's ESC seeded with the required value?" — pure data-driven, no env hardcoding.

**Rationale:**

- The dev thresholds in `ZitadelMonitoringComponent` are deliberately generous (50× over steady-state for latency p99, 10 errors / 60s for JWT). They will not page on the pre-launch prod traffic shape; if they become noisy later, threshold tuning is a separate concern.
- The billing budget needs DIFFERENT amount values per env (dev: ¥3000, prod: TBD by operator). However, the dev billing budget is currently *dormant* — `gcpConfig.billingAlertEmail` is unset in dev ESC, so the inner `if` evaluates false and no Budget resource exists in dev state today. Refactoring to "all envs" is effectively no-op until ESC is seeded. When seeded, the budget amount is read from `gcpConfig.budgetAmountJpy` (new field) — per-env value seeded by operator.
- **Resource renames (two of them, both env-prefix removal)**: `dev-cost-budget` → `cost-budget` and `dev-billing-alert-email` → `billing-alert-email`. Env-prefix removal follows D8 (Pulumi stack URN already disambiguates env). Pulumi state impact: zero — both resources are currently DORMANT in dev state (the inner `if (gcpConfig.billingAlertEmail)` evaluates false today, so neither resource exists in any stack state), so the rename triggers no destroy+create operation. If the operator seeds `billingAlertEmail` in ESC *after* the refactor lands, the resources are created under the new (un-prefixed) names directly.
- **`MonitoringComponent` parameterization for env-correct cluster targeting**: `gcp/index.ts:324-327` currently hardcodes `clusterLocation: ${Regions.Osaka}-a` (zonal — dev-only) and `clusterName: standard-cluster-osaka` (dev-only). For prod the cluster is regional (`asia-northeast2`) and named `autopilot-cluster-osaka`. Without parameterization, prod alerts would silently target log entries from the dev cluster — a real bug. The fix is two new env-keyed maps in `constants.ts`-equivalent location (or inline ternaries):
  ```ts
  const clusterNameByEnv: Record<Environment, string> = {
    dev: `standard-cluster-${RegionNames.Osaka}`,
    prod: `autopilot-cluster-${RegionNames.Osaka}`,
  }
  const clusterLocationByEnv: Record<Environment, string> = {
    dev: `${Regions.Osaka}-a`,   // zonal
    prod: Regions.Osaka,         // regional
  }
  ```

### D5 — Extract `sharedClusterConfig` for K8s cluster declarations; keep `if (env === 'dev')` only for the structural mode difference

**Decision:** Pull out a module-level `sharedClusterConfig` const containing fields identical across all envs (network, subnet, ipAllocationPolicy, workloadIdentityConfig, releaseChannel, costManagementConfig, gatewayApiConfig). Spread it into both the dev (Standard) and prod (Autopilot) cluster declarations. Extract a further `sharedAutopilotConfig` const (extends `sharedClusterConfig` with `enableAutopilot: true`, `location: region` regional, `deletionProtection: true`, `clusterAutoscaling.autoProvisioningDefaults`, `monitoringConfig` with `enableComponents: ['SYSTEM_COMPONENTS']` + `managedPrometheus.enabled: true`).

The `if (env === 'dev')` / `else` (= prod) structural branch remains because:
- Dev uses Standard mode + a separate `gcp.container.NodePool` resource that does not exist in Autopilot
- Prod uses Autopilot mode with `databaseEncryption.state: 'ENCRYPTED'` (CMEK), Standard cannot have this set
- The mutually exclusive sets of valid config knobs (`removeDefaultNodePool` / `initialNodeCount` for Standard; `enableAutopilot` for Autopilot) cannot collapse into a single Pulumi resource declaration

**Rationale:**

- The structural difference (Autopilot vs Standard) is genuinely the kind the user said `if` is justified for — different resource graphs, not just different config values.
- The duplicated SHARED config (network, subnet, IAM, Gateway, etc.) is what should be extracted. Future env-level additions (e.g., a new `costManagementConfig` flag) only have to be added in one place.

### D6 — `places.googleapis.com` API enabled in all envs

**Decision:** Remove the `if (environment === 'dev') apisToEnable.push('places.googleapis.com')` guard. Add the API to the base `apisToEnable` list unconditionally.

**Rationale:**

- API enablement in GCP is free until first call — enabling Places API in prod is zero-cost when prod doesn't call it.
- Per user direction: *"prod にも同じリソースを作成して... 条件を削除して"* — uniform principle. The stale comment claiming "gcp-cost-guardrails" justification is removed (no such mechanism exists).
- **Alternative considered (rejected): leave as dev-only.** Cost: more `if`-branch clutter, and the comment is misleading. Net: rejected.

### D7 — Comment out (not delete) the staging Cloud NAT block; delete the staging cluster block

**Decision:** The staging-only Cloud NAT scaffolding in `network.ts:193-228` (including the leading explanatory comment at line 193 so the commented-out block stays self-documenting) is **commented out** (with a clearly-labeled TODO comment explaining re-enable conditions). The staging-only cluster block in `kubernetes.ts:725-776` is **deleted** outright.

**Rationale (per user direction):**

- Cloud NAT will likely return — either when (a) prod's `enablePrivateNodes: true` flip happens post-launch (Cloud NAT becomes mandatory for private-node clusters to reach the internet), or (b) staging is reintroduced. The user said *"近い将来導入するのでコメントアウトがいいかも"*. Commenting out preserves the working block as ready-to-uncomment.
- The staging cluster block has dormant bugs (missing `gatewayApiConfig`, missing `monitoringConfig`, missing CMEK) and is largely a copy of the (now-modernized) prod block. Future staging adoption is better served by writing fresh from the unified `sharedClusterConfig` than from a partially-broken legacy.
- **Alternative considered (rejected): delete both.** Cost: Cloud NAT re-introduction will require recreating from git history. Benefit: cleaner active codebase. Net: rejected for Cloud NAT (user direction); accepted for the cluster block (it's been a worse copy than the alternative).

### D8 — Naming conventions: prod resources adopt dev's names; no per-env name suffixes

**Decision:** Under the unified `Zitadel` class, prod resources adopt dev's naming:
- Provider: `liverty-music-provider` (was `zitadel-prod` in prod state)
- MachineUserComponent: `liverty-music` (was `backend-app-prod` in prod state)
- Other component instantiations: same name across envs (the `name` arg passed to the `Zitadel` class — `'liverty-music'`)

The billing budget is renamed `cost-budget` (from `dev-cost-budget`) — env is implicit via Pulumi stack scoping, not encoded in the resource name.

**Rationale:**

- Pulumi resource URNs are scoped by stack — `urn:pulumi:dev::...::Type::name` and `urn:pulumi:prod::...::Type::name` are distinct even when name is the same. Suffixing the name with `-dev` / `-prod` is redundant.
- Simpler `grep` story for future maintainers — same name across envs means the same code path produces the same shape in every stack.
- **Alternative considered (rejected): env-suffixed names everywhere.** Cost: more boilerplate, harder to grep for "the prod Provider resource". Benefit: explicit env disambiguation in log lines (mild). Net: rejected, Pulumi state already disambiguates by stack.

### D9 — Pre-flight ESC seeding is operator pre-condition, not a Pulumi resource

**Decision:** Two new ESC values must be seeded by the operator before the unified `Zitadel` class + Monitoring stack produces the full intended end-state in prod:

- `pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend` — Slack channel ID for backend ERROR log alerts. Created out-of-band via the Slack OAuth flow + GCP Console (per the existing `MonitoringComponentArgs.slackNotificationChannelIds` docstring: *"API requires Slack OAuth flow that is not IaC-friendly"*).
- `pulumiConfig.gcp.billingAlertEmail` — recipient for Cloud Billing Budget alerts. Currently absent in BOTH dev and prod ESC; the dev billing budget has been dormant since inception. Operator decides whether to seed in this change cycle or defer.

The Pulumi code reads these via the existing `gcpConfig.monitoring?.slackNotificationChannels` and `gcpConfig.billingAlertEmail` optional-chain guards. The refactor itself does not require these values to be present — without them, the relevant resources remain unmaterialized (same as today), but the code is no longer env-hardcoded.

**Rationale:**

- These are operator-attended steps (one requires the Slack OAuth UI, the other a deliberate budget-alert-email decision). Documenting them as pre-flight tasks keeps the code change pure and reviewable.

### D10 — Supersede `complete-zitadel-prod-pulumi-stack`; archive at this change's archive step

**Decision:** The OpenSpec change `complete-zitadel-prod-pulumi-stack` (active in `openspec/changes/`, never deployed to prod state) is superseded by THIS change. As part of this change's archive step, the operator marks the remaining `complete-zitadel-prod-pulumi-stack` tasks (§1-3 pre-flight, §11-12 deploy / smoke, §13-14 docs / archive) as "superseded — replaced by `refactor-unify-env-dispatch`", then archives `complete-zitadel-prod-pulumi-stack` with a date-prefix archive directory name. No `pulumi up` is ever run against `complete-zitadel-prod-pulumi-stack`'s coded form.

**Rationale:**

- The `complete-zitadel-prod-pulumi-stack` change correctly identified the 9-component prod gap but chose a parallel-class pattern that this change retrospectively rejects. Its proposal/design/specs remain useful historical context but its tasks are no longer the path forward.
- Per memory `feedback_openspec_archive_when_done.md`, `/opsx:archive` requires `isComplete: true`. The remaining tasks need to be marked done (with "superseded" notes) before archive succeeds. Acceptable because the *intent* of those tasks is realized by this change.
- Archive PR will bundle: (a) updating `complete-zitadel-prod-pulumi-stack/tasks.md` to mark remaining tasks as superseded, (b) running `/opsx:archive complete-zitadel-prod-pulumi-stack` to move the directory to `archive/`, (c) running `/opsx:archive refactor-unify-env-dispatch` itself.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| **Prod backend → Zitadel JWT auth fails for 2-5 min during `pulumi up`** (D3) — destroy of old `MachineKey.kid` invalidates the JWT in the currently-mounted K8s Secret; new JWT propagates via GSM → ESO → Reloader → Pod restart. | Pre-launch prod has zero real users. Operator monitors backend logs; expects `Errors.AuthNKey.NotFound` until ESO sync + Pod restart completes. Documented as expected behavior in tasks.md §smoke-tests. |
| **Pulumi state-level orphan resources** if `pulumi up` is interrupted mid-destroy — the 9 old prod resources could be partially destroyed but not yet recreated, leaving Zitadel-side artifacts (e.g., the productOrg) referenced by destroyed Pulumi state. | Re-running `pulumi up --stack prod` after interruption recreates the missing leaves. If Zitadel-side orphans accumulate (e.g., productOrg created in Zitadel but Pulumi state lost), the operator manually deletes them via the Zitadel admin API before re-running. Acceptable manual cleanup window. |
| **Resource name collision on recreate** — if Pulumi's destroy doesn't fully complete before create (e.g., GSM Secret soft-deletion), the new create might error on "resource already exists". | The GSM Secret resource has `deletionPolicy: 'DELETE'` (already in code) → hard delete on destroy. Zitadel resources (Org, MachineUser, MachineKey) have no soft-delete equivalent. Risk window is small. |
| **Staging re-introduction friction** — type narrowed to `'dev' \| 'prod'`; `Record<Environment, T>` maps lose `staging` entries; staging cluster block deleted. | When staging is re-introduced, the operator (a) adds `'staging'` back to the union, (b) repopulates the env-keyed maps, (c) writes a fresh staging cluster block from `sharedAutopilotConfig`. The reintroduction is more work than today, but the result is correct (vs. today's partially-broken staging stub). |
| **Cloud NAT comment-out drift** — commented-out code can rot; references it makes (NetworkConfig.Osaka.masterCidr, etc.) might break silently. | TODO comment includes explicit re-enable instructions + required ESC seeds. Periodic review (e.g., as part of `enable-private-prod-nodes` future change) re-validates the commented block. If it becomes too stale, delete and rewrite — same outcome as today. |
| **`adminOrgIdMap` requires per-env admin-org-id hardcoded in source** — dev's `371280364565496672` and prod's `372892288692584603` are now both in `constants.ts`. If a Zitadel DB wipe + re-bootstrap happens, the org-id changes and the constant must be updated. | Same risk as today's `ZITADEL_DEV_ADMIN_ORG_ID`. The new map makes the prod entry visible alongside dev, so the dual-update is easier to remember. Comment on the const explains the discovery procedure. |
| **`MonitoringComponent` alert filters now correctly target prod cluster** — change in alert behavior on first prod deploy (was effectively no-op due to dev cluster name mismatch). | Expected behavior. Operator validates alerts route to the configured Slack/Chat channel via a smoke-test alert trigger. |
| **`complete-zitadel-prod-pulumi-stack` supersession archive failure** — `/opsx:archive` requires `isComplete: true`. The remaining tasks need manual mark-as-done with "superseded" notes. | Documented archive procedure in tasks.md. Acceptable manual step. |

## Migration Plan

**Phase 1 — Code refactor (this change's PR)**

1. Open feature branch `refactor-unify-env-dispatch` in cloud-provisioning. Apply all code modifications per the task list.
2. `make lint-ts` passes locally.
3. Open PR. Pulumi preview runs on dev (expected: no diff — the unified `Zitadel` class produces identical state to today's dev) and prod (expected: 9 destroys + ~30 creates + 1 update on `kubernetes-cluster` if `MonitoringComponent` becomes active for prod).
4. Review + merge.

**Phase 2 — Operator pre-flight (out-of-band, optional)**

- (Optional, can skip in this cycle) Create prod Slack channel + seed `pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend` in prod ESC.
- (Optional, can skip in this cycle) Decide budget alert email + budget amount; seed `pulumiConfig.gcp.billingAlertEmail` + `pulumiConfig.gcp.budgetAmountJpy` (new field) for both envs.

Skipping these means `MonitoringComponent` + `gcp.billing.Budget` resources stay unmaterialized in prod (same as today's dev situation). The Zitadel application stack still deploys cleanly.

**Phase 3 — `pulumi up --stack prod` (manual)**

- Trigger from Pulumi Cloud console: https://app.pulumi.com/pannpers/liverty-music/prod/deployments
- Watch destroy + recreate sequence for the 9 BackendMachineKey$... resources.
- Expected: 2-5 min window where backend Pod auth fails. ESO syncs new GSM Secret, Reloader rolls Pod, auth resumes.

**Phase 4 — Smoke tests**

(Inherited from `complete-zitadel-prod-pulumi-stack/tasks.md §12` — same six tests, just executed against the new state.)

1. SPA OIDC sign-in at `https://liverty-music.app`
2. Sign-up email verification arrives via Postmark
3. Operator Google IdP Console sign-in at `https://auth.liverty-music.app/ui/console`
4. JWT `email` claim present in SPA-issued access token
5. `kubectl get externalsecret -n zitadel zitadel-web-secrets` reports `Status=Ready`
6. `zitadel-web` Pod is `Running` (1/1 Ready)

**Phase 5 — Archive supersession**

1. Mark all remaining `openspec/changes/complete-zitadel-prod-pulumi-stack/tasks.md` items as `[x]` with comment `# superseded by refactor-unify-env-dispatch`.
2. Run `/opsx:archive complete-zitadel-prod-pulumi-stack` — moves to `openspec/changes/archive/YYYY-MM-DD-complete-zitadel-prod-pulumi-stack/`.
3. Run `/opsx:archive refactor-unify-env-dispatch` — moves to `openspec/changes/archive/YYYY-MM-DD-refactor-unify-env-dispatch/`.
4. Archive PR bundles both moves + delta→main spec sync.

**Rollback Strategy**

- If Phase 3 fails partway: re-run `pulumi up --stack prod`. The destroy + recreate is idempotent — Pulumi resumes from the failed step.
- If Zitadel-side orphans accumulate (e.g., productOrg created without Pulumi state): operator deletes via Zitadel admin API using `pulumi-admin` MachineUser JWT.
- If the refactor itself is rejected mid-deploy: revert the PR. Prod state stays partially migrated; manual cleanup of leaked resources required. **Likelihood is low** because dev preview already validates the unified class shape.

## Open Questions

- **OQ1: Should `budgetAmountJpy` be a new field in `GcpConfig` or a separate top-level ESC path?** The existing `gcpConfig` shape is mostly secrets-or-IDs; adding a plaintext budget amount is consistent. Recommendation: extend `GcpConfig` with `budgetAmountJpy?: string` (string for consistency with existing `currencyCode: 'JPY', units: '3000'` shape).
- **OQ2: Should the staging cluster block deletion include the `masterCidr` constant from `NetworkConfig.Osaka`?** The constant is referenced only by the deleted staging block. Recommendation: leave the constant (the prod private-nodes flip will need it). Add a comment "currently unused; will be referenced by future enable-private-prod-nodes change".
- **OQ3: Does the supersession of `complete-zitadel-prod-pulumi-stack` affect any open PRs or external references?** As of authoring time, PR #468 (spec) and PR #260 + #261 (cloud-provisioning) are all merged. The merged code still references `BackendMachineKeyComponent` + `ZitadelProdStackComponent`, which this change deletes. No external PRs reference these classes. Recommendation: document the merge-then-delete sequence in the supersession archive note.
- **OQ4: Should `Cloud NAT comment-out` include a NetworkConfig `masterCidr` reference comment, since masterCidr was previously only referenced by the now-commented-out and now-deleted blocks?** Tied to OQ2 — keep the constant, add a "future re-use" comment.
