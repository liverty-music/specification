## Why

Two `self-hosted-zitadel` follow-ups were deferred at archive time (2026-05-11) and remain blocking E2E coverage of the new issuer:

1. **§18.5** — the dev Zitadel instance currently has only a passkey-only test user. Passkey credentials require a biometric/PIN gesture from the device and are incompatible with headless test automation (Playwright, CI runners).
2. **§14** — Playwright's existing `.auth/` storage state was captured against Zitadel Cloud's issuer. After the cutover to `https://auth.dev.liverty-music.app`, the storage state is stale. The headed-Chromium capture script `capture-auth-state.ts` cannot regenerate it on WSL2 + WSLg (the Chromium window stays at `about:blank` past the 5-minute polling timeout) and even on a working display the passkey-only user cannot authenticate headlessly.

Without this change:

- E2E (`npx playwright test`) cannot run against the new issuer — every PR ships without integration coverage of the OIDC callback, hydration, and the `pre-access-token` webhook integration.
- Any issuer-bound regression (token validation, OIDC discovery, JWT claim handling) reaches main undetected.
- The team falls back to manual smoke testing for auth-touching changes, which is slower and less consistent.

The two items belong in a single change because §14 strictly depends on §18.5 — there is no way to regenerate `.auth/` against the new issuer until the password-based user exists. Splitting them would create an artificial sequencing barrier with no benefit.

GitHub issue [liverty-music/frontend#345](https://github.com/liverty-music/frontend/issues/345) is the existing operational tracking surface and remains in place; this OpenSpec change captures the spec-level decisions (test-user requirement, capture-path convention) that should outlive the issue.

## What Changes

- **Pulumi SHALL provision a password-only `zitadel.HumanUser`** in the dev self-hosted Zitadel instance for E2E use, distinct from the existing passkey user. The initial password is stored in GSM and surfaced to `.auth/` via the existing gitignored credential-file convention.
- **The existing passkey-only test user is retained** for device-bound manual testing. The two users coexist; the password user is the default for automation, the passkey user remains the canonical UX path.
- **`frontend/.auth/README.md` SHALL document the new test user**, the credential-file location (gitignored), and the WSL2-friendly capture path — likely Playwright MCP in headless mode, replacing `capture-auth-state.ts` for the password flow. `capture-auth-state.ts` is retained for the passkey flow on hosts where it works.
- **A fresh `.auth/` storage state SHALL be captured** against the password user and the new issuer, then committed (storage-state shape is public; credentials remain gitignored per current convention).
- **All existing E2E tests SHALL pass via the new storage state by default**. No test-level rewrites are expected; the storage-state swap is sufficient.

## Capabilities

### Modified Capabilities

- `identity-management`: Add a requirement specifying that the dev self-hosted Zitadel instance SHALL provision a password-based E2E test user in addition to any passkey users, so that headless test automation has a viable credential path. The requirement is dev-scoped — staging/prod test-user provisioning is intentionally out of scope.

### New Capabilities

None.

### Removed Capabilities

None.

## Impact

**Affected repositories**

- `cloud-provisioning/src/zitadel/...` — new `zitadel.HumanUser` Pulumi resource (with `InitialPassword`); possibly a new dedicated component if test-user provisioning warrants its own file.
- `cloud-provisioning/` GSM — new secret holding the test user's initial password, surfaced into `.auth/` via the existing ExternalSecret pattern or one-shot copy.
- `frontend/.auth/README.md` — credential-file reference + WSL2-friendly capture path documentation.
- `frontend/.auth/<user>.json` — regenerated storage state.
- `frontend/scripts/` — new headless capture script (or extension of an existing one) using Playwright MCP. The existing `capture-auth-state.ts` is kept for the passkey path.

**Affected systems**

- Dev self-hosted Zitadel instance — gains one HumanUser. No projects, OIDC apps, or policies are modified.
- Frontend E2E pipeline — unblocked. Before this change: missing/stale `.auth/` storage state blocks every test run. After: tests run against the new issuer with the password user's storage state.

**Reversibility**

- Single Pulumi revert removes the test user from Zitadel and the password from GSM. The `.auth/` storage state is replaced by reverting the frontend commit. No state migration involved.

**Dependencies**

- Requires `self-hosted-zitadel` archived (it is — `archive/2026-05-11-self-hosted-zitadel/`).
- Coordinates with — but does not require — `rename-zitadel-machine-keys` (archived 2026-05-13) for naming consistency around Zitadel-managed credentials.

**Out of scope**

- Replacing or removing the existing passkey user — passkey remains the canonical UX path for manual testing.
- CI integration of Playwright MCP (e.g., GitHub Actions workflow updates) — this change ships the local capture workflow first; CI automation is a future follow-up if/when it becomes blocking.
- Staging / prod Zitadel instances — those use their own test-user strategy.
- Migrating away from `capture-auth-state.ts` for the passkey flow.
