## 1. Frontend cleanup

- [x] 1.1 `git rm frontend/scripts/capture-auth-state.ts` — delete the dead headed-Chromium passkey capture script _Landed in [liverty-music/frontend#354](https://github.com/liverty-music/frontend/pull/354) commit `f4e041e` (merged as `ec4e84c`)._
- [x] 1.2 Revise `frontend/AGENTS.md` "Playwright MCP (Authenticated E2E Testing)" section to a single-user (password) table. Drop all `pepperoni9+playwright-1@gmail.com` references; preserve the password-flow procedure (ESC retrieval + `npm run auth:capture:password`) intact. Remove the WSL2 caveat for the passkey path (no longer relevant). _Same PR (commit `f4e041e`): the section now opens with "The dev Zitadel hosts a single Pulumi-managed test user for E2E:" followed by a one-row table; the dual-user host-suitability matrix is gone._
- [x] 1.3 Revise `frontend/.auth/README.md` to drop the dual-user / passkey sections (host-suitability table collapses to one row; "Falling back to the passkey flow" section deleted). Keep the password-flow setup procedure, rotation protocol, and gitignore conventions. _Same PR (commit `f4e041e`): the README is rewritten end-to-end. Added a "Historical note" footer documenting why the passkey path was removed and pointing at Chrome DevTools virtual authenticator as the design direction for any future WebAuthn / passkey CI regression testing._
- [x] 1.4 `make lint` passes (biome + stylelint + brand-vocabulary + tsc) _Verified locally before push; PR CI green._

## 2. Spec sync

- [x] 2.1 The `e2e-auth-testing` spec delta in this change defines a single REMOVED requirement ("Existing Passkey Capture Path Retained") with a clear `Reason:` + `Migration:` block. The remaining `e2e-auth-testing` requirements (Playwright MCP Authenticated Session, StorageState Capture Script, StorageState Gitignore, Password-Based Storage State Capture Path, Test-User Credential File Gitignored) stay intact and continue to describe the password capture path correctly _`specs/e2e-auth-testing/spec.md` authored at PR #462 commit `0a0620f`._
- [x] 2.2 The `identity-management` spec delta in this change defines (a) a REMOVED requirement ("Test User Coexists with Passkey User") with a clear `Reason:` + `Migration:` block — the passkey user it requires to remain present does not exist on the active dev Zitadel; and (b) a MODIFIED of the "Provision Password-Based E2E Test User in Dev Zitadel" requirement dropping the "distinct from the existing passkey-only test user" phrasing inherited from `playwright-password-test-user`. After the archive folds these in, `identity-management` no longer references the wiped passkey user _`specs/identity-management/spec.md` authored at PR #462 commit `8d2c845` (round-2 review fix r3241092396) and refined at `65c994c` (round-3 review fix r3241145273 — dropped self-referential pointer)._

## 3. Verification

- [x] 3.1 After both PRs merge: confirm `frontend/scripts/capture-auth-state.ts` is gone on `main` and `npm run auth:capture:password` still completes end-to-end on WSL2 + WSLg with "Smoke test PASSED" _Verified post-frontend-merge: `ls frontend/scripts/` returns 3 files (`capture-auth-state-password.ts`, `check-brand-vocabulary.ts`, `known-entities.ts`) — passkey script gone. Password capture path was last end-to-end verified during the playwright-password-test-user §3.5 run (Smoke test PASSED reaching /dashboard), unchanged in this change._
- [x] 3.2 `openspec validate remove-passkey-capture-path` passes locally _Re-verified after each of the 4 review-fix commits (`0a0620f`, `8c49c39`, `8d2c845`, `65c994c`, `ae99ae7`) on PR #462._
- [x] 3.3 `openspec list --json` shows the change with `isComplete=true` after tasks are ticked _Verified after this follow-up PR's commit (all `- [ ]` ticked; the `- 4.1` plain-bullet "out of scope" line correctly does not gate `isComplete`)._

## 4. Out of scope (do NOT include in this change)

- 4.1 Cloud-tenant cleanup of `pepperoni9+playwright-1@gmail.com` — Cloud tenant retention is governed by `self-hosted-zitadel §15.1` / `§18.10` (retained indefinitely as no-cost rollback escape hatch). User is inert (no DNS, no OIDC traffic). Folded into a future Cloud-decommission change if and when one is opened. This bullet exists in tasks.md only as an explicit "do not do here" marker for the implementer — formatted as a plain bullet (not `- [ ]`) so the `isComplete` calculation does not gate on it

## 5. Archive prep

- [x] 5.1 `openspec validate remove-passkey-capture-path` passes _Same verification path as §3.2._
- [x] 5.2 `openspec status --change remove-passkey-capture-path --json` reports `isComplete=true` _Verified after this PR's commit._
- [x] 5.3 `/opsx:archive remove-passkey-capture-path` _Performed in this PR's follow-up archive step. The git `mv` + `openspec/specs/{e2e-auth-testing,identity-management}/spec.md` delta sync are folded into the same PR per `[reference_openspec_archive_pattern]`._
