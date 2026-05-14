## ADDED Requirements

### Requirement: Password-Based Storage State Capture Path

The system SHALL provide a headless capture path that produces a Playwright `storageState.json` against the password-based dev Zitadel test user, runnable on a WSL2 + WSLg host without a working display server.

**Rationale**: The existing `capture-auth-state.ts` script requires a headed Chromium window. On WSL2 + WSLg the window opens but stays at `about:blank` past the polling timeout, blocking storage-state regeneration. A headless path that does not depend on a display server unblocks the developer workstation as a viable capture environment. The password user is the only credential type that headless Playwright can drive end-to-end (passkey requires a device-bound gesture).

#### Scenario: Capture script runs to completion on WSL2

- **WHEN** the developer executes the headless capture script (e.g., `npm run auth:capture:password`) on a WSL2 + WSLg host
- **AND** the test user's password is present in `frontend/.auth/password.md` (gitignored)
- **THEN** the script SHALL complete the OIDC login flow against `https://auth.dev.liverty-music.app` without requiring an interactive display
- **AND** SHALL write the resulting storage state to `frontend/.auth/storageState.json`
- **AND** the storage state SHALL contain the access token, refresh token, and user profile for the password-based test user

#### Scenario: Captured storage state authenticates Playwright tests

- **WHEN** `npx playwright test` runs with the storage state produced by the password-capture script
- **THEN** every test SHALL bypass the OIDC redirect and arrive at protected routes authenticated as the password-based test user
- **AND** the backend SHALL accept the captured access token via the existing JWT validator

### Requirement: Existing Passkey Capture Path Retained

The system SHALL retain the existing headed-Chromium passkey capture script (`capture-auth-state.ts`) unchanged. The password capture path SHALL NOT replace it.

**Rationale**: The passkey flow remains the canonical UX path under manual testing on display-capable hosts and exercises device-bound WebAuthn that the password path does not cover. Removing it would lose coverage and force every passkey-related issue to be debugged without a working test entry point.

#### Scenario: Passkey script still runnable on a display-capable host

- **WHEN** a developer on a host with a working display (non-WSL or WSL with x11 forwarding configured) runs the existing passkey capture script
- **THEN** the script SHALL behave exactly as before — open Chromium, drive the OIDC flow against the passkey-only user, write storage state to its existing output path

### Requirement: Test-User Credential File Gitignored

The test user's password SHALL live in a gitignored file under `frontend/.auth/`. It SHALL NOT be committed to the repository under any condition.

**Rationale**: Even a dev-only credential leaking into git history creates secret-scanning noise, sets a bad precedent, and would survive a Zitadel-side rotation in the public history.

#### Scenario: Git status after capture

- **WHEN** the password capture flow is set up on a fresh clone
- **AND** the developer creates `frontend/.auth/password.md` from the Pulumi stack output
- **THEN** `git status` SHALL NOT list `frontend/.auth/password.md` as either tracked or untracked
- **AND** `frontend/.gitignore` SHALL contain a pattern that excludes `.auth/password.md`
