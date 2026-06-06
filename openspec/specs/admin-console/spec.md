## Purpose

The developer admin console frontend foundation: a dedicated Vite MPA entry in the `frontend` repo, bundle-isolated from the consumer SPA, authenticated via Zitadel OIDC (admin org + Google Workspace IDP), with an authenticated route guard and a post-login welcome placeholder. Business features land in later changes; this establishes the access-controlled shell.

## Requirements

### Requirement: Bundle isolation from the consumer SPA

The admin console SHALL be built as a separate Vite/Rollup entry point in the
`frontend` repository such that no admin-only code is included in any chunk
loaded by the consumer SPA. Adding the admin console MUST NOT increase the
consumer SPA's downloaded bundle size or regress its Core Web Vitals.

#### Scenario: Consumer page loads no admin code

- **WHEN** a fan loads the consumer SPA at the consumer hostname
- **THEN** the network requests for the consumer entry's chunk graph contain no
  module originating from the admin source directory

#### Scenario: Consumer bundle size unchanged

- **WHEN** the production build runs with the admin entry present
- **THEN** the consumer entry's emitted chunk set is byte-for-byte equivalent to a
  build without the admin entry (excluding shared chunks the consumer already
  loads)

### Requirement: Authentication via the admin org with Google Workspace IDP

The admin console SHALL authenticate users through Zitadel OIDC (PKCE, no client
secret) scoped to the `admin` role org, so that the admin org's Google Workspace
IDP login policy applies. Only accounts that can complete the Google Workspace
sign-in SHALL gain access; authentication itself is the access boundary.

#### Scenario: Internal developer signs in

- **WHEN** an internal user with a Google Workspace account initiates sign-in on
  the admin console
- **THEN** they are redirected through the admin org's Google IDP and, on success,
  returned authenticated to the admin console

#### Scenario: Non-Workspace account cannot enter

- **WHEN** a user without an eligible Google Workspace account attempts to sign in
- **THEN** they cannot complete authentication and are not granted access to the
  admin console

#### Scenario: Org scope drives the login policy

- **WHEN** the admin console starts its OIDC sign-in flow
- **THEN** the request carries the admin org id in the
  `urn:zitadel:iam:org:id:<id>` scope so Zitadel applies the admin org login
  policy rather than the consumer product-org policy

### Requirement: Authenticated route guard

Every admin console route SHALL require authentication by default. An
unauthenticated visitor MUST be redirected into the sign-in flow before any
admin content renders. The OIDC callback route is the only exception.

#### Scenario: Unauthenticated access is redirected

- **WHEN** an unauthenticated visitor navigates to any admin console route other
  than the auth callback
- **THEN** they are redirected into the Zitadel sign-in flow and no admin content
  is shown

#### Scenario: Callback completes the session

- **WHEN** Zitadel redirects back to the admin console's `/auth/callback`
- **THEN** the console completes the OIDC code exchange and establishes the
  authenticated session

### Requirement: Post-login welcome placeholder

After successful authentication the admin console SHALL display a welcome
placeholder page and SHALL NOT expose any business feature. The placeholder
exists only to confirm the authenticated foundation is in place.

#### Scenario: Welcome page after login

- **WHEN** an authenticated developer lands on the admin console root
- **THEN** a welcome placeholder is shown with no admin business functionality

### Requirement: Dedicated source directory with an enforced import boundary

Admin console source SHALL live in a dedicated top-level `admin/` directory in
the `frontend` repository, separate from the consumer `src/` directory.
Cross-app code SHALL be consumed only from a shared location. An automated lint
check SHALL fail the build if consumer (`src/`) code imports admin (`admin/`)
code or vice versa, except through the shared location.

#### Scenario: Cross-import fails lint

- **WHEN** a module under `src/` imports a module under `admin/` (or the reverse)
  directly rather than through the shared location
- **THEN** the lint/CI check fails

#### Scenario: Shared code is importable by both

- **WHEN** both the consumer and admin entries import a module from the shared
  location
- **THEN** the import is permitted and the module is emitted as a shared chunk
