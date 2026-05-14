## Why

The just-archived `playwright-password-test-user` change ([archive/2026-05-14-playwright-password-test-user/](../archive/2026-05-14-playwright-password-test-user/)) shipped an `Existing Passkey Capture Path Retained` requirement on the `e2e-auth-testing` capability — the spec mandates that `frontend/scripts/capture-auth-state.ts` remain unchanged so a developer on a display-capable host can drive the headed OIDC flow with the existing passkey test user.

That requirement is **operationally vacuous on the active self-hosted dev Zitadel**: the passkey user the scenario implicitly references — `pepperoni9+playwright-1@gmail.com` — is a Zitadel-Cloud-era Self-Registration user that was wiped by `self-hosted-zitadel §10`'s `truncate_users_for_zitadel_migration` Atlas migration and was never re-provisioned on self-hosted. The script is now dead code: it loads Chromium, redirects to `/loginname`, fills the email, and Zitadel returns `user not found`.

Three concrete harms follow from leaving it as-is:

1. **Misleading docs**: `frontend/AGENTS.md` (the canonical agent-facing entry point) and `frontend/.auth/README.md` both name `pepperoni9+playwright-1@gmail.com` as the passkey path's test user. A new developer or agent following the docs will sink 5–10 minutes diagnosing "user not found" before realising the documented user doesn't exist on the active issuer.
2. **Spec drift**: `e2e-auth-testing` requires the script's retention, but no scenario in any capability requires Zitadel to host the user the script targets. The requirement and the surrounding reality have diverged; the spec is no longer a credible source of truth on this capability.
3. **Dead code**: `scripts/capture-auth-state.ts` plus the `npx tsx scripts/capture-auth-state.ts` invocation it implies clutters the repo without any path to working. Its existence prolongs the "maybe someone is using this?" ambiguity that retiring it removes.

The Cloud tenant where the user was originally provisioned is retained indefinitely per `self-hosted-zitadel §15.1` / `§18.10` as a no-cost rollback escape hatch — but DNS does not point at Cloud, no OIDC traffic reaches it, and rollback is no longer a planned action. The user on the Cloud tenant is inert.

## What Changes

- **Remove** the `Existing Passkey Capture Path Retained` requirement from `e2e-auth-testing/spec.md` (REMOVED with a clear `Migration:` line pointing operators at the password capture path).
- **Delete** `frontend/scripts/capture-auth-state.ts`.
- **Revise** `frontend/AGENTS.md` "Playwright MCP (Authenticated E2E Testing)" section to a single-user, password-only table. Drop all `pepperoni9+playwright-1@gmail.com` references; keep the password-flow procedure intact.
- **Revise** `frontend/.auth/README.md` to drop the dual-user / passkey columns and sections. Keep the password-flow procedure, rotation protocol, and gitignore conventions.
- **Leave the Cloud tenant user untouched.** It is inert (no DNS, no OIDC traffic) and the Cloud tenant retention is a separate operational decision (`self-hosted-zitadel §15.1`). If a future change consolidates the Cloud-tenant decommission, it can clean up the user as part of that scope.

## Capabilities

### Modified Capabilities

- `e2e-auth-testing`: one requirement REMOVED (`Existing Passkey Capture Path Retained`). No requirements added or otherwise modified. The capability narrows to password-only on its remaining requirements (Password-Based Storage State Capture Path, Test-User Credential File Gitignored).

### New Capabilities

None.

### Removed Capabilities

None at the capability level — only one requirement within `e2e-auth-testing` is removed.

## Impact

**Affected repositories**

- `specification/openspec/specs/e2e-auth-testing/spec.md`: one requirement folded out via archive's delta-sync.
- `frontend/scripts/capture-auth-state.ts`: deleted (~90 lines).
- `frontend/AGENTS.md`: "Playwright MCP" section trimmed (~10 lines net).
- `frontend/.auth/README.md`: dual-user matrix collapsed to single-user procedure (~30 lines net).

**Affected systems**

- None at runtime. Dev Zitadel state unchanged. The Cloud tenant user remains in place (inert).

**Reversibility**

- Single revert of both PR merges restores the script and docs. The `e2e-auth-testing` requirement can be re-added in a follow-up change if a future need surfaces (e.g., CI WebAuthn regression testing via virtual authenticator — a separate design problem, not a fork of the current script's lineage).

**Dependencies**

- Requires `playwright-password-test-user` archived (it is — `archive/2026-05-14-playwright-password-test-user/`).
- Does not interact with `archive-zitadel-cloud-tenant` (descoped per `self-hosted-zitadel §18.10` — tenant retained indefinitely).

**Out of scope**

- Cloud-tenant cleanup of `pepperoni9+playwright-1@gmail.com` (would belong in a future Cloud-decommission change, not here).
- Virtual-authenticator approach to passkey regression testing (separate design problem; out of scope until / unless the need surfaces).
- Retiring any other dev-only test fixture or seed user.
