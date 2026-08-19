## 1. Refine the watchdog hang classifier (cloud-provisioning)

- [x] 1.1 `k8s/namespaces/zitadel/overlays/prod/cronjob-watchdog-zitadel.yaml`: capture `%{time_total}` alongside `%{http_code}` in the probe `curl`; count a hang when `http_code=000` OR whole-seconds(`time_total`) `>= WATCHDOG_SLOW_SEC`.
- [x] 1.2 Add `WATCHDOG_SLOW_SEC` env (default `"8"`); bump probe `--max-time 10 → 12` (above the ~10s server deadline); reduce inter-probe `sleep 5 → 3` to keep the worst-case run < 60s under `concurrencyPolicy: Forbid`.
- [x] 1.3 Keep `401`/`403` credential fail-safe, the `/debug/healthz=200` precondition, N-consecutive-hangs rule, and read-only probe target unchanged.
- [x] 1.4 Update the manifest header/comments to document time-based detection and why 000-only missed the slow-5xx variant.

## 2. Verify

- [x] 2.1 `kubectl kustomize --enable-helm --load-restrictor LoadRestrictionsNone k8s/namespaces/zitadel/overlays/prod` renders without error and the CronJob shows the new probe logic.
- [x] 2.2 Unit-check the shell classifier against representative cases: healthy fast 200, slow 5xx (~9.9s), curl timeout 000, slow 503 at threshold, fast transient 500, 401, slow 200, empty output. All classify correctly.
- [x] 2.3 kube-linter introduces no new findings on the watchdog CronJob (pre-existing chart-Job findings unaffected).

## 3. Ship + remediate the live prod instance

- [x] 3.1 Open cloud-provisioning PR; CI green; merge to main. (PR #415 merged 2026-08-18; spec delta #805 merged)
- [x] 3.2 Trigger prod ArgoCD sync (automatic on merge) and confirm the updated CronJob is applied. (ArgoCD synced `f7422bc`, Healthy; live CronJob shows `WATCHDOG_SLOW_SEC=8` + `--max-time 12` + `time_total`)
- [x] 3.3 Confirm the next natural wedge (or a controlled reproduction) now triggers an auto-restart. (Observed live minutes after sync: `zitadel-wedge-watchdog-29783839` logged 3/3 `→ hang` while healthz=200 and ran `rollout restart deployment/zitadel-api`; rollout succeeded to 2/2 fresh pods; next cycle healthy `200 @0.36s`, and a fast `503 @0.97s` was correctly NOT counted as a hang)

## 5. Replace CronJob watchdog with per-pod liveness probe sidecar (cloud-provisioning)

- [x] 5.1 Add `curl`-capable sidecar container to `zitadel-api` Helm values / overlay patch (`image: alpine/curl:8.21.0`; `command: ["sleep","infinity"]`; hardened `securityContext`; resource requests/limits). Implemented via Kustomize strategic-merge patch `zitadel-api-liveness-sidecar-patch.yaml`.
- [x] 5.2 Add `exec` liveness probe on the sidecar: same `ListProjectRoles` check with `WATCHDOG_SLOW_SEC=8`, `--max-time 12`, `failureThreshold=3`, `periodSeconds=20`, `initialDelaySeconds=60`.
- [x] 5.3 Mount the watchdog PAT secret into the sidecar (ExternalSecret `zitadel-watchdog-probe-pat` retained; Secret mounted into `zitadel-api` pod at `/var/run/watchdog/token`).
- [x] 5.4 Remove `cronjob-watchdog-zitadel.yaml` from `kustomization.yaml` resources; ExternalSecret retained (Secret now used by sidecar).
- [ ] 5.5 Kustomize dry-run clean ✓; kube-linter no new findings ✓; open cloud-provisioning PR; CI green; merge; ArgoCD sync confirmed.
- [ ] 5.6 Verify: observe two `zitadel-api` pod restarts triggered by liveness probe failures on different schedules (not simultaneous); confirm no full-outage window during the wedge cycle.

## 6. Follow-up

- [ ] 6.1 Once upstream zitadel/zitadel#10103 ships a fix and prod is pinned to it, remove the liveness probe sidecar, the PAT secret mount, and the GSM secret / ExternalSecret entirely (all carry `liverty-music.app/temporary: until-upstream-zitadel-10103-fix`).
