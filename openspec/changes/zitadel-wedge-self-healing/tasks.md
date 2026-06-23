## 1. Restore prod replica posture (bound blast radius)

- [x] 1.1 In the `zitadel` prod overlay, explicitly set `replicaCount: 2` and PDB `minAvailable: 1` for `zitadel-api`, reconciling the observed `replicas: 1` drift
- [x] 1.2 `kustomize build` the prod overlay and confirm the rendered `zitadel-api` Deployment has `replicas: 2` and the PDB has `minAvailable: 1`

## 2. Self-healing watchdog CronJob (prod)

- [x] 2.1 Add a watchdog `CronJob` manifest to the `zitadel` prod overlay, modeled on `overlays/dev/cronjob-restart-zitadel.yaml`: every ~1 min, `concurrencyPolicy: Forbid`, an image carrying both `curl` and `kubectl` (e.g. `alpine/k8s:1.32.x`), Spot `nodeSelector`, minimal resources
- [x] 2.2 Add a dedicated `ServiceAccount` + `Role` (`get`/`patch` on `deployments`, restricted to `zitadel-api`) + `RoleBinding` in the `zitadel` namespace, mirroring the dev restart RBAC
- [x] 2.3 Implement the probe script: guard on `/debug/healthz`==200; probe `/oauth/v2/authorize` with valid prod params (`client_id=373015520582107291`, `redirect_uri=https://liverty-music.app/auth/callback`, `response_type=code&scope=openid` + PKCE) N times (~3 × 5s) with `--max-time` above normal latency but below the gateway timeout; restart only if all N hang (HTTP 000)
- [x] 2.4 Ship the CronJob in **dry-run/observe mode** first (log the restart decision, skip the actual `rollout restart`); document how to flip to active (remove the dry-run guard / `suspend: false`)
- [x] 2.5 Wire the new manifests into the prod overlay `kustomization.yaml` resources; `kustomize build` cleanly
- [x] 2.6 Add an inline comment + runbook note recording the hardcoded prod `client_id`/`redirect_uri` coupling and the eventstore side-effect (per design.md Open Questions)

## 3. Validate & ship

- [x] 3.1 `make lint-k8s` (or repo equivalent) passes for the zitadel prod overlay
- [ ] 3.2 Open the `cloud-provisioning` PR; after merge, confirm ArgoCD syncs the replica bump + watchdog (dry-run) in prod
- [ ] 3.3 Soak the dry-run watchdog for one window; confirm zero false-positive restart decisions in its logs
- [ ] 3.4 Flip the watchdog to active (restart-enabled) via a follow-up commit once the dry-run is clean
- [ ] 3.5 Validate recovery: confirm prod `zitadel-api` is at 2 replicas, and (on the next genuine wedge, or a controlled one) the watchdog auto-restarts within ~2 min and a fresh `/oauth/v2/authorize` returns `302`
- [ ] 3.6 Run `openspec validate zitadel-wedge-self-healing --strict`; archive once shipped to prod and verified

## 4. Deferred follow-ups (tracked, not implemented here)

- [ ] 4.1 Evaluate a read-only probe target that still triggers the wedged projection (eliminate the auth-request side-effect)
- [ ] 4.2 Add a notification alert via a viable signal (watchdog-restart log-based metric, or Gateway 504 rate) — the OIDCService latency metric is dropped at the OTLP collector and cannot be used as-is
- [ ] 4.3 Refresh `docs/runbooks/zitadel-hang.md` to reflect self-healing + the authorize-based verification (don't rely on `/debug/healthz`=200 as proof of recovery)
