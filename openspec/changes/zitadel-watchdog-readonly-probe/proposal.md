## Why

The self-healing watchdog (shipped in `zitadel-wedge-self-healing`) detects the projection-trigger wedge by probing `/oauth/v2/authorize` with valid OIDC params. That works, but the probe is a **write**: each healthy probe creates a throwaway OIDC auth request, and Zitadel **never auto-cleans auth requests** (confirmed in the docs), so on the small prod `db-f1-micro` this is unbounded eventstore growth (~1440 event-streams/day) plus steady load on the very projection path that wedges. It also hardcodes the prod consumer `client_id` + `redirect_uri`.

A source-level investigation found a clean read-only alternative: the v2 `ProjectService/ListProjectRoles` gRPC method calls `SearchProjectRoles(ctx, true, …)`, which triggers `ProjectRoleProjection.Trigger(WithAwaitRunning())` — the **exact projection that wedged on 2026-06-23** — on every call, as a pure read (no eventstore write). Verified against prod: the endpoint is reachable and unauthenticated calls return `401` fast (auth is enforced before the trigger), so the probe must carry a valid credential to reach the wedge path.

This change swaps the probe to that read-only call, eliminating the write side-effect and the consumer-client coupling, while keeping (and slightly improving) wedge-detection fidelity. Zitadel offers no official mechanism for this (no config to disable trigger-on-read, no projection-health endpoint/metric, no self-healing, and `#10103` is still open), so the watchdog remains the right tool — this change just makes it side-effect-free.

## What Changes

- **Swap the watchdog probe** from `POST`/`GET /oauth/v2/authorize` (write) to the read-only Connect/gRPC `zitadel.project.v2.ProjectService/ListProjectRoles` over HTTP+JSON, against a **static project id**, returning quickly when healthy and hanging when wedged.
- **Provision a dedicated, minimal-scope machine user + Personal Access Token** for the watchdog (read access to project roles only), export the PAT to GSM, and sync it into the `zitadel` namespace via External Secrets; mount it in the watchdog CronJob as a bearer token.
- **Remove** the hardcoded consumer `client_id` / `redirect_uri` from the watchdog (this resolves the earlier "decouple from the consumer app" follow-up — the coupling moves to the watchdog's own PAT, not a product client).
- **Keep all conservative guards** (N-of-N in-run hangs, `/debug/healthz`==200 precondition, `concurrencyPolicy: Forbid`) and the `until-upstream-zitadel-10103-fix` stopgap annotation.
- **Refresh the runbook** (`docs/runbooks/zitadel-hang.md`) to reflect self-healing + the read-only probe and the "check the watchdog first, verify via an auth-flow probe (not `/debug/healthz`)" flow.

## Capabilities

### New Capabilities
<!-- none — this refines the existing self-healing watchdog requirement. -->

### Modified Capabilities
- `zitadel-self-hosted-deployment`: change the "Self-healing watchdog auto-restarts a wedged Zitadel API" requirement so the detection signal is the read-only `ProjectService/ListProjectRoles` call authenticated by a dedicated watchdog machine-user PAT (instead of the write-bearing `/oauth/v2/authorize` probe with a consumer client id), and require the PAT to be least-privilege and delivered via GSM + External Secrets.

## Impact

- **Repo**: `cloud-provisioning` only.
  - Pulumi (`src/zitadel/…`): a new `zitadel.MachineUser` + `PersonalAccessToken` (read-project-roles scope) and a GSM secret holding the token.
  - K8s (`k8s/namespaces/zitadel/overlays/prod/`): an `ExternalSecret` syncing the PAT into the namespace; the watchdog CronJob rewritten to `curl` the Connect endpoint with `Authorization: Bearer` and parse hang-vs-response; drop the authorize URL/client env.
- **Behavior**: zero eventstore writes from probing (was ~1440/day); detection now exercises `ProjectRoleProjection` (the observed wedge). No change to login behavior or to the 2-replica posture.
- **New dependency / risk**: a long-lived watchdog PAT that must be stored, rotated before expiry, and least-privilege. Fail-safe is preserved — an invalid/expired PAT yields a fast `401` (read as "healthy"), so it stops detecting rather than false-restarting; this MUST be covered by PAT-expiry monitoring or a long/auto-rotated token.
- **Stopgap**: unchanged — when upstream removes the auth-request/project-role read-projections (`#10103` and siblings), the wedge disappears and the whole watchdog can be retired.
