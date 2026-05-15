## 1. Cloud-provisioning: Prod Zitadel SPA OIDC client (Phase 2 — `liverty-music/cloud-provisioning`)

- [ ] 1.1 Inspect existing `Zitadel` component to confirm the `web-frontend` `ApplicationOidc` is provisioned for all envs (dev already wired); if it's gated on `env === 'dev'`, remove the gate so prod also gets one.
- [ ] 1.2 Export `webFrontendClientId` and `productOrgId` as Pulumi stack outputs so operators can `pulumi stack output` them for `.env.prod`.
- [ ] 1.3 `pulumi preview --stack prod` and capture the diff in the PR description.
- [ ] 1.4 Open PR; review; merge.

## 2. Cloud-provisioning: Prod `ApplicationOidc` apply (Phase 3 — operator-attended)

- [ ] 2.1 Trigger `pulumi up --stack prod` manually via Pulumi Cloud console.
- [ ] 2.2 Verify the new resource appeared in prod stack state.
- [ ] 2.3 Capture `pulumi stack output webFrontendClientId` and `pulumi stack output productOrgId` from the prod stack; paste them into a private notes file under `tmp/` for use in §7.

## 3. Backend: Release-tag-triggered prod build path (Phase 4 — `liverty-music/backend`)

- [ ] 3.1 In `.github/workflows/deploy.yml`, change the trigger block to dual `push: branches: [main]` + `release: types: [published]`.
- [ ] 3.2 Add job-level `environment:` selector: `${{ github.event_name == 'release' && 'prod' || 'dev' }}`.
- [ ] 3.3 In the matrix step "Set Image URI", make `PROJECT_ID` resolve from the selected environment (`vars.PROJECT_ID` already points at `liverty-music-prod` in the prod environment, per existing Pulumi-managed GitHub vars).
- [ ] 3.4 In "Build and Push Docker Image" step, set tags conditionally: dev builds get `${IMAGE_URI}:latest,${IMAGE_URI}:${sha},${IMAGE_URI}:main`; release builds get `${IMAGE_URI}:${github.event.release.tag_name},${IMAGE_URI}:${sha}`.
- [ ] 3.5 Add a job-level guard: prod path SHALL NOT fire on `push` events; dev path SHALL NOT fire on `release` events.
- [ ] 3.6 Verify `make check` (or equivalent) still passes on the workflow YAML.

## 4. Backend: Atlas prod overlay (Phase 4 continued — `liverty-music/backend`)

- [ ] 4.1 Create `liverty-music/backend:k8s/atlas/overlays/prod/kustomization.yaml` mirroring the dev overlay structure.
- [ ] 4.2 Patch the `AtlasMigration` resource for the prod Cloud SQL connection (PSC DNS `298474959c18.25pf3r4b6sfkn.asia-northeast2.sql.goog`, database `liverty-music`, user `backend-app@liverty-music-prod.iam`).
- [ ] 4.3 Confirm the migration source ConfigMap is generated from the same `migrations/` directory as dev (no fork).
- [ ] 4.4 Run `kubectl kustomize k8s/atlas/overlays/prod` locally; verify exit 0 + sensible YAML output.
- [ ] 4.5 Compare the prod overlay's migration plan against the current prod Cloud SQL state via `atlas migrate diff` (dry-run, against prod via an operator's authenticated psql session). Confirm no destructive operations on first apply.
- [ ] 4.6 Open backend PR bundling §3 + §4; review; merge.

## 5. Backend: Cut prod Release (Phase 5 — operator-attended)

- [ ] 5.1 Tag `liverty-music/backend:main` HEAD as `v1.0.0` (or the next semver).
- [ ] 5.2 Publish the GitHub Release for that tag.
- [ ] 5.3 Watch `gh run watch` for `deploy.yml`; confirm all four images (`server`, `consumer`, `concert-discovery`, `artist-image-sync`) pushed to `liverty-music-prod/backend/`.
- [ ] 5.4 Verify via `gcloud artifacts docker images list asia-northeast2-docker.pkg.dev/liverty-music-prod/backend --include-tags` that each image carries both the `v1.0.0` tag and the commit SHA.

## 6. Operator: VAPID keypair verification + (if needed) regeneration (Phase 6 — must precede frontend `.env.prod` commit)

This section runs BEFORE §7 so `.env.prod` is committed with the authoritative VAPID public key in one shot. Without this ordering, Mode B would force a v1.0.1 frontend rebuild AND an overlay re-pin (PR review noted).

- [ ] 6.1 Decrypt the prod `vapid-private-key` GSM secret: `gcloud secrets versions access latest --secret=vapid-private-key --project=liverty-music-prod`.
- [ ] 6.2 Derive the public point from the private key (Base64URL-encoded uncompressed P-256). Compare to the current `VAPID_PUBLIC_KEY` value in `cloud-provisioning/k8s/namespaces/backend/overlays/prod/server/configmap.env`.
- [ ] 6.3 If match (Mode A in design D9): record the GSM-derived public key value (which equals the current configmap value) for use in §7.1 (`.env.prod`). No cloud-provisioning PR needed in this phase. Proceed to §7.
- [ ] 6.4 If mismatch (Mode B): generate a fresh prod VAPID keypair locally (`openssl ecparam -name prime256v1 -genkey -noout -out vapid-private.pem`; derive public point in Base64URL).
- [ ] 6.5 (Mode B only) Open a cloud-provisioning PR ("Mode B VAPID rotation") updating `VAPID_PUBLIC_KEY=` to the newly-generated public point in three backend prod configmap.env files (`server`, `consumer`, `cronjob/concert-discovery`). Review. Do NOT merge yet.
- [ ] 6.6 (Mode B only) `esc env set liverty-music/prod pulumiConfig.gcp.vapidPrivateKey "$(cat vapid-private.pem)" --secret`. ESC is not yet applied to GSM until the next `pulumi up`.
- [ ] 6.7 (Mode B only) **Atomic apply window** (target: sub-minute mismatch). In rapid succession:
  - Merge the §6.5 cloud-provisioning PR. ArgoCD will detect the change on its next poll cycle (~30s) and sync the configmaps; Reloader will roll the backend pods with the new configmap.
  - Immediately run `pulumi up --stack prod` (manual via Pulumi Cloud console) — this publishes the new GSM secret version.
  - Force-sync ESO right after the Pulumi apply succeeds: `kubectl annotate externalsecret server-backend-secrets -n backend force-sync=now-$(date +%s) --overwrite`. ESO refreshes the in-cluster Secret; Reloader rolls the backend pods again with the new GSM private key.
- [ ] 6.8 (Mode B only) Acknowledge: there is an unavoidable ~30-90s window where the rolled pods have either OLD-private + NEW-public or NEW-private + OLD-public (the two updates can't be truly atomic given ArgoCD and ESO are independent reconciliation channels). Prod is pre-launch with zero live push subscriptions, so this window is acceptable. If push subscriptions ever exist at the time of rotation, briefly disable subscription endpoints first.
- [ ] 6.9 Record the public key value (Mode A: GSM-derived = current configmap value; Mode B: freshly generated) in `tmp/vapid-public-prod.txt` for consumption by §7.1.

## 7. Frontend: `.env.prod` + Release-tag-triggered prod build path (Phase 7 — `liverty-music/frontend`)

- [ ] 7.1 Create `liverty-music/frontend:.env.prod` with the full `VITE_*` key set:
  - `VITE_LOG_LEVEL=info`
  - `VITE_API_BASE_URL=https://api.liverty-music.app`
  - `VITE_ZITADEL_ISSUER=https://auth.liverty-music.app`
  - `VITE_ZITADEL_CLIENT_ID=<webFrontendClientId from §2.3>`
  - `VITE_ZITADEL_ORG_ID=<productOrgId from §2.3>`
  - `VITE_VAPID_PUBLIC_KEY=<value from §6.7>` (authoritative — Mode A or Mode B both resolved upstream)
  - `VITE_PREVIEW_ARTIST_IDS` / `_NAMES` — initial copy from dev; flag follow-up as task §16
- [ ] 7.2 In `.github/workflows/push-image.yaml`, add `release: types: [published]` trigger alongside `push: branches: [main]`.
- [ ] 7.3 Add job-level `environment:` selector: `${{ github.event_name == 'release' && 'prod' || 'dev' }}`.
- [ ] 7.4 Add a build step that runs `npm run build -- --mode prod` only on the prod path (the existing dev build remains `npm run build`).
- [ ] 7.5 Set image tags conditionally per §3.4 pattern; prod gets `${tag}` and `${sha}`, dev keeps the existing triple.
- [ ] 7.6 Verify `tsc` + biome on the workflow + `.env.prod`.
- [ ] 7.7 Open frontend PR; review; merge.

## 8. Frontend: Cut prod Release (Phase 8 — operator-attended)

- [ ] 8.1 Tag `liverty-music/frontend:main` HEAD as `v1.0.0` (or matching backend's version).
- [ ] 8.2 Publish the GitHub Release.
- [ ] 8.3 Watch `gh run watch` for `push-image.yaml`; confirm `web-app:v1.0.0` pushed to `liverty-music-prod/frontend/`.
- [ ] 8.4 Pull the prod image locally; extract `/usr/share/caddy/index.html` and `assets/*.js`; verify:
  - No occurrences of `dev.liverty-music.app` in any chunk.
  - `api.liverty-music.app` appears in at least one chunk.
  - `auth.liverty-music.app` appears in at least one chunk.
  - The embedded OIDC `client_id` matches the value captured in §2.3.
  - The embedded `VITE_VAPID_PUBLIC_KEY` matches the value from §6.7.

## 9. Cloud-provisioning: Prod overlay image pinning + IAM revocation runbook (Phase 9 — `liverty-music/cloud-provisioning`)

Note: the Mode B `VAPID_PUBLIC_KEY=` configmap update was moved to §6.5+ (Phase 6) so the GSM rotation and configmap update land in the same coordinated apply window (per design D9 atomicity).

- [ ] 9.1 In `k8s/namespaces/backend/overlays/prod/kustomization.yaml`, add an `images:` block pinning each of `server`, `consumer`, `concert-discovery`, `artist-image-sync` to `asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/<name>:<sha-from-§5>`.
- [ ] 9.2 In `k8s/namespaces/frontend/overlays/prod/kustomization.yaml`, add an `images:` block pinning `web-app` to `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:<sha-from-§8>`.
- [ ] 9.3 Run `kustomize build k8s/namespaces/backend/overlays/prod` and `... frontend/overlays/prod`; grep rendered Deployment images:
  - Every backend Deployment image SHALL match `^asia-northeast2-docker\.pkg\.dev/liverty-music-prod/backend/`.
  - The frontend Deployment image SHALL match `^asia-northeast2-docker\.pkg\.dev/liverty-music-prod/frontend/`.
  - No rendered image URI contains the substring `liverty-music-dev/`.
- [ ] 9.4 Add `docs/runbooks/revoke-cross-project-ar-iam.md` documenting the exact `gcloud projects remove-iam-policy-binding` invocation with a "MUST run AFTER overlay merge" guard.
- [ ] 9.5 Open cloud-provisioning PR; review; merge.

## 10. Cloud-provisioning: Verify ArgoCD prod cutover (Phase 10 — operator-attended)

- [ ] 10.1 Wait for ArgoCD to detect the cloud-provisioning main-branch change.
- [ ] 10.2 In ArgoCD UI / `kubectl --context=prod -n argocd get applications`, confirm `backend` and `frontend` apps reach `Synced/Healthy`.
- [ ] 10.3 `kubectl --context=prod -n backend get pod -o yaml | grep image:` — every image SHALL start with `liverty-music-prod/backend/`.
- [ ] 10.4 `kubectl --context=prod -n frontend get pod -o yaml | grep image:` — image SHALL start with `liverty-music-prod/frontend/`.
- [ ] 10.5 Curl smoke: `api.liverty-music.app/healthz` returns 401 (auth gate reachable); `auth.liverty-music.app/.well-known/openid-configuration` returns 200.

## 11. Operator: Revoke manual cross-project IAM grant (Phase 11)

- [ ] 11.1 Re-verify §10.3 and §10.4 — no pod still references a dev-AR image.
- [ ] 11.2 Run `gcloud projects remove-iam-policy-binding liverty-music-dev --member='serviceAccount:gke-node@liverty-music-prod.iam.gserviceaccount.com' --role='roles/artifactregistry.reader'`.
- [ ] 11.3 Wait 5 minutes; `kubectl --context=prod get pods -A | grep -E 'ImagePullBackOff|ErrImagePull'` — output SHALL be empty.
- [ ] 11.4 Verify via `gcloud projects get-iam-policy liverty-music-dev --flatten='bindings[].members' --filter='bindings.members~liverty-music-prod'` returns empty.

## 12. Operator: Prod ESC seeding (Phase 12)

- [ ] 12.1 Create a Slack notification channel for prod in GCP Console (Monitoring → Alerting → Edit notification channels → Slack). Record the channel ID.
- [ ] 12.2 `esc env set liverty-music/prod pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend "<channel-id>"`.
- [ ] 12.3 `esc env set liverty-music/prod pulumiConfig.gcp.billingAlertEmail "pannpers@pannpers.dev"` (or the operator's preferred billing contact).
- [ ] 12.4 `esc env set liverty-music/prod pulumiConfig.gcp.budgetAmountJpy "10000"` (or operator-chosen prod budget; defaults to 3000 if unset).
- [ ] 12.5 `pulumi preview --stack prod`; confirm the diff shows MonitoringComponent + ZitadelMonitoringComponent + cost-budget + billing-alert-email creates.
- [ ] 12.6 `pulumi up --stack prod` (manual via Pulumi Cloud console).
- [ ] 12.7 Verify `gcloud monitoring channels list --project=liverty-music-prod` includes the new Slack channel + Google Chat + email channels.
- [ ] 12.8 Verify GCP Console → Billing → Budgets & Alerts shows the new prod budget.

## 13. Operator: Mainnet ticket SBT contract deployment (Phase 13)

- [ ] 13.1 Deploy the ticket SBT contract to Polygon mainnet (or the target EVM mainnet) using the prod deployer private key from `blockchain.deployerPrivateKey`. Record the deployed contract address.
- [ ] 13.2 Run the backend's existing SBT integration test against the deployed mainnet address; confirm `name()`, `symbol()`, `owner()`, `totalSupply()` respond correctly.
- [ ] 13.3 Open a cloud-provisioning PR updating the `TICKET_SBT_ADDRESS=` value in:
  - `k8s/namespaces/backend/overlays/prod/server/configmap.env`
  - `k8s/namespaces/backend/overlays/prod/consumer/configmap.env`
  - `k8s/namespaces/backend/overlays/prod/cronjob/concert-discovery/configmap.env`
- [ ] 13.4 Review + merge; ArgoCD picks up the new configmap; Reloader rolls server-app + consumer-app pods.
- [ ] 13.5 Verify via backend logs that the SBT client picks up the new contract address.

## 14. Operator: Verify blockchain mainnet values (Phase 13.5)

- [ ] 14.1 Decrypt `blockchain.rpcUrl` from prod ESC; verify it points at Polygon mainnet (no `amoy`/`mumbai`/`sepolia`/`testnet` substrings).
- [ ] 14.2 Decrypt `blockchain.deployerPrivateKey`; derive the Ethereum address; verify it equals the `owner()` of the mainnet SBT contract from §13.
- [ ] 14.3 Decrypt `blockchain.bundlerApiKey`; query the bundler's `chainId`; confirm it equals the mainnet chainId (137 for Polygon).
- [ ] 14.4 If any value is wrong, `esc env set liverty-music/prod pulumiConfig.blockchain.<key>` with the correct mainnet value.

## 15. Operator: Verify prod admin Google sub (Phase 13.5 continued)

- [ ] 15.1 Sign in to `https://auth.liverty-music.app/ui/console` with pannpers' Google account. The first sign-in attempt SHALL either succeed (sub matches what's in ESC) or fail with "user not found" (sub mismatch).
- [ ] 15.2 If sign-in fails, decrypt prod `zitadel.adminGoogleSubs.pannpers`; obtain the actual sub from the failed Zitadel IdP exchange logs or by listing the auto-created (unlinked) HumanUser in the admin org.
- [ ] 15.3 `esc env set liverty-music/prod pulumiConfig.zitadel.adminGoogleSubs.pannpers "<actual-sub>" --secret`.
- [ ] 15.4 `pulumi up --stack prod` to update the IdPLink resource.
- [ ] 15.5 Re-attempt sign-in; confirm success → IAM_OWNER role visible in Console.

## 16. Operator: Frontend prod preview artist content (Phase 13.5 continued, low priority)

- [ ] 16.1 Curate a prod-appropriate list of 11 artist UUIDs (sourced from prod DB) + 11 display names for `VITE_PREVIEW_ARTIST_IDS` / `VITE_PREVIEW_ARTIST_NAMES` in `frontend/.env.prod`.
- [ ] 16.2 Open a frontend PR with the curated list; cut the next Release (e.g., `v1.0.1`) to rebuild.

## 17. Operator: ESC stale field cleanup (Phase 14)

- [ ] 17.1 From the poly-repo workspace root (e.g., `~/dev/src/github.com/liverty-music/` or wherever your local workspace lives), run: `grep -rn "zitadel\.domain\|zitadel\.orgId\|pulumiJwtProfileJson" specification/ backend/ frontend/ cloud-provisioning/` — confirm zero readers in any of the 4 repos. Adjust directory names to match your local workspace layout.
- [ ] 17.2 `esc env rm liverty-music/prod pulumiConfig.zitadel.domain`.
- [ ] 17.3 `esc env rm liverty-music/prod pulumiConfig.zitadel.orgId`.
- [ ] 17.4 `esc env rm liverty-music/dev pulumiConfig.zitadel.domain`.
- [ ] 17.5 `esc env rm liverty-music/dev pulumiConfig.zitadel.orgId`.
- [ ] 17.6 `esc env rm liverty-music/dev pulumiConfig.zitadel.pulumiJwtProfileJson`.
- [ ] 17.7 `pulumi preview --stack dev` — expect zero diff (proof no reader).
- [ ] 17.8 `pulumi preview --stack prod` — expect zero diff.

## 18. Final: End-to-end prod smoke (Phase 15)

- [ ] 18.1 Visit `https://liverty-music.app/`; confirm SPA loads, no console errors, no `dev.liverty-music.app` requests in DevTools Network tab.
- [ ] 18.2 Sign up a new test user via prod SPA; confirm email verification email arrives (from `noreply@mail.liverty-music.app`).
- [ ] 18.3 Sign in the new test user; confirm OIDC redirect lands at `auth.liverty-music.app` and returns a JWT with the `email` claim.
- [ ] 18.4 Follow an artist; confirm the action persists (backend DB write).
- [ ] 18.5 Subscribe to push notifications via the prod SPA; trigger a backend notification path; confirm browser receives the push without signature failure (this is the §6 VAPID end-to-end verification).
- [ ] 18.6 In GCP Console → Monitoring → Alerting, trigger a test alert (e.g., emit a fake ERROR log via `gcloud logging write`); confirm both the Slack channel and the Google Chat space receive the notification.
- [ ] 18.7 Confirm `kubectl --context=prod -n argocd get applications` shows all 14 apps `Synced/Healthy` (including `backend-migrations`).
- [ ] 18.8 Mark this change ready for `/opsx:archive`.
