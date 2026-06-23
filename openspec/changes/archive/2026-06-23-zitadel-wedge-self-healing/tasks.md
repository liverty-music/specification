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
- [x] 3.2 Open the `cloud-provisioning` PR (#366); after merge, confirm ArgoCD synced the replica bump + watchdog (dry-run) in prod (verified: `zitadel-api` replicas=2, PDB minAvailable=1, watchdog CronJob created)
- [x] 3.3 Soak the dry-run watchdog; confirm zero false-positive restart decisions (verified: live runs logged `healthy: 0/3 probes hung — no action`)
- [x] 3.4 Flip the watchdog to active (#367, `WATCHDOG_DRY_RUN=false`); after ArgoCD sync, confirm active config and that a run still correctly takes no action on healthy prod (verified)
- [x] 3.5 `openspec validate zitadel-wedge-self-healing --strict` passes

Note: recovery on an actual wedge cannot be induced on prod and is therefore not a discrete task here — it is confirmed opportunistically via the watchdog's job logs on the next genuine occurrence. Deferred follow-ups (read-only probe target, a viable notification alert, runbook refresh) are documented in design.md Open Questions and the PR descriptions, to be picked up as separate work.
