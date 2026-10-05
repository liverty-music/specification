## Context

See proposal.md — Why. Current state that shapes the approach (all in `liverty-music/cloud-provisioning`, prod only; dev is shut down indefinitely and out of scope):

- **ArgoCD v3.5.3** (chart `argo-cd-10.9.2`) manages 14 prod Applications from `main` with automated sync, prune and selfHeal. `argocd-notifications-cm` (`k8s/namespaces/argocd/base/values.yaml`) defines three default triggers — `on-sync-failed`, `on-health-degraded` (Degraded ≥ 3m) and `on-sync-status-unknown` — subscribed to a Google Chat webhook whose URL ESO syncs from Secret Manager (`argocd-google-chat-webhook-url`) into `argocd-notifications-secret` through the `google-secret-manager-argocd` ClusterSecretStore (restricted to the `argocd` namespace).
- **Health semantics, verified in the v3.5.3 source:** a Deployment is `Degraded` only on `ProgressDeadlineExceeded`; once a rollout has completed, `AvailableReplicas < UpdatedReplicas` (e.g. Pods crash-looping later) keeps it `Progressing` indefinitely. The built-in CronJob check reports `Degraded` when the last run failed (`lastSuccessfulTime < lastScheduleTime`, nothing active); KEDA `ScaledObject` (`Ready=False` / `Fallback=True`) and `ExternalSecret` (`Ready=False`) have built-in checks. No `progressDeadlineSeconds` is set anywhere, so the 600s default applies.
- **Cluster:** GKE Autopilot on Spot capacity; `media-consumer` scales 0→1 via KEDA. GKE metrics are reduced to `SYSTEM_COMPONENTS` (no kube-state-metrics), so `kubernetes.io/container/*` system metrics are available but `kube_*` series are not.
- **GitHub:** org Apps include `liverty-music-ci-bot` (Contents: write, `cloud-provisioning` only, sole bypass actor of the `main` ruleset, key held in GitHub secrets) and Anthropic's `claude` App. `CLAUDE_CODE_OAUTH_TOKEN` (Claude Max subscription) is a Pulumi-managed org secret already used by `claude.yml` and the reusable review workflow.
- **GCP identity:** one WIF pool with a GitHub OIDC provider restricted to `repository_owner == 'liverty-music'`; the existing `github-actions` SA holds only Artifact Registry Writer.
- Runbooks live in `cloud-provisioning/docs/runbooks/`; Cloud Monitoring alert policies carry triage steps in `documentation.content`.

## Goals / Non-Goals

**Goals:**
- Every ArgoCD-detectable incident starts a Claude investigation within minutes, with no human action.
- The investigation is strictly read-only against GKE and GCP; Claude's only output is text, which a deterministic step posts as an Issue.
- No long-lived PAT, and every credential presented to ArgoCD or the workflow is short-lived (1-hour App installation token, WIF-issued GCP token). The one long-lived secret is the `liverty-music-cluster-bot` private key. It lives only in Secret Manager and the `argocd` namespace, and its App can only start or re-run workflows (D3), never change code.
- Reuse the existing ArgoCD / ESO / WIF / claude-code-action patterns; add no new runtime infrastructure (no relay service).
- Bounded cost and noise: one active investigation per Application, no duplicate Issues, an instant off switch.

**Non-Goals:**
- Any write by Claude to the cluster, GCP or Git (PRs, merges, rollbacks) — next tier.
- Triggering on Cloud Monitoring alerts, or a scheduled health patrol.
- Custom Lua health checks (e.g. CronJob that never succeeded); accepted gap.
- Changing existing triggers' conditions or the Google Chat routing.

## Decisions

### D1: ArgoCD Notifications is the only machine trigger

**Chosen:** extend `argocd-notifications-cm` with one more trigger and a second notifier; nothing else emits triage events.

**Alternatives:** Cloud Monitoring → Pub/Sub / webhook channel. The webhook channel only supports Basic auth or a query-string token and Pub/Sub push only an OIDC token, so neither can call the GitHub API without a relay service — rejected. A scheduled patrol workflow catches more classes but costs a Claude run per interval and is a separate design — deferred.

**Accepted gaps:**
- Application-level failures invisible to Kubernetes health (ERROR logs, JetStream backlog stall, poison messages, goroutine leak, Web Push failures) stay on the existing Cloud Monitoring → human path; so do Pulumi-managed resources.
- **A crash loop whose container passes readiness before each exit** (OOM under load, a panic after minutes, a dropped dependency). Argo CD's `getAppsv1DeploymentHealth` reports Healthy whenever `AvailableReplicas == UpdatedReplicas` at evaluation time, so each restart flips the Application back to Healthy and resets `on-health-progressing-stuck`'s timer: neither Google Chat nor triage hears about it. Observed in the 2026-10-05 end-to-end test (a fixture healthy for 120s per start). A container that exits before readiness on every restart stays Progressing and is caught (the same test, 15 minutes to the trigger). Covered for humans by a `Container Crash Loop` Cloud Monitoring alert: `kubernetes.io/container/restart_count` delta > 3 in 30 minutes, cluster-wide, grouped by namespace and container (baseline zero restarts in every namespace).

### D2: `on-health-progressing-stuck` at 15 minutes

```yaml
trigger.on-health-progressing-stuck: |
  - description: Application health has been Progressing for 15 minutes
    send: [app-health-progressing-stuck]
    when: app.status.health.status == 'Progressing' && now() - date(app.status.health.lastTransitionTime) >= duration("15m")
```

15m is above the 600s default progress deadline (so an in-flight rollout failure turns `Degraded` and is reported by `on-health-degraded` first, not twice), above Spot preemption → reschedule recovery and KEDA 0→1 node provisioning, and still far faster than the 12h notification rate limit of the log alerts. It is added to `defaultTriggers`, so it reaches Google Chat as well. Tune after observing real noise.

**Alternatives:** 10m collides with the progress deadline; 30m (the old dev Degraded value) delays the common CrashLoop case for no benefit in prod.

### D3: `workflow_dispatch` instead of `repository_dispatch`

**Chosen:** `POST /repos/liverty-music/cloud-provisioning/actions/workflows/incident-triage.yml/dispatches` with `{"ref":"main","inputs":{...}}`.

**Why:** `repository_dispatch` requires **Contents: write**; a leaked token could push branches to the repo that is prod's source of truth. `workflow_dispatch` requires only **Actions: write**. The holder cannot write Contents directly. It can start, re-run, cancel or disable *existing* workflows on existing refs, so its reach is whatever those workflows can do behind their own gates. As of this change, the privileged workflows in `cloud-provisioning` are:

| Workflow | Reachable by Actions: write | Gate that still holds |
|---|---|---|
| `bump-prod-pin.yml` (ci-bot credential, pushes `main`) | `workflow_dispatch` | Runs in the `prod-pin` Environment, which needs admin approval |
| `bump-prod-pin.yml` | re-run of a past `repository_dispatch` run | Replays that run's tag: either a no-op (idempotent) or rejected by the fail-closed no-downgrade guard |
| `claude.yml` (Claude App credential) | re-run of a past run; not dispatchable (comment / issue triggers only) | Repeats a request a human already made; cannot reach `main` (ruleset) |
| `ci.yml`, `lint.yml`, `claude-code-review.yml` | re-run only | Read-only checks |

So no path changes prod without an existing human or machine gate. The invariant this relies on is recorded as a rule in the runbook and audited in tasks: **every `cloud-provisioning` workflow that holds a write-capable credential and accepts `workflow_dispatch` must be Environment-gated.** It also lets the workflow live in `cloud-provisioning` next to the runbooks, so no extra repository and no cross-repo read token are needed.

**Alternative rejected:** a dedicated `incident-response` repository as the dispatch target — needed only to contain a Contents-write token, which D3 avoids.

### D4: A dedicated GitHub App `liverty-music-cluster-bot`

**Chosen:** new org App, Repository permissions **Actions: write** (plus mandatory Metadata: read), webhook inactive, installed on `cloud-provisioning` only. Created out-of-band like `ci-bot`; App ID and installation ID are non-secret and live in the generator manifest.

**Actual reach (verified 2026-10-05):** a contents write with a cluster-bot installation token returns `403 Resource not accessible by integration`. Like any GitHub account, the bot can still open issues and comments on **public** repositories, including `cloud-provisioning` (a test created #574); App permissions cannot remove that ("any actor, including a GitHub App using an installation access token, can open an issue in a public repository unless the repository has disabled the 'Issues' feature" — GitHub, community discussion #157656).

**Why not reuse `liverty-music-ci-bot`:** whoever holds an App's private key can mint a token with *all* of that App's permissions, regardless of the scoping requested at mint time. ci-bot can push `cloud-provisioning:main` past the ruleset; putting its key in the cluster would let a cluster compromise rewrite prod manifests. The ci-bot runbook already prescribes a separate App for a different trust boundary. The name follows ci-bot's convention of naming by where the key lives (trust level), not by single use.

### D5: Short-lived token via the ESO `GithubAccessToken` generator

**Chosen:**
- Pulumi stores the App private key as a Secret Manager secret `argocd-cluster-bot-private-key` through the existing `esoOnlySecrets` path (same as `argocd-google-chat-webhook-url`).
- An ExternalSecret in `argocd` syncs it into a Secret `argocd-cluster-bot-private-key`.
- A `GithubAccessToken` generator (`generators.external-secrets.io/v1alpha1`, ESO v2.11.0 ships the CRD) references that Secret, with `repositories: [cloud-provisioning]` and `permissions: {actions: write}`.
- The **existing** `argocd-notifications-secret` ExternalSecret gains a `dataFrom` entry with `sourceRef.generatorRef` to the generator (its `token` key rewritten to `github-token`) next to its current `data` entry, and its `refreshInterval` drops from 1h to 30m. Tokens live 60 minutes, so a refresh always lands before expiry.

**Why one ExternalSecret:** ArgoCD Notifications reads only `argocd-notifications-secret`, and that Secret is already owned (`creationPolicy: Owner`) by an ExternalSecret; a second owner is not possible. Re-reading the Google Chat URL every 30m is a negligible Secret Manager cost.

**Alternatives:** a fine-grained PAT (long-lived, user-owned) — rejected; a CronJob that mints tokens — custom code ESO already provides.

### D6: Webhook notifier and payload

```yaml
service.webhook.incident-triage: |
  url: https://api.github.com
  headers:
  - name: Authorization
    value: Bearer $github-token
  - name: Accept
    value: application/vnd.github+json
template.incident-triage-dispatch: |
  webhook:
    incident-triage:
      method: POST
      path: /repos/liverty-music/cloud-provisioning/actions/workflows/incident-triage.yml/dispatches
      body: |
        {"ref":"main","inputs":{"app":"{{.app.metadata.name}}","trigger":"...","payload":{{ toJson ... }}}}
```

**Wiring (settled in implementation):** each trigger keeps sending **one** template, which now carries both its Google Chat `message` and a `webhook.incident-triage` part; each service reads only its own part. Separate templates do not work: notifications-engine sends every template of a trigger to every subscribed service, so a webhook-only template makes Google Chat post an empty message and a message-only one makes the webhook service send a GET. One template per trigger also carries the trigger name, which the template context does not provide. The subscription recipient is `incident-triage` — `service.webhook.<name>` registers the service under `<name>`, so `webhook:incident-triage` would address a non-existent `webhook` service. Inputs are kept to three strings: `app`, `trigger` and `payload` (a JSON string with health status/message, sync status, operation phase/message, revision, conditions and destination namespace, truncated to 16000 characters), well within the `workflow_dispatch` input limits.

ArgoCD Notifications already deduplicates per trigger condition (it notifies once when a condition becomes true and records that on the Application), so a persistently broken app does not re-dispatch every reconcile.

### D7: Claude runtime — `claude-code-action` in automation mode

**Chosen:** `anthropics/claude-code-action@v1` pinned by SHA (same pin as `claude.yml`), `prompt` set (automation mode), `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`. No new Anthropic credential.

**Fallback not needed:** the pinned action lists `workflow_dispatch` among its automation events. Its agent mode rejects non-human actors, so `allowed_bots: liverty-music-cluster-bot` is required for ArgoCD's dispatches.

### D8: Read-only GCP identity

**Chosen:** a new SA `incident-triage` with exactly two roles, bound to the existing GitHub WIF provider for `attribute.repository/liverty-music/cloud-provisioning`. The workflow authenticates with `google-github-actions/auth` (`id-token: write`).

- `roles/container.viewer` — Kubernetes objects and events (incl. CRDs such as ArgoCD `Application` and KEDA `ScaledObject`). It deliberately contains **no** `container.pods.getLogs`, `container.secrets.get|list` or `container.pods.exec`; every predefined GKE role that has `getLogs` (`developer`, `editor`, `admin`) also grants Secret reads, exec and workload updates.
- `roles/logging.viewer` — container stdout/stderr. Autopilot always ships workload logs to Cloud Logging (the existing `k8s_container` log alerts rely on it), and Cloud Logging is the better source anyway: it keeps the output of every crashed container instance (not only `--previous`), survives Pod deletion and filters by time and severity.

Cloud Monitoring time series are not read in this tier: `gcloud` has no time-series query command, and every trigger in D1 is a Kubernetes-state failure that objects, events and logs explain. `roles/monitoring.viewer` is added when a metrics-driven trigger is.

**Alternative for Pod logs via the Kubernetes API:** bind the built-in `view` ClusterRole (includes `pods/log`, excludes Secrets) to the SA through RBAC. Not needed while Cloud Logging covers logs.

**Why a new SA:** the existing `github-actions` SA is a writer to Artifact Registry; mixing read-everything into a write identity widens both. Any `cloud-provisioning` workflow could impersonate `incident-triage`, which is acceptable because it is read-only; narrowing to the workflow ref would require changing the shared provider's attribute mapping and is not worth it at this tier.

### D9: Tools — `gcloud` / `kubectl` with an allowlist, no GitHub write

**Chosen:** the CLIs the runbooks are already written in.

- `google-github-actions/get-gke-credentials` writes a kubeconfig for `autopilot-cluster-osaka` from the D8 credentials. The prod control plane uses its public endpoint, IAM-gated, with no authorized-networks list, so hosted runners reach it the same way operators do. `gcloud` and `kubectl` are preinstalled on `ubuntu-latest`.
- Subprocess env scrubbing (below) also removes the credential environment variables the auth actions set (`CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE`, `KUBECONFIG`). So `setup-gcloud` registers the credential in gcloud's own config, as `bump-prod-pin.yml` does, and the kubeconfig is copied to `~/.kube/config`.
- Scrubbing requires bubblewrap; without it Claude Code refuses to start. `claude-code-action` installs it only when `allowed_non_write_users` is set, so the job installs `bubblewrap` and `socat` itself (mirroring the action's step) and fails if that fails.
- `Bash` is allowed only for read-only commands: `kubectl get`, `kubectl describe`, `kubectl events`, `gcloud logging read`, `gcloud container clusters describe`, `git log`, `git show`. Claude Code checks each part of a compound command (`&&`, `;`, `|`) against these rules. The rules are prefix matches, so the Skill writes the subcommand first (`kubectl get pods -n x`, not `kubectl -n x get pods`, which "requires approval", i.e. is denied headless).
- Deny rules block flags that redirect where credentials are sent: `kubectl` `--server` / `-s`, `--kubeconfig`, `--token`; `gcloud` `--access-token-file`, `--impersonate-service-account`.
- **The Claude credential is absent from the Bash subprocess environment.** Permission rules match the command text, not expanded values, so an allowlisted command could still print `$CLAUDE_CODE_OAUTH_TOKEN` (e.g. `kubectl get pods -n "$CLAUDE_CODE_OAUTH_TOKEN"`). Denying `env` / `printenv` is therefore not a control. Claude Code's subprocess environment scrubbing removes the Anthropic credentials from Bash subprocesses; the exact setting is confirmed at implementation and proven by test (task 3.4).
- Built-in `Read`, `Glob`, `Grep` are limited to repo paths (manifests, runbooks), excluding the `gha-creds-*.json` and `gha-kubeconfig-*` files the auth steps write. `Write` is limited to `triage-report.md`. **With scrubbing on, Claude Code also enforces the `Read(...)` deny rules as OS-level read denials for every Bash subprocess**, so the deny list must not contain a path an allowed command needs: denying `.git`, `~/.kube` or `~/.config/gcloud` broke `git`, `kubectl` and `gcloud`. Those paths are outside the Read tool's reach anyway (Read is allowed only in the workspace), and `.git` holds no token (`persist-credentials: false`).
- **Claude never holds a GitHub write token. This is enforced by job isolation, not by step ordering:**
  - The `triage` job has `permissions: {contents: read, id-token: write}`, checks out with `persist-credentials: false`, and passes this read-only `GITHUB_TOKEN` as `github_token` explicitly. When `github_token` is omitted, `claude-code-action` exchanges OIDC for a Claude App token with Contents and PR write.
  - The `triage` job uploads `triage-report.md` as an artifact.
  - A separate `report` job (`needs: triage`, `if: always()`, `permissions: {issues: write}`) downloads the artifact and creates or comments on the Issue.
- **Last check before anything leaves the job:** the `report` job refuses to post a report that contains the OAuth token value or a GCP access-token pattern (`ya29.`). It posts a stub saying the report was withheld instead.

The security boundary is D8's read-only identity, plus the absence of long-lived secrets from Claude's reach. If the allowlist is bypassed, the worst outcome is that the WIF-issued GCP access token leaks. That token expires within the job's lifetime (at most 1 hour) and reads Kubernetes objects and logs only: no Secrets, no writes.

**Verified (2026-10-05, with the production settings and a test prompt; runs 37328784276, 37329349428, 37329806391):** `kubectl --server` / `-s` / `--server=` / `--token`, `gcloud --impersonate-service-account` and `env` were denied by rule; Read of `gha-creds-*` / `gha-kubeconfig-*` was denied; `${...}` expansions were refused by Claude Code before execution ("Contains expansion"); the OAuth token never appeared in the session logs. **Residual risk:** a plain `"$CLAUDE_CODE_OAUTH_TOKEN"` expansion was declined by the model in both attempts, so whether a rule or only the model blocks it, and the scrubbing of that variable itself, are not directly confirmed. The report job's credential scan and the token's limited reach remain behind it.

**Alternative rejected:** Google-managed remote MCP servers (GKE, Cloud Logging, Cloud Monitoring) with no `Bash`. They are structurally tighter (no shell, no credential-redirect vector) and add metrics, but cost an extra dependency chain:
- per-project MCP endpoint enablement,
- `roles/mcp.toolUser`,
- an MCP config with bearer-token plumbing,
- unverified acceptance of WIF-issued tokens.

They also make Claude translate the gcloud-based runbooks into MCP tool calls. That is not worth it while the identity is read-only.

### D10: Guardrails

- **Kill switch:** `INCIDENT_TRIAGE_ENABLED` as a `prod` **environment** variable. The Pulumi GitHub token cannot create repository variables (403, as for the bump workflow), and a job-level `if:` cannot read environment variables, so a `gate` job in the `prod` environment reads it and passes it on. Created as `false` with `ignoreChanges`, so flipping it in the UI is not reverted by `pulumi up`. The WIF provider and project come from the environment's existing variables; `INCIDENT_TRIAGE_SA_EMAIL` is added.
- **Concurrency:** `group: incident-triage-${{ inputs.app }}`, `cancel-in-progress: false` — one investigation per Application at a time.
- **Dedup:** Issue title `[incident] <app>: <trigger>`; if an open `incident` Issue for the same `<app>` exists, the report is added as a comment instead of a new Issue. Runs dispatched by anyone other than the cluster-bot are titled `[incident] [manual] <app>: …`, so they never merge with a real incident. The `incident` label is created by the report job (`gh label create --force`): label writes need Issues: write, which the Pulumi GitHub token lacks and the job's `GITHUB_TOKEN` has.
- **Failed runs:** the post names the stage a failed run stopped at (setup before Claude, Claude Code failing to start, Claude not finishing, timeout) and always ends with the ArgoCD status snapshot from `payload`, so the Issue carries the incident even when Claude produced nothing.
- **Budget:** `--max-turns 25` and job `timeout-minutes: 15`.
  - A typical investigation needs about 10–19 turns: Skill/runbook 1–2, Application 1–2, workload/events 2–4 (parallel calls in one turn), Cloud Logging 2–4, recent changes 2–3, report 1–2.
  - Because the cap is tight, D11 has Claude write a draft report early.
  - When the run stops at the cap or the timeout, the `report` job still posts whatever report exists, marked as truncated.
- **Untrusted input:** `inputs.*` reach the prompt only through environment variables and are never interpolated into `run:` scripts. The Skill tells Claude that Application messages, logs, events and commit text are data, never instructions. The real boundary is structural: a read-only identity, allowlisted read-only commands, and no GitHub write.

### D11: Skill `incident-triage`

`.claude/skills/incident-triage/SKILL.md` in `cloud-provisioning` contains:

- **Investigation order:**
  1. ArgoCD state: `kubectl get application`.
  2. Workload objects and events: `kubectl describe` / `kubectl events`.
  3. Container logs: `gcloud logging read` on `k8s_container`.
  4. Recent manifest changes on `main`: `git log` / `git show`.
- **Runbook map:** each Application / namespace points to its runbook in `docs/runbooks/`. Runbooks are referenced, not copied.
- **Report template:** summary, impact, timeline, evidence with the exact commands, suspected cause and confidence, suggested remediation, and what was not checked.
- **Incremental report rule:** write a first `triage-report.md` once the initial evidence is in, and refine it at the end. A capped run still leaves a usable report.
- **Untrusted-input rule.**

### D12: ArgoCD control plane down → Cloud Monitoring

A new alert policy in `src/gcp/components/monitoring.ts` on GKE system metrics for namespace `argocd` (containers `application-controller`, `notifications-controller`): fires when `kubernetes.io/container/uptime` is absent for 10m **or** `kubernetes.io/container/restart_count` increases by more than 3 in 15m. Routed to the existing Slack / Google Chat channels — it must not depend on the component it watches.

### D13: Compute Engine quota for the GKE nodes

Autopilot manages the nodes, but their VMs and boot disks draw on the project's Compute Engine quota: "GKE can only provision infrastructure for your workloads if your project has enough quota for that hardware" (GKE Autopilot overview). Each node boots from a pd-balanced disk (about 100 GB; Autopilot sizes some larger), which counts against the regional `SSD-TOTAL-GB` quota. At the new-project default of 500 GB the four prod nodes (447 GB with a 10 GB PVC) left no room for a fifth, so every node auto-upgrade surge and scale-up failed from 2026-09-27 (550–870 rejected inserts a day; nodes stuck on the previous patch). Raising it exposed the next cap, `CPUS-ALL-REGIONS` (32).

**Chosen:** Cloud Quotas API preferences in Pulumi: `SSD-TOTAL-GB-per-project-region` (asia-northeast2) 1000 GB (about nine nodes including the upgrade surge, approved) and `CPUS-ALL-REGIONS-per-project` 100 (matching the single region's `CPUS` limit). An increase needs a contact email, so the preferences exist only where `gcp.quotaContactEmail` is set in ESC (prod).

## Risks / Trade-offs

- [Notifications controller keeps a stale token after ESO rotation] → Verify in the end-to-end test that a dispatch succeeds more than 60 minutes after the first token was minted; if it caches, add a Reloader annotation to restart the notifications controller on Secret change.
- [`claude-code-action` rejects `workflow_dispatch`] → D7 fallback to `claude -p`.
- [Prompt injection drives a credential-redirecting command (e.g. `kubectl --server https://<attacker>` sending the kubeconfig bearer token)] → deny rules on the redirecting flags (D9). Verified by a test run that the denied forms are rejected. If they are bypassed anyway, the leaked token is read-only and expires within 1 hour.
- [The allowlist is too narrow, so Claude loops on denied commands] → the report states what could not be checked. Widen the allowlist only with read-only subcommands, after reviewing real runs.
- [Shared Claude Max limit exhausted by an incident storm] → concurrency per app, max-turns, kill switch; ArgoCD's once-per-condition dedup limits fan-out.
- [Progressing-stuck noise during long but healthy operations (e.g. Zitadel / NATS StatefulSet rollouts)] → 15m threshold; tune from observed data; the trigger can be removed from a specific Application via annotations if needed.
- [Prompt injection via cluster-controlled text] → read-only identity, allowlisted read-only commands, no GitHub token in Claude's session, report-only output reviewed by a human.
- [Investigation quality is wrong but confident] → Tier 0 is advisory by design; the report must state confidence and what was not checked.
- [cluster-bot key compromise] → The attacker can start, re-run, cancel or disable workflows in `cloud-provisioning`. Mitigations: rotate the key in Secret Manager and revoke it via the App settings, as described in the runbook.
- [Workflow-chaining escalation: Actions: write starts or re-runs a workflow that holds a stronger credential] → Every such path is gated today (D3 table). Task 1.4 audits this, and the runbook rule requires Environment gating for any future privileged `workflow_dispatch`.
- [Claude credential exposed through an expanded variable in an allowed command] → Mitigations:
  - the credential is scrubbed from the Bash subprocess environment (D9), proven by a test;
  - the `report` job scans the report for credential values before posting.

## Migration Plan

1. Create the `liverty-music-cluster-bot` App, install it on `cloud-provisioning`, generate a private key, store it in Pulumi ESC.
2. Pulumi (prod, manual `pulumi up`): Secret Manager secret, `incident-triage` SA + roles + WIF binding, `incident` label, `INCIDENT_TRIAGE_ENABLED=false`, ArgoCD-down alert.
3. Merge the workflow and Skill (inert while the variable is `false`; can be exercised by a manual `workflow_dispatch`).
4. Merge the ArgoCD manifests (generator, ExternalSecrets, notifier, trigger). ArgoCD self-syncs. **Only after step 2 is applied:** when the manifests landed first, the generator failed (no key in Secret Manager), `argocd-notifications-secret` and with it the `argocd` Application turned Degraded, Google Chat reported it, and the webhook retried with an empty token (401) until the secret existed. The dev overlay patches all triage pieces out, so a restarted dev cluster neither fails that sync nor dispatches triage of prod.
5. Flip `INCIDENT_TRIAGE_ENABLED=true`; run the end-to-end test in prod (prod has no users yet and verification there is approved): a throwaway Application in a scratch namespace that crash-loops after becoming Available, confirming Google Chat + dispatch + Issue; then delete it.

**Rollback:** set `INCIDENT_TRIAGE_ENABLED=false` (instant). Full removal: revert the ArgoCD manifest commit (Google Chat routing is untouched by design), then the Pulumi resources.

## Open Questions

- ~~Whether a single template can carry the trigger name~~ — resolved in D6: one template per trigger with both parts.
- `--max-turns 25` and `timeout-minutes: 15` sufficed in every run so far (triage took 2–4 minutes); revisit after real incidents.
