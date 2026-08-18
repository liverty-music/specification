# Fix the Zitadel wedge watchdog to detect the slow-5xx wedge variant

## Why

The self-healing watchdog (`zitadel-self-hosted-deployment` capability) exists
to auto-restart a `zitadel-api` pod caught in the projection-trigger wedge
(zitadel/zitadel#10103, still OPEN upstream as of v4.17.x — no fix shipped).
It detects the wedge by probing `ProjectService/ListProjectRoles` and treating
a probe that "hangs past the gateway timeout" as the wedge signal.

The prod manifest implemented "hang" **too narrowly**: it counted a probe as
hung **only when `curl` returned `http_code=000`** (a full client-side timeout
at `--max-time 10`). But the wedge does not always time the client out. When
the projection trigger blocks, Zitadel's own internal ~10s deadline frequently
fires **first**, returning a **slow HTTP 500 at ~9.9s** — just under the old
`--max-time 10`. That is a real wedge, yet `http_code=000` never matched, so
`hangs` stayed at 0 and the watchdog **never restarted the pod**.

This was observed directly while trying to deactivate a test organizer: the
`RemoveUser` path wedged, `ListProjectRoles` returned slow 500s, `/debug/healthz`
stayed 200, and the watchdog took no action — the exact failure the watchdog was
built to prevent. The narrow `000`-only check made the safeguard effectively
inert against the most common manifestation of the wedge.

## What Changes

- **MODIFIED** `zitadel-self-hosted-deployment` — redefine the watchdog's "hang"
  detection as **time-based**, not HTTP-code-based. A probe counts as a hang
  when its **total time crosses a slow-response threshold** (whole seconds,
  `WATCHDOG_SLOW_SEC`, default 8s) **OR** it times out entirely (`http_code=000`).
  A **fast** response — a healthy sub-second `200`, or a fast transient error —
  is NOT a hang (preserving the conservative-against-false-restarts guarantee).
  The client `--max-time` is set above the server's internal deadline so a slow
  error is captured **with its timing** instead of racing to a bare `000`.
- Add a scenario asserting a **slow 5xx returned just under the client timeout**
  is detected as a wedge (the previously-missed case).
- Add a scenario asserting a **fast transient error** is NOT treated as a wedge.

No credential, RBAC, probe-target, read-only, or healthz-precondition behavior
changes — only the hang classifier is refined.

## Impact

- Affected capability: `zitadel-self-hosted-deployment` (watchdog requirement).
- Affected code: `cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/cronjob-watchdog-zitadel.yaml`
  (probe loop reads `%{time_total}`; `--max-time 10 → 12`; inter-probe `sleep 5 → 3`
  to keep the worst-case run under 60s; new `WATCHDOG_SLOW_SEC` env).
- Prod-only; the wedge and the watchdog are prod concerns. Rolling restart stays
  non-disruptive behind the 2-replica posture.
- Temporary: still annotated `until-upstream-zitadel-10103-fix`; removed when the
  upstream fix ships and is pinned.
