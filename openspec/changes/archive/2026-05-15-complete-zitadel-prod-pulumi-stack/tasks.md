> ⚠️ **This change is SUPERSEDED.** See [SUPERSEDED.md](./SUPERSEDED.md) for the
> rationale. The `[ ]` markers in the tasks below were **not performed** — they are
> preserved unchanged for audit-trail honesty (not fake-checked as `[x]`).
> `refactor-unify-env-dispatch` (archived alongside this directory) delivered the
> same end-state via a simpler unified-class shape.

## 1. Pre-Flight (Out-of-Band, Before First `pulumi up --stack prod`)

- [ ] 1.1 Verify the prod `bootstrap-uploader` sidecar has completed: `gcloud secrets versions list zitadel-machine-key-for-pulumi-admin --project liverty-music-prod` SHALL return at least one ENABLED version.
- [ ] 1.2 Fetch the prod admin-org-id via the Zitadel admin API: write the GSM `zitadel-machine-key-for-pulumi-admin` JSON to a tmp file, exchange it for an access token at `https://auth.liverty-music.app/oauth/v2/token` (JWT-bearer grant), then `GET /admin/v1/orgs` and record the org id where `name == "admin"`. Keep the access token only in shell history scrubbed of the secret.
- [ ] 1.3 Check the prod Zitadel admin API for any existing `SmtpConfig`: `GET /admin/v1/smtp`. If a pre-seeded config exists from out-of-band setup, document it and decide whether to keep, replace, or remove it before §6 of this plan runs.
- [ ] 1.4 Create the prod Google OAuth 2.0 Web Application client in Google Cloud Console (project `liverty-music-prod`). Authorized redirect URI: `https://auth.liverty-music.app/ui/v2/login/login/callback`. Record `client_id` + `client_secret` to a secure password manager.
- [ ] 1.5 Confirm `pannpers@pannpers.dev`'s Google `sub` claim is the same numeric string in use by the dev stack (look up dev's `pulumiConfig.zitadel.adminGoogleSubs.pannpers` value). The `sub` is account-scoped and identical across all Google OAuth clients for the same account.

## 2. ESC Seeding (`liverty-music/prod`)

- [ ] 2.1 `esc env set liverty-music/prod pulumiConfig.zitadel.googleAdminIdp.clientId "<prod-client-id>"` (plaintext).
- [ ] 2.2 `esc env set liverty-music/prod pulumiConfig.zitadel.googleAdminIdp.clientSecret "<prod-client-secret>" --secret`.
- [ ] 2.3 `esc env set liverty-music/prod pulumiConfig.zitadel.adminGoogleSubs.pannpers "<pannpers-google-sub>" --secret`.
- [ ] 2.4 Verify Postmark API token already present at `pulumiConfig.postmark.serverApiToken` (set during the dev cutover; same token used for both envs).
- [ ] 2.5 `esc env get liverty-music/prod` and confirm all 3 new entries resolve with the expected secret-marking. (Implementation note: `pulumiJwtProfileJson` ESC entry is NOT needed — `HumanAdminComponent`'s dynamic resource consumes the admin JWT routed through `BackendMachineKeyComponent.adminJwt` inside `ZitadelProdStackComponent`, sourced from GSM `zitadel-machine-key-for-pulumi-admin` at plan time.)

## 3. One-Time Pulumi Import of Admin Org

- [ ] 3.1 In `cloud-provisioning/` directory, run `pulumi stack select prod`.
- [ ] 3.2 `pulumi import zitadel:index/org:Org admin <prod-admin-org-id>` — the resource name `admin` MUST match the value used in the new `ZitadelProdStackComponent` source (so the import attaches to the right Pulumi resource).
- [ ] 3.3 Verify the import added the resource to state without churn: `pulumi stack export | jq '.deployment.resources[] | select(.type == "zitadel:index/org:Org")'` SHALL return the admin org with `isDefault: true` and `protect: true`.

## 4. New ZitadelProdStackComponent — Skeleton + Provider

- [x] 4.1 Create `cloud-provisioning/src/zitadel/components/zitadel-prod-stack.ts`. Export class `ZitadelProdStackComponent extends pulumi.ComponentResource`. URN namespace: `zitadel:liverty-music:ZitadelProdStack`.
- [x] 4.2 Define `ZitadelProdStackComponentArgs` interface: `env: Environment`, `gcpProject: pulumi.Input<string>`, `postmarkServerApiToken: string`, `googleAdminIdpClientId: pulumi.Input<string>`, `googleAdminIdpClientSecret: pulumi.Input<string>` (secret-wrapped upstream), `pannpersGoogleSub: pulumi.Input<string>`. (Design pivot: no separate `pulumiJwtProfileJson` arg — admin JWT comes from `BackendMachineKeyComponent.adminJwt`, re-exposed for sibling components.)
- [x] 4.3 Re-use the admin-JWT read from inside `BackendMachineKeyComponent` (added a public `adminJwt: pulumi.Output<string>` property) instead of fetching twice. The `CRITICAL` `pulumi.secret()` wrap invariant is enforced inside `BackendMachineKeyComponent` (was already there).
- [x] 4.4 Provider creation happens inside `BackendMachineKeyComponent` (re-used as a sub-component). `ZitadelProdStackComponent` uses `this.backendMachineKey.provider` for all 9 leaves.

## 5. New ZitadelProdStackComponent — Admin Org (Imported) + Product Org + Project

- [x] 5.1 Declare the admin org as a Pulumi resource (`new zitadel.Org('admin', { name: 'admin', isDefault: true }, { provider, protect: true, parent: this })`). Matches the imported state from §3.2.
- [x] 5.2 Product org is created inside `BackendMachineKeyComponent` (already existing — `zitadel.Org('liverty-music', { isDefault: false })`). Re-used as `this.backendMachineKey.productOrg`.
- [x] 5.3 Create the `zitadel.Project` named `liverty-music` in the product org. Mirror dev's `Zitadel.project` constructor args verbatim.
- [x] 5.4 Design pivot: backend MachineKey + productOrg URNs preserved by re-using `BackendMachineKeyComponent` as a sub-component (with `parent: this` + `aliases: [{ parent: pulumi.rootStackResource }]`). Aliases on the parent propagate to all children — verify via `pulumi preview --stack prod` that no resource is marked for replace.

## 6. New ZitadelProdStackComponent — Frontend + Smtp + Actions V2

- [x] 6.1 Instantiate `FrontendComponent` with `env`, `orgId: productOrg.id`, `projectId: project.id`, `provider`, `parent: this`. Creates `ApplicationOidc` + product-org `LoginPolicy`.
- [x] 6.2 Instantiate `SmtpComponent` with `env`, `serverApiToken: postmarkServerApiToken`, `provider`, `domain: zitadelDomainMap[env]`, `jwtProfileJson: <secret-wrapped admin JWT>`, `parent: this`. Creates `SmtpConfig` + `ZitadelSmtpActivation` dynamic resource.
- [x] 6.3 Instantiate `ActionsV2Component` with `domain`, `jwtProfileJson`, `preAccessTokenEndpoint: \`${BACKEND_WEBHOOK_BASE_URL}${PRE_ACCESS_TOKEN_PATH}\``, `provider`, `parent: this`. Creates `Target` + `Execution`.

## 7. New ZitadelProdStackComponent — Login Client + GSM Secret for PAT

- [x] 7.1 Instantiate `LoginClientComponent` with `orgId: adminOrg.id`, `provider`, `parent: this`. Creates the `login-client` `MachineUser` + instance `IAM_LOGIN_CLIENT` role + `PersonalAccessToken`.
- [x] 7.2 Design pivot: GSM `zitadel-login-pat` Secret + Version + ESO IAM binding are NOT created inside `ZitadelProdStackComponent`. Instead `loginClientToken` is surfaced and routed via `src/index.ts` → `Gcp({ ..., zitadelLoginPat })` → `KubernetesComponent.esoOnlySecrets`. Matches the dev path exactly; one code path for both envs.
- [x] 7.3 (Subsumed by 7.2.) The `pulumi.secret()` wrap on the PAT value happens inside `Gcp.KubernetesComponent.esoOnlySecrets` (`pulumi.secret(zitadelLoginPat)` in `src/gcp/index.ts:270`).
- [x] 7.4 (Subsumed by 7.2.) The ESO IAM binding is created inside `Gcp.KubernetesComponent` for `esoOnlySecrets` entries (`src/gcp/components/kubernetes.ts:268-277`).

## 8. New ZitadelProdStackComponent — Google IdP + LoginPolicies + Human Admin

- [x] 8.1 Instantiate `GoogleAdminIdpComponent` with `clientId: googleAdminIdpClientId`, `clientSecret: googleAdminIdpClientSecret`, `provider`, `parent: this`. Creates instance-level `IdpGoogle`.
- [x] 8.2 Instantiate `AdminOrgConfigComponent` with `adminOrgId: adminOrg.id`, `googleIdpId: googleAdminIdp.idp.id`, `provider`, `consoleUrl`, `parent: this`. (Added `consoleUrl` arg to `AdminOrgConfigComponent` — optional, defaults to dev URL for dev-callsite back-compat; prod passes `https://auth.liverty-music.app/ui/console`.)
- [x] 8.3 Instantiate `HumanAdminComponent` with `adminOrgId: adminOrg.id`, `email: 'pannpers@pannpers.dev'`, `firstName: 'Kyosuke'`, `lastName: 'Hamada'`, `googleIdpId: googleAdminIdp.idp.id`, `googleSub: pannpersGoogleSub`, `domain`, `jwtProfileJson`, `provider`, `parent: this`. Creates `HumanUser` + instance `IAM_OWNER` `OrgMember` + dynamic `ZitadelUserIdpLink`.

## 9. Backend MachineKey Absorption — Reuse via Composition (NOT Delete)

- [x] 9.1 Design pivot: keep `cloud-provisioning/src/zitadel/components/backend-machine-key.ts` AS-IS (with the addition of one public `adminJwt` property for sibling re-use). `BackendMachineKeyComponent` is instantiated INSIDE `ZitadelProdStackComponent` with `parent: this` — composition over inlining. This minimizes URN churn (one alias on `BackendMachineKeyComponent` propagates to all children) and avoids re-minting the lifecycle-sensitive backend `MachineKey` JWT (re-mint would cascade the §13.15 `Errors.AuthNKey.NotFound` failure).
- [x] 9.2 Single `aliases: [{ parent: pulumi.rootStackResource }]` on `BackendMachineKeyComponent` covers the parent change. Pulumi's alias propagation re-anchors all child URNs (MachineUser, MachineKey, OrgMember, Secret, SecretVersion, IAM binding) without per-resource alias. Verify in §11.1 `pulumi preview --stack prod` that NONE of these are marked for replace.
- [x] 9.3 (Cancelled — `backend-machine-key.ts` stays. The "delete + inline" path in the original tasks would have forced per-resource aliases across 7 inner resources and increased the destroy-replace risk.)
- [x] 9.4 Update `cloud-provisioning/src/index.ts`: replace `import { BackendMachineKeyComponent } from './zitadel/components/backend-machine-key.js'` with `import { ZitadelProdStackComponent } from './zitadel/components/zitadel-prod-stack.js'`. (Internal re-import inside `zitadel-prod-stack.ts` preserves the `BackendMachineKeyComponent` usage point.)

## 10. Wire ZitadelProdStackComponent in `src/index.ts`

- [x] 10.1 Replace the existing `new BackendMachineKeyComponent('backend-app-prod', ...)` line in the prod-environment branch of `src/index.ts` with a single `new ZitadelProdStackComponent('liverty-music', ...)` instantiation. (Also removed the standalone `if (env === 'prod') { new BackendMachineKeyComponent(...) }` block — the wrapper now creates that resource subtree internally.)
- [x] 10.2 Re-use the existing `zitadelConfig = config.requireSecretObject<...>('zitadel')` object. Three values consumed in the prod branch: `googleAdminIdp.clientId`, `googleAdminIdp.clientSecret`, `adminGoogleSubs.pannpers`. (No separate `pulumiJwtProfileJson` — see §2.5 note.)
- [x] 10.3 The `ZitadelProdStackComponent` constructor receives the three ESC values via `zitadelConfig.apply(...)` (matches the dev call site shape). `loginClientToken` is forwarded into `Gcp` via the `zitadelLoginPat` slot.
- [x] 10.4 `make lint-ts` passes (biome + tsc).

## 11. Pulumi Preview + Deploy

- [ ] 11.1 In `cloud-provisioning/` directory, run `pulumi preview --stack prod --diff`. Verify: ~20-25 new resources are created (the 9 new components + their leaves); NO resource is marked for replace or destroy; the admin org appears as imported (no churn); the backend MachineKey stack's URNs are stable (alias-mapped).
- [ ] 11.2 Run `rm -rf node_modules package-lock.json && npm install` if any `package.json` changes were introduced (per memory `feedback_npm_lockfile_clean_install.md`).
- [ ] 11.3 Commit + push the changes; open a PR to `main`; wait for `pulumi preview` PR check (preview-only on prod per `CLAUDE.md` "Pulumi Deployments (Automated)"). Address any CI failures.
- [ ] 11.4 After PR approval + merge, manually trigger `pulumi up --stack prod` from the Pulumi Cloud console: https://app.pulumi.com/pannpers/liverty-music/prod/deployments. Watch deploy logs for SMTP activation, IdP link, login-client PAT, frontend ApplicationOidc.

## 12. Smoke Tests (Post-Deploy)

- [ ] 12.1 SPA sign-in flow: open `https://liverty-music.app` in a fresh browser, complete OIDC redirect, verify the prod Login V2 UI presents passkey + username/password sign-in.
- [ ] 12.2 Sign-up email verification: complete a test sign-up with a real-but-disposable inbox; verify the verification email arrives via Postmark (check Postmark dashboard if the email doesn't arrive within 60s).
- [ ] 12.3 Operator Console sign-in: open `https://auth.liverty-music.app/ui/console` in a fresh browser; click "Sign in with Google"; complete OAuth as `pannpers@pannpers.dev`; verify Console resolves to that user with IAM_OWNER role.
- [ ] 12.4 Backend access-token email claim: capture a token from the SPA sign-in flow (`localStorage.getItem('access_token')` via DevTools); decode JWT claims via `jwt.io` or `jq`; verify `email` claim is present and matches the signed-in user's email.
- [ ] 12.5 ESO sync verification: `kubectl get externalsecret -n zitadel zitadel-web-secrets -o yaml --context prod`. Verify `Status=Ready` and the synced K8s Secret `zitadel-web-pat` has a non-empty token.
- [ ] 12.6 `zitadel-web` Pod healthy: `kubectl get pods -n zitadel --context prod`. The `zitadel-web` Pod SHALL be `Running` (1/1 Ready), transitioning out of the previous `ContainerCreating` state.

## 13. Documentation + Memory

- [ ] 13.1 Update `cloud-provisioning/CLAUDE.md` if any prod-specific operating rule changed (e.g., new GSM Secret names, new ESC paths). Likely just a one-line note pointing at this archived change.
- [ ] 13.2 If the operator-attended workflow in §1 (admin-org-id discovery via curl) turns into a recurring break-glass step, add a short runbook at `cloud-provisioning/docs/runbooks/zitadel-admin-org-discovery.md` and link from `CLAUDE.md`.
- [ ] 13.3 Run `openspec validate complete-zitadel-prod-pulumi-stack --strict` and confirm no spec-graph regressions.

## 14. Archive

- [ ] 14.1 Run `/opsx:archive complete-zitadel-prod-pulumi-stack` only after `openspec status complete-zitadel-prod-pulumi-stack --json` reports `isComplete: true` and all §11 + §12 + §13 tasks are checked.
- [ ] 14.2 Per `reference_openspec_archive_pattern.md`: bundle the doc-fixes, delta→main spec sync (via `/opsx:archive`'s sync prompt), and git mv into a single archive PR.
