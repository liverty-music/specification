## 1. Frontend cleanup

- [ ] 1.1 `git rm frontend/scripts/capture-auth-state.ts` — delete the dead headed-Chromium passkey capture script
- [ ] 1.2 Revise `frontend/AGENTS.md` "Playwright MCP (Authenticated E2E Testing)" section to a single-user (password) table. Drop all `pepperoni9+playwright-1@gmail.com` references; preserve the password-flow procedure (ESC retrieval + `npm run auth:capture:password`) intact. Remove the WSL2 caveat for the passkey path (no longer relevant).
- [ ] 1.3 Revise `frontend/.auth/README.md` to drop the dual-user / passkey sections (host-suitability table collapses to one row; "Falling back to the passkey flow" section deleted). Keep the password-flow setup procedure, rotation protocol, and gitignore conventions.
- [ ] 1.4 `make lint` passes (biome + stylelint + brand-vocabulary + tsc)

## 2. Spec sync

- [ ] 2.1 The `e2e-auth-testing` spec delta in this change defines a single REMOVED requirement ("Existing Passkey Capture Path Retained") with a clear `Reason:` + `Migration:` block. No additional spec edits are required — the rest of `e2e-auth-testing` (Playwright MCP Authenticated Session, StorageState Capture Script, StorageState Gitignore, Password-Based Storage State Capture Path, Test-User Credential File Gitignored) stays intact and continues to describe the password capture path correctly

## 3. Verification

- [ ] 3.1 After both PRs merge: confirm `frontend/scripts/capture-auth-state.ts` is gone on `main` and `npm run auth:capture:password` still completes end-to-end on WSL2 + WSLg with "Smoke test PASSED"
- [ ] 3.2 `openspec validate remove-passkey-capture-path` passes locally
- [ ] 3.3 `openspec list --json` shows the change with `isComplete=true` after tasks are ticked

## 4. Out of scope (do NOT include in this change)

- [ ] 4.1 Cloud-tenant cleanup of `pepperoni9+playwright-1@gmail.com` — Cloud tenant retention is governed by `self-hosted-zitadel §15.1` / `§18.10` (retained indefinitely as no-cost rollback escape hatch). User is inert (no DNS, no OIDC traffic). Folded into a future Cloud-decommission change if and when one is opened. This task exists in tasks.md only as an explicit "do not do here" marker for the implementer

## 5. Archive prep

- [ ] 5.1 `openspec validate remove-passkey-capture-path` passes
- [ ] 5.2 `openspec status --change remove-passkey-capture-path --json` reports `isComplete=true`
- [ ] 5.3 `/opsx:archive remove-passkey-capture-path`
