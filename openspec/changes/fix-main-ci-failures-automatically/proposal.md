## Why

A failure on `main` that no pull request caused (a flaky test, a test that breaks on a date, a slow package mirror) went unnoticed for two weeks: frontend's nightly CI failed five times from 2026-11-05 to 2026-11-20, and each failure only added a comment to the Issue "CI failing on main" (frontend#929), which had no assignee and reached no one. Detection works; delivery, triage and the fix do not. The owner wants the failure in Slack and Claude to analyze it and open the fix PR on its own.

## What Changes

- **Issue lifecycle** — the nightly CI report moves to a reusable workflow in `liverty-music/.github`, called by frontend and backend:
  - a failed nightly opens the Issue "CI failing on main" (or comments on the open one);
  - a green nightly closes the open Issue, so each new outbreak opens a new Issue (the event that starts Claude);
  - when the green nightly ran on the same commit as a failed one, the Issue gets the label `flaky` before it closes.
- **Cron off minute 0** — both nightly schedules move from `0 19 * * *` to `17 19 * * *`. GitHub warns that runs at the start of the hour are delayed or dropped; frontend's 04:00 JST run started 2 to 7 hours late in the last 30 runs.
- **Claude routine** — a Claude Code routine (scheduled task on claude.ai) fires on the GitHub event "issue opened" in frontend and backend, and acts only on Issues the CI workflow itself opened (the repositories are public). It reads the failed run's logs, classifies the cause (flaky test, real bug, infrastructure), and for a cause it can fix pushes a `claude/` branch and opens a normal (not draft) pull request that names the Issue. It posts the cause, the Issue link and the PR link to Slack through the Slack connector. The owner reviews and merges through the normal PR flow.
- **Instructions in the repository** — the routine's instructions live in `liverty-music/.github` as a versioned file; the routine's own prompt only points at it.
- **Fallback** — the routine is a research preview and its settings live only in claude.ai. If the trial shows a problem (the Issue event does not fire, limits, quality), the same instructions move to a GitHub Actions job with `anthropics/claude-code-action`, the pattern `incident-triage.yml` already runs in cloud-provisioning.

## Capabilities

### New Capabilities
<!-- none: CI and operations tooling outside the product spec tree; .openspec.yaml sets skip_specs: true -->

### Modified Capabilities
(none: no product behavior changes)

## Impact

- **`liverty-music/.github`** — new reusable workflow `report-main-ci.yml`; new routine instructions `routines/fix-main-ci.md`.
- **`liverty-music/frontend`**, **`liverty-music/backend`** — `ci.yaml` / `ci.yml`: the `report-main-failure` job is replaced by a call to the reusable workflow that runs on every scheduled run (pass or fail); cron moved to minute 17.
- **`liverty-music/cloud-provisioning`** — Pulumi: the Claude GitHub App's installation covers frontend, backend and `.github` (`github.AppInstallationRepository`); runbook `docs/runbooks/main-ci-auto-fix.md` (how the routine and the Slack connector are set up, paused and recreated). The routine and the Slack connector have no API Pulumi can call (design D5).
- **claude.ai** (by hand) — one routine with GitHub triggers on frontend and backend, the Slack connector.
- **Cost / limits** — routine runs count against the owner's Claude subscription and the routine hourly limits; at most one run per outbreak (a failure while the Issue is still open only adds a comment, which starts no run).
- **Unaffected** — branch protection and rulesets, the release path, the pull request CI, product code.
