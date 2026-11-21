## 1. Routine trigger trial (claude.ai, liverty-music/frontend)

- [ ] 1.1 Check which repositories the Claude GitHub App's installation covers (organization settings → GitHub Apps → claude). frontend is needed for 1.2; if it is missing, add it by hand for the trial (task 5.1 brings the selection under Pulumi)
- [ ] 1.2 Create a trial routine with the GitHub trigger "Issue opened" on liverty-music/frontend and the prompt "Post the Issue title and author to Slack"; open an Issue from a `workflow_dispatch` run of a throwaway workflow on a `trial/` branch using `GITHUB_TOKEN`, and verify the routine run starts and the Slack message arrives. Delete the trial workflow branch, the Issue and the routine afterwards. If the run does not start, stop and replan with design D4

## 2. Issue lifecycle and routine instructions (liverty-music/.github)

- [ ] 2.1 Add `.github/workflows/report-main-ci.yml` (design D1): open, comment, close with `flaky`, label creation, trusting only Issues and comments by `github-actions[bot]`; verify with a `workflow_dispatch` test caller on a branch, using a scratch Issue title, that each of the four table rows produces the expected Issue state and that an Issue with the same title opened by the owner is ignored
- [ ] 2.2 Add `routines/fix-main-ci.md` with the steps of design D3, and verify a dry run: in a local Claude Code session on frontend, ask it to follow the file for frontend#929's run 42738483384 without pushing, and check it classifies the E2E timeout and names the cause

## 3. Callers (liverty-music/frontend)

- [ ] 3.1 Replace `report-main-failure` in `.github/workflows/ci.yaml` with a call to `report-main-ci.yml` (`if: always() && github.event_name == 'schedule'`, input `needs.ci-success.result`) and move the cron to `17 19 * * *`; verify after merge that the next nightly starts after 19:17 UTC and, when green, leaves no open "CI failing on main" Issue

## 4. Callers (liverty-music/backend)

- [ ] 4.1 Same as 3.1 for `.github/workflows/ci.yml`; verify the same on backend's next nightly

## 5. Routine, App selection and runbook (liverty-music/cloud-provisioning, claude.ai)

- [ ] 5.1 Add `github.AppInstallationRepository` resources for the Claude App on frontend, backend and `.github` in `src/github/` (installation id from ESC config); verify `pulumi preview` for prod shows only these creates (or imports for repositories already selected), and that after the owner's `pulumi up` the installation lists the three repositories. If the installation API refuses the Pulumi token, record the error in design D5 and keep the selection by hand
- [ ] 5.2 Connect the Slack connector on claude.ai and create the routine of design D3 (triggers on frontend and backend, repositories, one-line prompt, Slack connector) by hand; write `docs/runbooks/main-ci-auto-fix.md` with its exact settings, how to pause it, and the D4 fallback
- [ ] 5.3 Verify end to end on frontend with a test caller on a `trial/` branch whose CI step fails on purpose and which calls `report-main-ci.yml`: check that the bot opens "CI failing on main", a routine run starts, posts to Slack with the cause and Issue link, and comments on the Issue why it opens no pull request (the failure is outside `main`). Also open an Issue with the same title as the owner and check that its run ends without a comment or Slack message. Close the Issues and delete the branch afterwards
