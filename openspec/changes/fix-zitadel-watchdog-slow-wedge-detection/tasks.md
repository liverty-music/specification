## 1. Refine the watchdog hang classifier (cloud-provisioning)

- [x] 1.1 `k8s/namespaces/zitadel/overlays/prod/cronjob-watchdog-zitadel.yaml`: capture `%{time_total}` alongside `%{http_code}` in the probe `curl`; count a hang when `http_code=000` OR whole-seconds(`time_total`) `>= WATCHDOG_SLOW_SEC`.
- [x] 1.2 Add `WATCHDOG_SLOW_SEC` env (default `"8"`); bump probe `--max-time 10 → 12` (above the ~10s server deadline); reduce inter-probe `sleep 5 → 3` to keep the worst-case run < 60s under `concurrencyPolicy: Forbid`.
- [x] 1.3 Keep `401`/`403` credential fail-safe, the `/debug/healthz=200` precondition, N-consecutive-hangs rule, and read-only probe target unchanged.
- [x] 1.4 Update the manifest header/comments to document time-based detection and why 000-only missed the slow-5xx variant.

## 2. Verify

- [x] 2.1 `kubectl kustomize --enable-helm --load-restrictor LoadRestrictionsNone k8s/namespaces/zitadel/overlays/prod` renders without error and the CronJob shows the new probe logic.
- [x] 2.2 Unit-check the shell classifier against representative cases: healthy fast 200, slow 5xx (~9.9s), curl timeout 000, slow 503 at threshold, fast transient 500, 401, slow 200, empty output. All classify correctly.
- [x] 2.3 kube-linter introduces no new findings on the watchdog CronJob (pre-existing chart-Job findings unaffected).

## 3. Ship time-based detection

- [x] 3.1 Open cloud-provisioning PR; CI green; merge to main. (PR #415 merged 2026-08-18; spec delta #805 merged)
- [x] 3.2 Trigger prod ArgoCD sync and confirm the updated CronJob is applied. (ArgoCD synced `f7422bc`; live CronJob shows `WATCHDOG_SLOW_SEC=8` + `--max-time 12` + `time_total`)
- [x] 3.3 Confirm the next natural wedge triggers an auto-restart. (Watchdog fired on a live wedge; rollout succeeded 2/2 fresh pods; next cycle healthy `200 @0.36s`)

## 4. Attempt per-pod liveness probe sidecar — reverted

- [x] 4.1 Implement `zitadel-api-liveness-sidecar-patch.yaml` with `watchdog-probe` sidecar and exec liveness probe (PR #425 merged 2026-08-19).
- [x] 4.2 Discover K8s design constraint: exec liveness probe failure restarts only the container owning the probe, not other pod containers. `watchdog-probe` entered CrashLoopBackOff (restart count 12); `zitadel` container restart count remained 0. Wedge continued unabated.
- [x] 4.3 Revert: remove CronJob, sidecar, and ExternalSecret from prod overlay (PR #429 merged 2026-08-19). Recovery is manual `kubectl -n zitadel rollout restart deploy/zitadel-api`.

## 5. Investigate and resolve root cause

- [x] 5.1 Identify wedge pattern: `projections.notifications` handler occupied DB connections continuously; `MaxOpenConns: 3` left zero connections for login `Trigger(WithAwaitRunning())` → QUERY-5Ngd9 → wedge at ~4-minute intervals.
- [x] 5.2 Confirm `projections.failed_events2` is empty (no poison events). Root cause is position backlog, not failed events.
- [x] 5.3 Identify backlog source: `projections.notifications.position` was rolled back to `1782101700`; eventstore latest is `1787110216`; handler needed to scan 5,994 events (4,586 `auth_request.added`) — useless re-scan monopolising the connection pool.
- [x] 5.4 Fix SMTP: pulumi up v221 activated `smtp-activation`; no new notification failures will accumulate.
- [x] 5.5 Advance `projections.notifications` position to current eventstore head (`1787110216`) via DB UPDATE; handler released from backlog.
- [x] 5.6 Confirm wedge resolved: 5-minute monitoring window showed QUERY-5Ngd9 = 0, pod RESTARTS = 0. Wedge has not recurred.
