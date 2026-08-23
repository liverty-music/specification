## 1. Compute and verify the deny list

- [x] 1.1 Recompute `10.0.0.0/8` minus the prod webhook Service CIDR `10.30.0.0/20` with `ipaddress.address_exclude` and confirm the 12 CIDRs match design.md Decision 1
- [x] 1.2 Assemble the full prod deny list = all 13 v4.17.1 defaults with `10.0.0.0/8` replaced by the 12 CIDRs; diff it against the deployed version's `cmd/defaults.yaml` `HTTPClient.DenyList` and confirm every other entry (esp. `169.254.0.0/16`, `127.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `0.0.0.0/8`, `100.64.0.0/10`, `198.18.0.0/15`, and all IPv6 entries) is preserved
- [x] 1.3 Confirm the prod webhook ClusterIP (`fan-api-webhook-svc`, `10.30.12.134`) falls inside `10.30.0.0/20` and is NOT in any denied CIDR

## 2. Apply the config in cloud-provisioning

- [x] 2.1 Add `HTTPClient.DenyList` (full list from 1.2) under `zitadel.configmapConfig` in the prod overlay values, so prod gets the `10.30.0.0/20`-hole list (deep-merges with base `configmapConfig`; env-scoped)
- [x] 2.2 Render the manifests (kustomize/helm) and confirm the config appears in the rendered Zitadel config with the exact expected value (24 entries, `169.254.0.0/16` preserved, `10.0.0.0/8` hole-punched) and no dropped entries
- [x] 2.3 Run the cloud-provisioning checks/lint and open the PR per the standard workflow (issue #445, PR #446)

## 3. Deploy and verify (prod)

- [x] 3.1 Merge → confirm ArgoCD syncs and the Zitadel pods roll with the new env (ArgoCD Synced/Healthy at `da99a2a`; pods rolled `564cf5454c`→`66b5cfdc54` with new `checksum/configmap`)
- [x] 3.2 Verify `POST /oauth/v2/token` returns success (not HTTP 500 `Errors.Internal`) and a real login completes end-to-end (user confirmed successful login post-roll; zero token 500s in logs)
- [x] 3.3 Confirm the `error calling target ... address is denied by '10.0.0.0/8'` log line has stopped for both `/pre-access-token` and `/account-login-event` (0 deny + 0 target errors since roll; only benign session WARNs)
- [x] 3.4 Spot-check that a denied range is still blocked (metadata `169.254.169.254` remains denied) — via config review, since it is not externally exercisable (rendered + running config keep `169.254.0.0/16`)

## 4. Follow-ups

- [x] 4.1 Add a note/checklist item to re-review this deny-list override against `defaults.yaml` on every future Zitadel version bump (merged inline comment in `overlays/prod/values.yaml`; runbook version-bump procedure note shipped in PR #447)
- [x] 4.2 Record the dev-overlay Service CIDR value to apply when the dev env is next brought up (recorded as design.md Open Question; dev cluster stopped so the CIDR value cannot be fetched now)
