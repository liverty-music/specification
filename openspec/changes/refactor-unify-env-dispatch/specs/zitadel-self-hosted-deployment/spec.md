## ADDED Requirements

### Requirement: Single Unified Zitadel Class Across All Environments

The Pulumi `cloud-provisioning` codebase SHALL provision the Zitadel application stack via a **single** `Zitadel` class (`src/zitadel/index.ts`) used by every Pulumi stack. The class SHALL accept an `env: Environment` argument and SHALL handle all environment-specific behavior internally via ternary expressions and `Record<Environment, T>` constant maps. Parallel "prod-only" or "env-specific" wrapper classes (e.g., `BackendMachineKeyComponent`, `ZitadelProdStackComponent`) SHALL NOT exist; the call-site in `src/index.ts` SHALL invoke `new Zitadel(name, { env, ... })` once, without env-branching.

**Rationale**: The previous parallel-class pattern (`BackendMachineKeyComponent` from `enable-zitadel-prod-pulumi-provider`, `ZitadelProdStackComponent` from `complete-zitadel-prod-pulumi-stack`) duplicated the 9-component Zitadel topology across two near-identical class definitions. Every future Zitadel-side change had to be applied in both places with no compiler-level synchronization guarantee. The leaf components already accept `env` and switch behavior internally via env-keyed maps (`baseDomainMap`, `zitadelDomainMap`, `senderAddressMap`); the wrappers fought that grain. A single class with env-aware internals fits the established leaf-component pattern and eliminates the drift hazard.

#### Scenario: Single Zitadel class instantiation in src/index.ts

- **WHEN** `cloud-provisioning/src/index.ts` is inspected
- **THEN** it SHALL contain exactly one `new Zitadel(...)` instantiation
- **AND** the instantiation SHALL NOT be wrapped in an `if (env === ...)` branch
- **AND** no other `zitadel:liverty-music:*` ComponentResource wrapping the 9 Zitadel leaf components SHALL exist

#### Scenario: Env-driven differences via map / ternary, not branching wrapper

- **WHEN** the `Zitadel` class constructor handles an environment-specific value (admin org id, redirect URI, sender address, etc.)
- **THEN** the value SHALL be sourced from a `Record<Environment, T>` map (e.g., `adminOrgIdMap`, `baseDomainMap`) consulted via `[env]` indexing
- **AND/OR** the value SHALL be a ternary expression (`env === 'dev' ? X : Y`)
- **AND** the class SHALL NOT have its own `if (env === 'dev')` / `if (env === 'prod')` top-level dispatch (env-conditional leaf-component instantiation such as `if (env === 'dev') this.e2eTestUser = ...` is acceptable when the leaf component is truly env-scoped, but the wrapper structure itself is uniform)

#### Scenario: Zero dev URN churn after unification

- **WHEN** `pulumi preview --stack dev` runs after this requirement is implemented
- **THEN** the preview SHALL show zero changes to existing Zitadel-side resource URNs in dev state
- **AND** the `Zitadel` class internal structure SHALL be byte-equivalent to its pre-refactor form modulo the removal of the `env !== 'dev'` throw guard and the addition of env-conditional `E2eTestUserComponent` creation

### Requirement: Env-Driven Configuration Uses Maps or Ternaries, Not Top-Level If-Branches

The Pulumi `cloud-provisioning` codebase SHALL express environment-specific configuration values via `Record<Environment, T>` constant maps or inline ternary expressions. Top-level `if (env === 'dev')` / `if (env === 'prod')` branches in component constructors or in `src/index.ts` SHALL be reserved for **structurally different resource shapes** — i.e., cases where the env difference produces fundamentally different Pulumi resource types or resource graphs that cannot be expressed as parameter differences on the same resource declaration.

Examples of structural differences (where `if` IS justified):
- DNS topology: prod uses Cloudflare for the apex + Cloud DNS for subdomains; non-prod uses Cloud DNS only with a single zone (`src/gcp/components/network.ts`)
- K8s cluster mode: dev uses Standard cluster + separate NodePool resource; prod uses Autopilot cluster with mutually-exclusive config knobs (`src/gcp/components/kubernetes.ts`)
- Organization folder: prod creates a new folder; non-prod imports via `StackReference` (`src/gcp/components/project.ts`)
- GitHub organization-level config: prod stack owns the GitHub org-level resources to avoid cross-stack conflict (`src/index.ts`)

Examples of NON-structural differences (where ternary / map SHALL replace `if`):
- Environment-specific redirect URIs (add localhost only for dev)
- Environment-specific OAuth client values
- Environment-specific admin org ids
- Environment-specific Postmark sender addresses
- Conditional API enablement of harmless APIs

**Rationale**: The `if`-as-default pattern leads to code drift across env branches because each branch carries an independent copy of the surrounding configuration. Centralizing env-keyed differences in maps and inline ternaries forces the env-specific value to be the ONLY thing that varies, making divergence visible at the point of value selection rather than spread across duplicated blocks.

#### Scenario: Per-env redirect URIs use ternary spread, not if-push

- **WHEN** `FrontendComponent` constructs `redirectUris` for the SPA's `ApplicationOidc`
- **THEN** dev-only localhost URIs SHALL be added via ternary spread (`...(env === 'dev' ? ['http://localhost:9000/auth/callback'] : [])`)
- **AND** an `if (env === 'dev')` block that calls `redirectUris.push(...)` SHALL NOT appear

#### Scenario: Per-env admin org id sourced from env-keyed map

- **WHEN** the `Zitadel` class imports the admin org via `zitadel.Org('admin', ...)` resource option `import:`
- **THEN** the import id SHALL be `adminOrgIdMap[env]` where `adminOrgIdMap: Record<Environment, string>` lives in `src/zitadel/constants.ts`
- **AND** no per-env scalar constant (such as a legacy `ZITADEL_DEV_ADMIN_ORG_ID`) SHALL be referenced

#### Scenario: places.googleapis.com enabled in all environments

- **WHEN** `src/gcp/components/kubernetes.ts` builds the `apisToEnable` list
- **THEN** `places.googleapis.com` SHALL be included unconditionally (no env-gated `apisToEnable.push`)
- **AND** API enablement SHALL incur zero recurring cost when the API is not called (justified by GCP's enablement-is-free / per-call-is-paid pricing)

### Requirement: Backend MachineUser Lives in Product Org Across All Environments

The Pulumi `Zitadel` class SHALL create the backend `MachineUser` (with `ORG_USER_MANAGER` role grant via `OrgMember`) inside a **Pulumi-managed product org** named `liverty-music`, in every environment. Pulumi SHALL NOT create or manage the first-boot admin org (auto-created by Zitadel via `ZITADEL_FIRSTINSTANCE_ORG_NAME`) as a creation; the admin org SHALL be brought into Pulumi state via the `import:` resource option using an environment-keyed admin-org-id map (`adminOrgIdMap`), without per-env wrapper classes or per-env scalar constants.

**Rationale**: The first-boot admin org holds operator identities — `pulumi-admin` (IaC break-glass), `login-client` (Login V2 PAT host), and any human IAM_OWNER admins. Granting the backend `MachineUser` `ORG_USER_MANAGER` in that org would let the runtime backend Pod create, suspend, or modify those operator identities — a privilege-escalation foothold from a compromised backend Pod to the IaC/admin tier. Placing `backend-app` in a separate Pulumi-managed product org confines `ORG_USER_MANAGER` to end-user principals. This rule applied to dev from the original cutover (`add-zitadel-console-admin-via-google-idp`) and was extended to prod in `enable-zitadel-prod-pulumi-provider` with the prod-specific `BackendMachineKeyComponent`. The unified `Zitadel` class makes the rule env-agnostic: same code path, same Pulumi resource shapes, env-specific values only via maps.

#### Scenario: backend-app MachineUser lives in product org (any env)

- **WHEN** `pulumi up` is applied to any env (`dev` or `prod`)
- **THEN** the resulting Pulumi state SHALL contain exactly one `zitadel.Org` resource named `liverty-music` (the product org)
- **AND** the backend `zitadel.MachineUser` resource SHALL reference `productOrg.id`, NOT the admin org's id
- **AND** the `zitadel.OrgMember` granting `ORG_USER_MANAGER` SHALL also scope to `productOrg.id`

#### Scenario: Admin org imported via inline import: resource option, env-keyed id

- **WHEN** the `Zitadel` class instantiates `new zitadel.Org('admin', ...)` for any env
- **THEN** the resource SHALL declare `protect: true`
- **AND** SHALL declare `isDefault: true` (matching the bootstrap-set flag)
- **AND** SHALL declare `import: adminOrgIdMap[env]` to bind to the pre-existing bootstrap-created admin org
- **AND** the `adminOrgIdMap` SHALL contain at minimum a `dev` entry and a `prod` entry, each set to the respective env's admin-org-id as discovered post-bootstrap via `POST /admin/v1/orgs/_search`

#### Scenario: Provider sourced from GSM admin JWT in all envs

- **WHEN** the `Zitadel` class instantiates `new zitadel.Provider(...)` for any env
- **THEN** `jwtProfileJson` SHALL be a `pulumi.secret()`-wrapped `Output<string>` produced by `gcp.secretmanager.getSecretVersionAccessOutput` against the GSM Secret `zitadel-machine-key-for-pulumi-admin` in the env's GCP project
- **AND** the env's `domain` SHALL be `zitadelDomainMap[env]`
- **AND** no per-env wrapper class SHALL pre-process or shadow this Provider construction

### Requirement: Cost Guardrails and Observability Applied to All Environments

The Pulumi `cloud-provisioning` codebase SHALL instantiate `ZitadelMonitoringComponent` and `gcp.billing.Budget` in every environment (`dev` and `prod`). Materialization of these resources at apply time SHALL be gated by the presence of their required ESC configuration (`gcpConfig.monitoring?.slackNotificationChannels` for the monitoring chain; `gcpConfig.billingAlertEmail` for the budget), not by env-hardcoded branches.

**Rationale**: The previous `if (environment === 'dev')` guard around `ZitadelMonitoringComponent` and the billing budget was a pre-prod decision rationalized as "thresholds tuned for dev, would page on prod". Empirically the thresholds (50× headroom on latency p99, 10 errors / 60s on JWT validation) are generous enough for pre-launch prod traffic. Re-tuning is a future operational concern; gating on env at code level prevents the operator from enabling prod alerts via ESC seeding without a code change. The new pattern: code is env-uniform, materialization is ESC-driven.

#### Scenario: ZitadelMonitoringComponent runs in all envs when Slack channel ESC seeded

- **WHEN** `pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend` is seeded in an env's ESC
- **THEN** `pulumi up` for that env SHALL create the `ZitadelMonitoringComponent` resources (latency p99 alert, JWT error rate alert, connection-pool dashboard)
- **AND** no `if (environment === 'dev')` code branch SHALL gate the instantiation

#### Scenario: Billing budget materializes when ESC seeded, any env

- **WHEN** `gcpConfig.billingAlertEmail` is set in an env's ESC
- **THEN** `pulumi up` for that env SHALL create a `gcp.billing.Budget` resource named `cost-budget` (env scoping is via Pulumi stack URN, not the resource name)
- **AND** the budget amount SHALL be sourced from `gcpConfig.budgetAmountJpy` (new field, env-specific value)

#### Scenario: MonitoringComponent targets the env's actual cluster

- **WHEN** `MonitoringComponent` instantiates log-based alert policies
- **THEN** the `clusterName` and `clusterLocation` arguments SHALL be sourced from env-keyed maps (e.g., `clusterNameByEnv`, `clusterLocationByEnv`)
- **AND** the resolved values SHALL match the cluster actually deployed in that env (dev: `standard-cluster-osaka` / `asia-northeast2-a`; prod: `autopilot-cluster-osaka` / `asia-northeast2`)
- **AND** no per-cluster name SHALL be hardcoded to a single env's value

## REMOVED Requirements

### Requirement: Backend MachineUser Placed in Product Org, Not the First-Boot Admin Org

**Reason**: Superseded by the new general-form requirement "Backend MachineUser Lives in Product Org Across All Environments" (ADDED above). The removed requirement was written in `enable-zitadel-prod-pulumi-provider` with prod-specific language ("Pulumi `BackendMachineKeyComponent` (or equivalent) SHALL ...") that constrained the implementation choice to a parallel wrapper class. The new general-form requirement applies env-agnostically and does not constrain the implementation to a particular wrapper.

**Migration**: Implementations satisfying the removed requirement automatically satisfy the new general-form requirement, as the rule itself (product-org placement of backend `MachineUser` + ORG_USER_MANAGER) is preserved. The constraint that was relaxed is the implementation shape: the unified `Zitadel` class replaces the prod-specific `BackendMachineKeyComponent` while continuing to honor the org-placement rule.

### Requirement: Prod Backend MachineKey Component Authenticates with Bootstrap-Uploaded Admin JWT

**Reason**: The `BackendMachineKeyComponent` (the subject of this requirement) is deleted by this change. Its responsibilities — fetching the admin JWT from GSM via `getSecretVersionAccessOutput`, wrapping it in `pulumi.secret()`, configuring the `zitadel.Provider` — are absorbed into the unified `Zitadel` class and apply to all envs uniformly. The new ADDED requirement "Backend MachineUser Lives in Product Org Across All Environments" scenarios `Admin org imported via inline import: resource option, env-keyed id` and `Provider sourced from GSM admin JWT in all envs` together cover all the operational invariants the removed requirement encoded.

**Migration**: The `pulumi.secret()` wrap, the GSM data source, and the failure-on-missing-version behavior are all preserved in the unified `Zitadel` class. Implementations migrating from `BackendMachineKeyComponent` SHALL:
1. Delete the `BackendMachineKeyComponent` file.
2. Remove the `env !== 'dev'` throw guard from the `Zitadel` class.
3. Source the admin JWT inside the unified class (it was already there pre-refactor for dev; remove the env guard so the same code path runs in prod).
4. Accept the prod state migration cost: the previous `BackendMachineKey$...` URNs are destroyed and recreated under `Zitadel$...` URNs on the first prod `pulumi up`. Brief backend-auth outage (~2-5 min pre-launch).

## MODIFIED Requirements

### Requirement: Bootstrap Admin Machine Key Stored in Secret Manager

On first startup of an empty database, Zitadel SHALL create an initial admin machine user by consuming `ZITADEL_FIRSTINSTANCE_*` environment variables, write the resulting JWT-profile JSON key to a shared `emptyDir` pod volume, and a `bootstrap-uploader` sidecar container co-located in the same Zitadel API Pod SHALL upload that key to GCP Secret Manager as `zitadel-machine-key-for-pulumi-admin`; subsequent Pulumi stack applies SHALL read the key from Secret Manager as the `jwtProfileJson` for the Zitadel provider. This lifecycle SHALL apply identically across all environments (`dev` and `prod`).

Per the `Single Unified Zitadel Class Across All Environments` requirement, the JWT read + Provider construction live inside one shared `Zitadel` class consumed by all Pulumi stacks. No per-env wrapper class (`BackendMachineKeyComponent`, `ZitadelProdStackComponent`) shall mediate this lifecycle.

**Rationale**: This closes the bootstrap chicken-and-egg — Pulumi needs admin credentials to configure Zitadel, but admin credentials only exist after Zitadel has bootstrapped itself. Shifting the boundary into the cluster avoids manual human steps. A separate Kubernetes `Job` cannot share an `emptyDir` volume with the Zitadel Deployment Pod (volumes are Pod-scoped), so the uploader runs as a sidecar container inside the Zitadel API Pod where the shared volume is naturally accessible. The sidecar idles after the upload (`tail -f /dev/null`) so the Pod stays ready and the upload is idempotent across Pod restarts (it skips re-uploading when the stored GSM version already matches).

The GSM name `zitadel-machine-key-for-pulumi-admin` follows the platform-wide convention `zitadel-machine-key-for-<principal>`, where `<principal>` is the Pulumi `MachineUser` resource id. The legacy name `zitadel-admin-sa-key` was renamed because (1) it did not encode the binding between the GSM secret and the owning Zitadel principal, and (2) the principal label `admin` did not match the Pulumi `MachineUser` resource id `pulumi-admin`.

The unified `Zitadel` class refactor (`refactor-unify-env-dispatch`) deletes the prod-specific `BackendMachineKeyComponent` that previously mediated this for prod. The unified class re-runs the same GSM read + Provider construction in both envs from a single code path; the `pulumi.secret()` wrap that protects the embedded RSA private key from leaking into preview/state/log output is enforced once in the unified class and inherited by all envs.

#### Scenario: First boot writes the admin key

- **WHEN** the Zitadel API container starts against an empty database
- **THEN** `ZITADEL_FIRSTINSTANCE_MACHINEKEYPATH` SHALL point to a path on an `emptyDir` volume mounted into both the Zitadel container and the `bootstrap-uploader` sidecar container in the same Pod
- **AND** Zitadel SHALL write a JSON key file at that path
- **AND** the `bootstrap-uploader` sidecar container in the same Pod SHALL upload the file to GCP Secret Manager secret `zitadel-machine-key-for-pulumi-admin`
- **AND** the `bootstrap-uploader` sidecar SHALL unlink the key file from the shared `emptyDir` after a successful GSM upload, so the org-admin private key does not persist in the volume for the Pod's lifetime where any future co-located container with the same `volumeMount` could read it

#### Scenario: Subsequent boots skip bootstrap

- **WHEN** Zitadel starts against an already-initialized database
- **THEN** the `ZITADEL_FIRSTINSTANCE_*` environment variables SHALL be ignored
- **AND** the existing admin machine user and key in Secret Manager SHALL remain unchanged

#### Scenario: Unified Zitadel class reads admin JWT in all envs

- **WHEN** `pulumi up` runs for any env after the `refactor-unify-env-dispatch` change is applied
- **THEN** the JWT is read via `gcp.secretmanager.getSecretVersionAccessOutput` against the env-scoped `zitadel-machine-key-for-pulumi-admin` GSM Secret
- **AND** the read result is wrapped in `pulumi.secret()` inside the unified `Zitadel` class
- **AND** the wrapped value is passed to `new zitadel.Provider(...).jwtProfileJson`
- **AND** no env-specific wrapper class mediates this construction
