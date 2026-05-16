## 1. Cloud-provisioning: Prod Zitadel SPA OIDC client (Phase 2 — `liverty-music/cloud-provisioning`)

- [x] 1.1 Inspect existing `Zitadel` component to confirm the `web-frontend` `ApplicationOidc` is provisioned for all envs (dev already wired); if it's gated on `env === 'dev'`, remove the gate so prod also gets one. — landed in liverty-music/cloud-provisioning#264
- [x] 1.2 Export `webFrontendClientId` and `productOrgId` as Pulumi stack outputs so operators can `pulumi stack output` them for `.env.prod`. — liverty-music/cloud-provisioning#264
- [x] 1.3 `pulumi preview --stack prod` and capture the diff in the PR description. — captured in #264 description
- [x] 1.4 Open PR; review; merge. — liverty-music/cloud-provisioning#264 (merged)

## 2. Cloud-provisioning: Prod `ApplicationOidc` apply (Phase 3 — operator-attended)

- [x] 2.1 Trigger `pulumi up --stack prod` manually via Pulumi Cloud console. — prod stack v160 executed
- [x] 2.2 Verify the new resource appeared in prod stack state.
- [x] 2.3 Capture `pulumi stack output webFrontendClientId` and `pulumi stack output productOrgId` from the prod stack; paste them into a private notes file under `tmp/` for use in §7. — values fed forward into §7.1

## 3. Backend: Release-tag-triggered prod build path (Phase 4 — `liverty-music/backend`)

- [x] 3.1 In `.github/workflows/deploy.yml`, change the trigger block to dual `push: branches: [main]` + `release: types: [published]`. — liverty-music/backend#296
- [x] 3.2 Add job-level `environment:` selector: `${{ github.event_name == 'release' && 'prod' || 'dev' }}`. — liverty-music/backend#296
- [x] 3.3 In the matrix step "Set Image URI", make `PROJECT_ID` resolve from the selected environment (`vars.PROJECT_ID` already points at `liverty-music-prod` in the prod environment, per existing Pulumi-managed GitHub vars). — liverty-music/backend#296
- [x] 3.4 In "Build and Push Docker Image" step, set tags conditionally: dev builds get `${IMAGE_URI}:latest,${IMAGE_URI}:${sha},${IMAGE_URI}:main`; release builds get `${IMAGE_URI}:${github.event.release.tag_name},${IMAGE_URI}:${sha}`. — liverty-music/backend#296
- [x] 3.5 Add a job-level guard: prod path SHALL NOT fire on `push` events; dev path SHALL NOT fire on `release` events. — liverty-music/backend#296; reinforced with runtime `git merge-base --is-ancestor HEAD origin/main` per round-2 review feedback
- [x] 3.6 Verify `make check` (or equivalent) still passes on the workflow YAML.

  Follow-up that landed in this phase but was not in the original plan: prod GitHub Environment's `deployment_branch_policy` had to flip from `protected_branches: true` to `custom_branch_policies: true` + explicit `main` + `v*` patterns so release tag refs are accepted — shipped as liverty-music/cloud-provisioning#266.

## 4. Backend: Atlas prod overlay (Phase 4 continued — `liverty-music/backend`)

- [x] 4.1 Create `liverty-music/backend:k8s/atlas/overlays/prod/kustomization.yaml` mirroring the dev overlay structure. — liverty-music/backend#297
- [x] 4.2 Patch the `AtlasMigration` resource for the prod Cloud SQL connection (PSC DNS `298474959c18.25pf3r4b6sfkn.asia-northeast2.sql.goog`, database `liverty-music`, user `backend-app@liverty-music-prod.iam`). — liverty-music/backend#297
- [x] 4.3 Confirm the migration source ConfigMap is generated from the same `migrations/` directory as dev (no fork).
- [x] 4.4 Run `kubectl kustomize k8s/atlas/overlays/prod` locally; verify exit 0 + sensible YAML output.
- [x] 4.5 Compare the prod overlay's migration plan against the current prod Cloud SQL state via `atlas migrate diff` (dry-run, against prod via an operator's authenticated psql session). Confirm no destructive operations on first apply.
- [x] 4.6 Open backend PR bundling §3 + §4; review; merge. — §3 shipped as liverty-music/backend#296 and §4 as liverty-music/backend#297 (split for review-load reasons)

## 5. Backend: Cut prod Release (Phase 5 — operator-attended)

- [x] 5.1 Tag `liverty-music/backend:main` HEAD as `v1.0.0` (or the next semver). — `v1.0.0` cut at commit `3bc2dada`
- [x] 5.2 Publish the GitHub Release for that tag.
- [x] 5.3 Watch `gh run watch` for `deploy.yml`; confirm all four images (`server`, `consumer`, `concert-discovery`, `artist-image-sync`) pushed to `liverty-music-prod/backend/`. — first attempt blocked by `deployment_branch_policy`; resolved via liverty-music/cloud-provisioning#266; rerun blocked by WIF SA binding drift (Pulumi state declared the binding but GCP had silently dropped it), restored via `gcloud iam service-accounts add-iam-policy-binding` on the prod `github-actions` SA; release reran green
- [x] 5.4 Verify via `gcloud artifacts docker images list asia-northeast2-docker.pkg.dev/liverty-music-prod/backend --include-tags` that each image carries both the `v1.0.0` tag and the commit SHA.

## 6. Operator: VAPID keypair verification + (if needed) regeneration (Phase 6 — must precede frontend `.env.prod` commit)

This section runs BEFORE §7 so `.env.prod` is committed with the authoritative VAPID public key in one shot. Without this ordering, Mode B would force a v1.0.1 frontend rebuild AND an overlay re-pin (PR review noted).

- [x] 6.1 Decrypt the prod `vapid-private-key` GSM secret: `gcloud secrets versions access latest --secret=vapid-private-key --project=liverty-music-prod`.
- [x] 6.2 Derive the public point from the private key (Base64URL-encoded uncompressed P-256). Compare to the current `VAPID_PUBLIC_KEY` value in `cloud-provisioning/k8s/namespaces/backend/overlays/prod/server/configmap.env`. — **mismatch detected** (configmap held a dev-era placeholder; GSM private was already prod-specific)
- [x] 6.3 If match (Mode A in design D9): record the GSM-derived public key value (which equals the current configmap value) for use in §7.1 (`.env.prod`). No cloud-provisioning PR needed in this phase. Proceed to §7. — N/A (Mode B path was taken)
- [x] 6.4 If mismatch (Mode B): generate a fresh prod VAPID keypair locally — **not needed**; the GSM-stored prod private key was already correct, only the configmap public placeholder had to be rewritten to match the GSM-derived public. Recorded as a "Mode B exception" in liverty-music/cloud-provisioning#265's PR description.
- [x] 6.5 (Mode B only) Open a cloud-provisioning PR ("Mode B VAPID rotation") updating `VAPID_PUBLIC_KEY=` to the newly-generated public point in three backend prod configmap.env files (`server`, `consumer`, `cronjob/concert-discovery`). Review. Do NOT merge yet. — landed as liverty-music/cloud-provisioning#265 (configmap public realigned to GSM-derived public; GSM private untouched because it was already authoritative)
- [x] 6.6 (Mode B only) `esc env set liverty-music/prod pulumiConfig.gcp.vapidPrivateKey "$(cat vapid-private.pem)" --secret`. ESC is not yet applied to GSM until the next `pulumi up`. — skipped (GSM private was already prod-specific)
- [x] 6.7 (Mode B only) **Atomic apply window** (target: sub-minute mismatch). — collapsed to a configmap-only merge because no GSM rotation was required.
- [x] 6.8 (Mode B only) Acknowledge: there is an unavoidable ~30-90s window — N/A for this Mode B exception path; no GSM rotation, single configmap change rolled by Reloader.
- [x] 6.9 Record the public key value (Mode A: GSM-derived = current configmap value; Mode B: freshly generated) in `tmp/vapid-public-prod.txt` for consumption by §7.1. — public key fed forward into §7.1 (frontend `.env.prod`)

## 7. Frontend: `.env.prod` + Release-tag-triggered prod build path (Phase 7 — `liverty-music/frontend`)

- [x] 7.1 Create `liverty-music/frontend:.env.prod` with the full `VITE_*` key set. — liverty-music/frontend#356 (all VITE_* keys committed, including the §2.3-sourced `VITE_ZITADEL_CLIENT_ID` / `VITE_ZITADEL_ORG_ID` and the §6.2-resolved `VITE_VAPID_PUBLIC_KEY`). `VITE_PREVIEW_ARTIST_IDS` / `_NAMES` carry initial copy from dev — curation tracked as §16 follow-up.
- [x] 7.2 In `.github/workflows/push-image.yaml`, add `release: types: [published]` trigger alongside `push: branches: [main]`. — liverty-music/frontend#356
- [x] 7.3 Add job-level `environment:` selector: `${{ github.event_name == 'release' && 'prod' || 'dev' }}`. — liverty-music/frontend#356
- [x] 7.4 Add a build step that runs `npm run build -- --mode prod` only on the prod path (the existing dev build remains `npm run build`). — liverty-music/frontend#356
- [x] 7.5 Set image tags conditionally per §3.4 pattern; prod gets `${tag}` and `${sha}`, dev keeps the existing triple. — liverty-music/frontend#356
- [x] 7.6 Verify `tsc` + biome on the workflow + `.env.prod`.
- [x] 7.7 Open frontend PR; review; merge. — liverty-music/frontend#356 (merged)

## 8. Frontend: Cut prod Release (Phase 8 — operator-attended)

- [x] 8.1 Tag `liverty-music/frontend:main` HEAD as `v1.0.0` (or matching backend's version). — `v1.0.0` cut at commit `51f5bce3`
- [x] 8.2 Publish the GitHub Release.
- [x] 8.3 Watch `gh run watch` for `push-image.yaml`; confirm `web-app:v1.0.0` pushed to `liverty-music-prod/frontend/`.
- [x] 8.4 Pull the prod image locally; extract `/usr/share/caddy/index.html` and `assets/*.js`; verify:
  - No occurrences of `dev.liverty-music.app` in any chunk.
  - `api.liverty-music.app` appears in at least one chunk.
  - `auth.liverty-music.app` appears in at least one chunk.
  - The embedded OIDC `client_id` matches the value captured in §2.3.
  - The embedded `VITE_VAPID_PUBLIC_KEY` matches the value from §6.7.

## 9. Cloud-provisioning: Prod overlay image pinning + IAM revocation runbook (Phase 9 — `liverty-music/cloud-provisioning`)

Note: the Mode B `VAPID_PUBLIC_KEY=` configmap update was moved to §6.5+ (Phase 6) so the GSM rotation and configmap update land in the same coordinated apply window (per design D9 atomicity).

- [x] 9.1 In `k8s/namespaces/backend/overlays/prod/kustomization.yaml`, add an `images:` block pinning each of `server`, `consumer`, `concert-discovery`, `artist-image-sync` to `asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/<name>:<sha-from-§5>`. — liverty-music/cloud-provisioning#268 (pinned to `3bc2dada3c4cd06c218235eb7fe21ad638e29bf3`)
- [x] 9.2 In `k8s/namespaces/frontend/overlays/prod/kustomization.yaml`, add an `images:` block pinning `web-app` to `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:<sha-from-§8>`. — liverty-music/cloud-provisioning#268 (pinned to `51f5bce376d4eda670f83b4a654cf1f924c2f4f1`)
- [x] 9.3 Run `kustomize build k8s/namespaces/backend/overlays/prod` and `... frontend/overlays/prod`; grep rendered Deployment images:
  - Every backend Deployment image SHALL match `^asia-northeast2-docker\.pkg\.dev/liverty-music-prod/backend/`.
  - The frontend Deployment image SHALL match `^asia-northeast2-docker\.pkg\.dev/liverty-music-prod/frontend/`.
  - No rendered image URI contains the substring `liverty-music-dev/`.
- [x] 9.4 Add `docs/runbooks/revoke-cross-project-ar-iam.md` documenting the exact `gcloud projects remove-iam-policy-binding` invocation with a "MUST run AFTER overlay merge" guard. — liverty-music/cloud-provisioning#268
- [x] 9.5 Open cloud-provisioning PR; review; merge. — liverty-music/cloud-provisioning#268 (merged)

## 10. Cloud-provisioning: Verify ArgoCD prod cutover (Phase 10 — operator-attended)

- [x] 10.1 Wait for ArgoCD to detect the cloud-provisioning main-branch change.
- [x] 10.2 In ArgoCD UI / `kubectl --context=prod -n argocd get applications`, confirm `backend` and `frontend` apps reach `Synced/Healthy`.
- [x] 10.3 `kubectl --context=prod -n backend get pod -o yaml | grep image:` — every image SHALL start with `liverty-music-prod/backend/`. — initial cutover hit `ImagePullBackOff` because the prod `gke-node` SA was missing `roles/artifactregistry.reader` on the prod backend AR (Pulumi state had it, GCP had silently dropped it — second drift incident this phase); restored manually, then verified clean
- [x] 10.4 `kubectl --context=prod -n frontend get pod -o yaml | grep image:` — image SHALL start with `liverty-music-prod/frontend/`.
- [x] 10.5 Curl smoke: `api.liverty-music.app/healthz` returns 401 (auth gate reachable); `auth.liverty-music.app/.well-known/openid-configuration` returns 200.

## 11. Operator: Revoke manual cross-project IAM grant (Phase 11)

- [x] 11.1 Re-verify §10.3 and §10.4 — no pod still references a dev-AR image.
- [x] 11.2 Run `gcloud projects remove-iam-policy-binding liverty-music-dev --member='serviceAccount:gke-node@liverty-music-prod.iam.gserviceaccount.com' --role='roles/artifactregistry.reader'`.
- [x] 11.3 Wait 5 minutes; `kubectl --context=prod get pods -A | grep -E 'ImagePullBackOff|ErrImagePull'` — output SHALL be empty.
- [x] 11.4 Verify via `gcloud projects get-iam-policy liverty-music-dev --flatten='bindings[].members' --filter='bindings.members~liverty-music-prod'` returns empty.

## 12. Operator: Prod ESC seeding (Phase 12)

- [x] 12.1 Create a Slack notification channel for prod in GCP Console (Monitoring → Alerting → Edit notification channels → Slack). Record the channel ID.
- [x] 12.2 `esc env set liverty-music/prod pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend "<channel-id>"`.
- [x] 12.3 `esc env set liverty-music/prod pulumiConfig.gcp.billingAlertEmail "pannpers@pannpers.dev"` (or the operator's preferred billing contact).
- [x] 12.4 `esc env set liverty-music/prod pulumiConfig.gcp.budgetAmountJpy "10000"` (or operator-chosen prod budget; defaults to 3000 if unset).
- [x] 12.5 `pulumi preview --stack prod`; confirm the diff shows MonitoringComponent + ZitadelMonitoringComponent + cost-budget + billing-alert-email creates.
- [x] 12.6 `pulumi up --stack prod` (manual via Pulumi Cloud console). — v162 failed mid-stream because `billingbudgets.googleapis.com` was not enabled on prod (no implicit `dependsOn` from `gcp.billing.Budget` to a project Service). Codified the fix in liverty-music/cloud-provisioning#270 (added `gcp.projects.Service` for `billingbudgets` + `dependsOn` on Budget); v163 re-ran with 11/12 resources created. Final resource — `alert-zitadel-oidc-latency-p99` — failed because `workload.googleapis.com/rpc.server.duration` was not yet registered on the prod metric inventory; that alert was disabled in liverty-music/cloud-provisioning#273 to unblock prod up. Re-enablement is tracked in a separate worktree (the OTEL pipeline issue has since been resolved).
- [x] 12.7 Verify `gcloud monitoring channels list --project=liverty-music-prod` includes the new Slack channel + Google Chat + email channels.
- [x] 12.8 Verify GCP Console → Billing → Budgets & Alerts shows the new prod budget.

## 13. Operator: Mainnet ticket SBT contract deployment (Phase 13)

**Pre-deploy verification gate** (§13.1-§13.3): the ESC values consumed by §13.4's `forge create` / equivalent contract deploy SHALL be confirmed to target mainnet BEFORE the deploy fires. A misconfigured `blockchain.rpcUrl` (still pointing at Amoy / Mumbai / Sepolia testnet) would cause the deploy to land on the wrong network — an irreversible on-chain action whose only "rollback" is redeploying to mainnet (paying gas + losing the testnet address). The `owner()` post-deploy check (§13.7) catches private-key mismatches but only after the on-chain action.

**Status: deferred to follow-up #482.** §13 + §14 require an on-chain mainnet deploy paid for in real MATIC (or the target chain's gas token). This is an operator product decision (when to spend, which chain, which deployer key custody), not an automation gap. Moved to a dedicated follow-up so the rest of this change can archive without artificially holding §13-18 hostage to a payment decision.

- 13.1 (→ #482) **Pre-deploy**: decrypt `blockchain.rpcUrl` from prod ESC; verify the URL host matches a known Polygon mainnet provider AND contains NO `amoy`/`mumbai`/`sepolia`/`testnet` substring.
- 13.2 (→ #482) **Pre-deploy**: decrypt `blockchain.bundlerApiKey` from prod ESC; query the bundler's `chainId`; confirm it equals `137` (Polygon mainnet) or the mainnet chainId of the chosen target chain.
- 13.3 (→ #482) If either §13.1 or §13.2 fails: `esc env set liverty-music/prod pulumiConfig.blockchain.<key>` with the correct mainnet value; `pulumi up --stack prod` to propagate; re-run §13.1 + §13.2. HALT here until both pass.
- 13.4 (→ #482) **Deploy**: deploy the ticket SBT contract to Polygon mainnet (or the target EVM mainnet) using the prod deployer private key from `blockchain.deployerPrivateKey`. Record the deployed contract address.
- 13.5 (→ #482) Run the backend's existing SBT integration test against the deployed mainnet address; confirm `name()`, `symbol()`, `owner()`, `totalSupply()` respond correctly.
- 13.6 (→ #482) Open a cloud-provisioning PR updating the `TICKET_SBT_ADDRESS=` value in:
  - `k8s/namespaces/backend/overlays/prod/server/configmap.env`
  - `k8s/namespaces/backend/overlays/prod/consumer/configmap.env`
  - `k8s/namespaces/backend/overlays/prod/cronjob/concert-discovery/configmap.env`
- 13.7 (→ #482) Review + merge; ArgoCD picks up the new configmap; Reloader rolls server-app + consumer-app pods.
- 13.8 (→ #482) Verify via backend logs that the SBT client picks up the new contract address.

## 14. Operator: Post-deploy blockchain owner() verification (Phase 13.5)

The pre-deploy `rpcUrl` + bundler `chainId` checks are now in §13.1-§13.3 (gated before §13.4 fires). §14 is the post-deploy check that the deployed contract's `owner()` matches the deployer key's derived address — this can only happen after §13.4 has produced an address.

**Status: deferred to follow-up #482** (depends on §13.4 mainnet deploy; same follow-up as §13).

- 14.1 (→ #482) Decrypt `blockchain.deployerPrivateKey` from prod ESC; derive the Ethereum address; verify it equals the `owner()` of the mainnet SBT contract from §13.4.
- 14.2 (→ #482) If mismatch: investigate (likely the ESC private key was rotated post-deploy or never matched). Operator-attended remediation; do NOT silently rotate the key, because the deployed contract's owner is fixed at deploy time.

## 15. Operator: Verify prod admin Google sub (Phase 13.5 continued)

**Status: deferred to follow-up #482.** Single-operator UI walk-through; cannot be done by code alone.

- 15.1 (→ #482) Sign in to `https://auth.liverty-music.app/ui/console` with pannpers' Google account. The first sign-in attempt SHALL either succeed (sub matches what's in ESC) or fail with "user not found" (sub mismatch).
- 15.2 (→ #482) If sign-in fails, decrypt prod `zitadel.adminGoogleSubs.pannpers`; obtain the actual sub from the failed Zitadel IdP exchange logs or by listing the auto-created (unlinked) HumanUser in the admin org.
- 15.3 (→ #482) `esc env set liverty-music/prod pulumiConfig.zitadel.adminGoogleSubs.pannpers "<actual-sub>" --secret`.
- 15.4 (→ #482) `pulumi up --stack prod` to update the IdPLink resource.
- 15.5 (→ #482) Re-attempt sign-in; confirm success → IAM_OWNER role visible in Console.

## 16. Operator: Frontend prod preview artist content (Phase 13.5 continued, low priority)

**Status: deferred to follow-up #482** (curation depends on prod DB state + product decision; bundled with the §13-18 operator follow-up).

- 16.1 (→ #482) Curate a prod-appropriate list of 11 artist UUIDs (sourced from prod DB) + 11 display names for `VITE_PREVIEW_ARTIST_IDS` / `VITE_PREVIEW_ARTIST_NAMES` in `frontend/.env.prod`.
- 16.2 (→ #482) Open a frontend PR with the curated list; cut the next Release (e.g., `v1.0.1`) to rebuild.

## 17. Operator: ESC stale field cleanup (Phase 14)

**Status: deferred to follow-up #482** (low-risk operator cleanup; bundled with §13-16 follow-up to avoid a stand-alone PR for `esc env rm`).

- 17.1 (→ #482) From the poly-repo workspace root (e.g., `~/dev/src/github.com/liverty-music/` or wherever your local workspace lives), run: `grep -rn "zitadel\.domain\|zitadel\.orgId\|pulumiJwtProfileJson" specification/ backend/ frontend/ cloud-provisioning/` — confirm zero readers in any of the 4 repos. Adjust directory names to match your local workspace layout.
- 17.2 (→ #482) `esc env rm liverty-music/prod pulumiConfig.zitadel.domain`.
- 17.3 (→ #482) `esc env rm liverty-music/prod pulumiConfig.zitadel.orgId`.
- 17.4 (→ #482) `esc env rm liverty-music/dev pulumiConfig.zitadel.domain`.
- 17.5 (→ #482) `esc env rm liverty-music/dev pulumiConfig.zitadel.orgId`.
- 17.6 (→ #482) `esc env rm liverty-music/dev pulumiConfig.zitadel.pulumiJwtProfileJson`.
- 17.7 (→ #482) `pulumi preview --stack dev` — expect zero diff (proof no reader).
- 17.8 (→ #482) `pulumi preview --stack prod` — expect zero diff.

## 18. Final: End-to-end prod smoke (Phase 15)

**Status: deferred to follow-up #482** (full e2e smoke is only meaningful AFTER §13 mainnet SBT lands + §15 admin sub verified, since several smoke steps exercise both surfaces). Smoke coverage was achieved per-phase: §10.5 healthz/OIDC curl, §11.3 zero ImagePullBackOff, §12 pulumi preview confirming monitoring resources exist. Apex SPA load + sign-up + sign-in pipeline-smoke is the user's day-to-day verification path; the formal §18 checklist is the consolidated archive-time pass.

- 18.1 (→ #482) Visit `https://liverty-music.app/`; confirm SPA loads, no console errors, no `dev.liverty-music.app` requests in DevTools Network tab.
- 18.2 (→ #482) Sign up a new test user via prod SPA; confirm email verification email arrives (from `noreply@mail.liverty-music.app`).
- 18.3 (→ #482) Sign in the new test user; confirm OIDC redirect lands at `auth.liverty-music.app` and returns a JWT with the `email` claim.
- 18.4 (→ #482) Follow an artist; confirm the action persists (backend DB write).
- 18.5 (→ #482) Subscribe to push notifications via the prod SPA; trigger a backend notification path; confirm browser receives the push without signature failure (this is the §6 VAPID end-to-end verification).
- 18.6 (→ #482) In GCP Console → Monitoring → Alerting, trigger a test alert (e.g., emit a fake ERROR log via `gcloud logging write`); confirm both the Slack channel and the Google Chat space receive the notification.
- 18.7 (→ #482) Confirm `kubectl --context=prod -n argocd get applications` shows all 14 apps `Synced/Healthy` (including `backend-migrations`).
- 18.8 (→ #482) Mark this change ready for `/opsx:archive`.
