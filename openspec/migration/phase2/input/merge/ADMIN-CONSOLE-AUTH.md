<!-- merge_group: ADMIN-CONSOLE-AUTH | target: stories/sign-in-to-admin-console | members: 3 -->

<!-- member: admin-console | flags:  -->
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

<!-- member: admin-console | flags:  -->
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

<!-- member: admin-console | flags:  -->
### Requirement: Post-login welcome placeholder

After successful authentication the admin console SHALL display a welcome
placeholder page and SHALL NOT expose any business feature. The placeholder
exists only to confirm the authenticated foundation is in place.

#### Scenario: Welcome page after login

- **WHEN** an authenticated developer lands on the admin console root
- **THEN** a welcome placeholder is shown with no admin business functionality

