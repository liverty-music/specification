## Why

The just-archived `prod-k8s-manifests` change deployed self-hosted Zitadel on prod (auth.liverty-music.app is live, the bootstrap-uploader sidecar populated `zitadel-machine-key-for-pulumi-admin` GSM Secret at 11:12:47 UTC 2026-05-14 on first boot). The design assumed a follow-up `pulumi up --stack prod` would then use that org-admin JWT to create the backend's lower-privilege `MachineKey` (a Zitadel API call) and write the result to a *separate* GSM Secret `zitadel-machine-key-for-backend-app` — which is what the backend Pod mounts at runtime.

**That follow-up Pulumi code does not exist for prod.** The `Zitadel` class at [`src/zitadel/index.ts`](https://github.com/liverty-music/cloud-provisioning/blob/main/src/zitadel/index.ts) — which wraps the `MachineUserComponent` that creates the backend MachineKey — is currently gated to `env === 'dev'` at [`src/index.ts:74`](https://github.com/liverty-music/cloud-provisioning/blob/main/src/index.ts#L74). The original gate was correct for the SaaS Cloud-tenant Zitadel (`https://liverty-music.zitadel.cloud`); it was *not* lifted when prod switched to self-hosted in `prod-k8s-manifests`. As a result, the prod backend Pods are stuck in `ContainerCreating` waiting for `zitadel-machine-key-for-backend-app` that nothing creates.

This change closes that gap: enables a prod-scoped `Zitadel` Pulumi instance that points at `https://auth.liverty-music.app` and runs the same `MachineUserComponent` → backend MachineKey → GSM SecretVersion flow that dev has.

## What Changes

- **NEW**: `src/index.ts` instantiates a prod-scoped `Zitadel` (or a leaner equivalent — see Design) that points its Zitadel provider at `https://auth.liverty-music.app` and authenticates with the `zitadel-machine-key-for-pulumi-admin` GSM SecretVersion (populated by the in-cluster bootstrap-uploader sidecar on first Zitadel API Pod boot). Currently this is gated `env === 'dev'`; the gate lifts.
- **NEW**: Prod ESC values for the Zitadel-side seeds needed by the Pulumi provider — at minimum the `zitadelConfig` ESC structure (`googleAdminIdp.{clientId,clientSecret}`, `adminGoogleSubs.pannpers`, `e2eTestUser.password`). Either prod gets its own values or each input is made optional in the `Zitadel` class so prod can run with a subset (the minimum being whatever `MachineUserComponent` requires).
- **NEW**: `MachineUserComponent` runs for prod and creates a `zitadel.MachineUser` + `zitadel.MachineKey` inside prod's Zitadel; Pulumi writes the resulting JWT-profile JSON to the GSM Secret `zitadel-machine-key-for-backend-app` (prod project).
- **MODIFIED**: ESO's prod-scoped `backend` namespace `ExternalSecret` already references `zitadel-machine-key-for-backend-app` (inherited from the dev pattern via the k8s base); once the Pulumi side creates the GSM SecretVersion, ESO reconciles it into the backend Pod and Reloader rolls the Deployment.
- **DESIGN DECISION**: Whether to instantiate the full `Zitadel` class for prod (which also tries to create `adminOrg`, `productOrg`, `frontend`, `smtp`, `actionsV2`) — most of which are *already* configured inside the self-hosted Zitadel via its own bootstrap and Pulumi shouldn't recreate them — or to refactor `MachineUserComponent` into a stand-alone top-level component that can be instantiated independently. Tracked in design.md.
- **OUT OF SCOPE**: The `zitadel-machine-key-for-pulumi-admin` to `zitadel-machine-key-for-backend-app` *handoff* is the load-bearing flow. The full SaaS Zitadel feature set (Google admin IDP wiring, SMTP, ActionsV2 webhooks) is not in scope — that comes when prod actually needs admin login + email + custom auth actions, which is a separate change. This PR is the minimum to make backend → Zitadel runtime auth work.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `zitadel-self-hosted-deployment`: extend the existing Bootstrap Admin Machine Key + Backend MachineKey Lifecycle requirements to cover **prod** (currently they reference dev's project/SA/connection name with the implicit assumption that an `env === 'dev'` gate exists Pulumi-side). The requirement narrative becomes env-agnostic, and the prod-specific values (project = `liverty-music-prod`, Zitadel API URL = `https://auth.liverty-music.app`, IAM SA = `zitadel@liverty-music-prod.iam`) are validated against the existing scenarios. No new requirements; existing requirements broaden to apply equally to dev + prod.

## Impact

- **`cloud-provisioning/src/index.ts`**: lift the `env === 'dev'` gate around `new Zitadel(...)` (line 74-95) to include prod. Or replace the call with a leaner top-level `MachineUserComponent` instantiation for prod (cleaner, but requires refactoring the `Zitadel` class to expose what's needed).
- **`cloud-provisioning/src/zitadel/`**: depending on design decision, either refactor `Zitadel` class to make non-MachineKey resources optional, OR extract `MachineUserComponent` to a top-level component.
- **Prod ESC** (`liverty-music/prod` environment): add the `zitadelConfig` ESC structure with the prod values needed by the `Zitadel` class signature (TBD which inputs are required vs optional — see Design).
- **Prod Pulumi state**: `pulumi up --stack prod` will create:
  - 1 Zitadel `MachineUser` (in the prod self-hosted Zitadel API)
  - 1 Zitadel `MachineKey`
  - 1 GSM `Secret` (`zitadel-machine-key-for-backend-app`)
  - 1 GSM `SecretVersion` (the JWT-profile JSON)
  - 1 IAM `SecretIamMember` (ESO accessor on the new Secret)
- **Backend Pod runtime**: currently `ContainerCreating` — flips to `Running` once ESO syncs the new GSM Secret into the backend namespace and Reloader rolls the Deployment.
- **Risk**: Pulumi runs against the prod Zitadel API using the org-admin JWT — bugs in MachineUserComponent could create orphaned MachineUsers or grant excessive privileges. Mitigation: review the same code path that has been stable in dev (no architectural changes, just env propagation).
- **Out of scope**: SaaS Zitadel admin IDP / SMTP / ActionsV2 for prod; backend-migrations Application's cross-repo dependency on the backend repo's `k8s/atlas/overlays/prod` (separate backend-repo PR); making the cross-project Artifact Registry IAM grant Pulumi-managed (manual `gcloud projects add-iam-policy-binding` was applied during the prod-k8s-manifests deploy — a separate Pulumi-side cleanup change should adopt it into state).
