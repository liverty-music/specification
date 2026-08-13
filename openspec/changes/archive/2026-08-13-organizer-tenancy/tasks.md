## 1. Specification

- [x] 1.1 `identity-management` MODIFIED delta: relax the org topology to allow runtime-provisioned Organizer tenant orgs (not IaC-managed, not drift)
- [x] 1.2 New `organizer-tenancy` capability spec: shared `organizer-console` project + `owner` role (named `owner`, not `admin`) + apps, `organizer-provisioner` machine user (IAM_ORG_MANAGER + short-lived credential), required passkey-primary + recovery + federation + org-pinned-resolution tenant-org login policy
- [x] 1.3 `openspec validate --strict organizer-tenancy` passes; open specification PR and merge (no BSR gen — no proto changes) — merged via specification#780 (+ design coherence follow-up #781)

## 2. Cloud-provisioning (IaC / Pulumi)

- [x] 2.1 `organizer-console` Zitadel Project in the `liverty-music` org with the `owner` ProjectRole and access-token role assertion enabled (`projectRoleCheck` off)
- [x] 2.2 `organizer-console` OIDC app (PKCE, no secret) + per-env redirect URIs for the organizer console host; `backend-api` app on the same project (audience)
- [x] 2.3 `organizer-provisioner` machine user with `IAM_ORG_MANAGER` (narrowest built-in instance role for org-create + cross-org Project/User Grants); credential in ESC/Secret Manager; separate from `backend-app`; root JWT-profile key has a **finite expiry** (not year-2099), short-lived access tokens come from the standard jwt-bearer flow. (Rotation runbook is authored in `organizer-accounts`, where the key is first consumed.)
- [x] 2.4 Ensure Pulumi does not treat runtime-provisioned Organizer tenant orgs as drift
- [x] 2.5 `make lint` (biome + tsc + kustomize render) passes; `pulumi preview` shows only the intended additions — local `make lint-ts` (biome+tsc) clean, CI `Lint` passed; prod preview = 13 create / 2 update (non-mine) / 0 delete (cloud-provisioning#401)

## 3. Ship to prod

- [x] 3.1 cloud-provisioning PR merged → dev Pulumi up (automated) — dev is intentionally stopped (`workloadEnabled=false`), so the Zitadel orchestrator is skipped and dev `up` is a **verified no-op** (`liverty-music/dev - Update: success`); the resources materialize in prod (3.2). Not applied in dev by design.
- [x] 3.2 Prod Pulumi up (manual from console) applies the same — prod `up` **succeeded** (`create: 13, update: 2, same: 299`, 0 delete); `organizer-console` project + apps + `organizer-provisioner` machine user confirmed in prod state
- [x] 3.3 Verify: the `organizer-console` project + `owner` role + both apps + the provisioner machine user are present in **prod** (dev intentionally stopped); no other org was created — the 13 creates contain no `Org` resource and the two IaC-managed orgs remain in `same:299`; `organizerConsoleClientId` stack output resolved to a real (secret) value
