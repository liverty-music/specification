# E2E Auth Testing

## Purpose

Configuration and workflow for running authenticated E2E tests using Playwright MCP against the enforced authentication layer. Enables automated browser testing of protected routes and authenticated API calls.

## Requirements

## ADDED Requirements

### Requirement: Playwright MCP Authenticated Session

The system SHALL support launching Playwright MCP with a pre-captured authenticated browser session via `storageState`.

**Rationale**: With authentication enforced on both frontend routes and backend APIs, E2E tests must run as an authenticated user. The `storageState` approach avoids replaying the login flow on every test run.

#### Scenario: MCP starts with storageState

- **WHEN** Playwright MCP is launched with `--isolated --storage-state=.auth/storageState.json`
- **THEN** the browser context SHALL contain the authenticated user's cookies and localStorage
- **AND** the `oidc-client-ts` UserManager SHALL recognize the user as authenticated
- **AND** API calls SHALL include a valid `Authorization: Bearer` header

#### Scenario: MCP navigates to protected route

- **WHEN** Playwright MCP navigates to a protected route (e.g., `/dashboard`)
- **AND** the storageState contains a valid authenticated session
- **THEN** the route SHALL load without being redirected to the landing page

### Requirement: StorageState Capture Script

The system SHALL provide a setup script that captures an authenticated session's storageState for Playwright MCP use.

**Rationale**: The storageState file must be generated from a real OIDC login flow. A reusable script ensures consistent generation and simplifies CI integration.

#### Scenario: Capture storageState from test user login

- **WHEN** the setup script is executed
- **THEN** the script SHALL open a browser and navigate to the application
- **AND** perform the OIDC login flow with a configured test user
- **AND** save the resulting browser state to `.auth/storageState.json`
- **AND** the saved state SHALL include the access token, refresh token, and user profile

### Requirement: StorageState Gitignore

The storageState file SHALL NOT be committed to version control.

**Rationale**: The file contains authentication tokens and user session data that are sensitive and environment-specific.

#### Scenario: Git status after storageState generation

- **WHEN** `.auth/storageState.json` is generated
- **THEN** the file SHALL be excluded from git tracking via `.gitignore`