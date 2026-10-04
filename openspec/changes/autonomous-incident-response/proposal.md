## Why

When something breaks in prod today, a human has to notice a Google Chat / Slack message, fetch cluster credentials, and work through `gcloud` / `kubectl` and the runbooks before anyone knows what is wrong. Many failure modes are not covered by a Cloud Monitoring alert at all (ArgoCD sync failures, workloads that stop becoming available, KEDA scaler errors, failing CronJobs), and the one ArgoCD trigger that catches workload trouble (`on-health-degraded`) is structurally blind to the most common one: a Deployment whose Pods start crash-looping *after* a rollout completed stays `Progressing` forever and never turns `Degraded` (Argo CD v3.5.3 `getAppsv1DeploymentHealth`).

The long-term goal is for Claude to respond to incidents on its own — investigate, open a fix PR, merge it, and confirm recovery. That end state needs trust in the quality of Claude's investigations first, so this change delivers the foundation and the first autonomy tier only: **every detected incident is automatically investigated by Claude, read-only, and reported as a GitHub Issue** before a human has to open a terminal. Later tiers (PRs, gated auto-merge, recovery verification) build on the same trigger, identity and runbook plumbing introduced here.

## What Changes

- **Detection** — ArgoCD Notifications stays the single machine trigger:
  - Add `on-health-progressing-stuck`: fires when an Application's health has been `Progressing` for ≥ 15 minutes (covers post-rollout CrashLoop; 15m sits above the 10m default `progressDeadlineSeconds`, Autopilot Spot preemption recovery and KEDA 0→1 scale-up).
  - The existing `on-sync-failed`, `on-health-degraded` and `on-sync-status-unknown` triggers, plus the new one, notify both Google Chat (unchanged) and the new Claude triage webhook.
  - Add a Cloud Monitoring alert policy for the ArgoCD control plane itself being down — the one failure ArgoCD cannot report — routed to the existing human channels.
- **Trigger** — a new ArgoCD Notifications webhook service calls the GitHub `workflow_dispatch` API on `cloud-provisioning`'s new `incident-triage.yml`, passing the Application name, trigger, health / sync status and messages as workflow inputs.
- **GitHub identity** — a new dedicated GitHub App `liverty-music-cluster-bot` (Repository permission **Actions: write** only, installed on `cloud-provisioning` only). Its private key lives in Secret Manager; the External Secrets Operator `GithubAccessToken` generator mints a 1-hour installation token into `argocd-notifications-secret`, refreshed every 30 minutes. No long-lived PAT, and the cluster-resident credential cannot push code.
- **Triage workflow** — `incident-triage.yml` (on `workflow_dispatch`) runs `anthropics/claude-code-action` authenticated with the existing org secret `CLAUDE_CODE_OAUTH_TOKEN`. It authenticates to GCP via Workload Identity Federation as a **new read-only service account**, investigates with allowlisted read-only `kubectl` and `gcloud logging` commands (the same CLIs the runbooks use) guided by an `incident-triage` Skill built on `docs/runbooks/`, and writes its diagnosis (summary, evidence, suspected cause, suggested remediation) to a GitHub Issue labelled `incident`.
- **Guardrails** — one triage per Application at a time (workflow `concurrency`), an existing open `incident` Issue for the same Application is commented on instead of duplicated, bounded `--max-turns` and job timeout, a repository-variable kill switch, and telemetry content treated as untrusted data in the prompt.

Out of scope (next tiers / follow-ups): Claude opening PRs, auto-merge and recovery verification; Cloud Monitoring alerts as Claude triggers; scheduled health patrol; Kyverno / Argo Rollouts guardrails; custom CronJob health checks; the dev environment (shut down indefinitely).

## Capabilities

### New Capabilities
<!-- none — operations tooling outside the product spec tree; .openspec.yaml sets skip_specs: true -->

### Modified Capabilities
(none — no product behavior changes; see design.md)

## Impact

- **`liverty-music/cloud-provisioning`**
  - `k8s/namespaces/argocd/base/values.yaml` — new webhook notifier, template, `on-health-progressing-stuck` trigger, subscription to the webhook.
  - `k8s/namespaces/argocd/base/` — `GithubAccessToken` generator and an ExternalSecret for the minted token; the App private key ExternalSecret.
  - `src/gcp/` — Secret Manager secret for the App private key; new read-only triage service account (`container.viewer`, `logging.viewer`) + WIF binding scoped to `liverty-music/cloud-provisioning`; ArgoCD-control-plane-down alert policy.
  - `src/github/` — `incident` label; kill-switch repository variable.
  - `.github/workflows/incident-triage.yml` and `.claude/skills/incident-triage/` — new.
  - `docs/runbooks/` — runbook for the App, token flow, kill switch and how to read a triage Issue.
- **GitHub settings** — new GitHub App `liverty-music-cluster-bot` (created out-of-band, like `liverty-music-ci-bot`).
- **Unaffected** — application workloads and their manifests, the prod release path (`bump-prod-pin`), branch protection / rulesets, backend / frontend / specification code. The triage service account is read-only, so Claude cannot change cluster or GCP state.
- **Cost / limits** — triage runs share the Claude Max subscription limit with interactive use, `@claude` and code review; bounded by concurrency and `--max-turns`. Prod `pulumi up` is a manual step, as for every Pulumi change.
- **Notification volume** — one additional ArgoCD trigger reaching Google Chat.
