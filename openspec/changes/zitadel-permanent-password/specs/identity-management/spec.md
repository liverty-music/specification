## ADDED Requirements

### Requirement: E2E Test User Password Marked Permanent at Provision Time

The dev self-hosted Zitadel instance SHALL mark the password-based E2E test user's password as permanent (`noChangeRequired = true`) at Pulumi-apply time, via a dedicated Dynamic Resource that calls the Zitadel Management API `POST /management/v1/users/{user_id}/password` immediately after the `zitadel.HumanUser` is created. The dev `e2e-test-password` user SHALL NOT be redirected to `/ui/v2/login/password/change` on its first sign-in or on any subsequent sign-in.

**Rationale**: `@pulumiverse/zitadel.HumanUser` v0.2.0 sets the user's credential state with `changeRequired = true` and exposes no knob to flip this flag at create time. Without an explicit `SetPassword(noChangeRequired = true)` call, Zitadel redirects the user to a password-change page on first sign-in and refuses to issue tokens until the password is changed. Headless E2E automation cannot tolerate this gate without a fragile script-side workaround that depends on Zitadel's default password-history policy remaining unchanged.

#### Scenario: Pulumi apply marks the password permanent

- **WHEN** `pulumi up` runs on the `dev` stack with `E2eTestUserComponent` enabled
- **THEN** a `ZitadelHumanUserPasswordPermanent` Dynamic Resource SHALL be created with `dependsOn: [humanUser]` so it executes only after the `zitadel.HumanUser` for `e2e-test-password` is ready
- **AND** the resource's `create()` handler SHALL POST `/management/v1/users/{user_id}/password` with `{ password, noChangeRequired: true }` against the dev Zitadel domain
- **AND** the resource SHALL receive the same ESC-sourced password the HumanUser was created with (`pulumiConfig.zitadel.e2eTestUser.password`)
- **AND** any 2xx response from Zitadel SHALL be treated as success, including the case where the password was already marked permanent

#### Scenario: First sign-in does not redirect to /password/change

- **WHEN** the `e2e-test-password` user signs in via the OIDC password flow after `pulumi up` completes
- **THEN** the auth host SHALL NOT redirect to `/ui/v2/login/password/change`
- **AND** the OIDC callback SHALL complete directly after the password submission step
- **AND** the captured Playwright `storageState.json` SHALL contain a valid `oidc.user:*` entry

#### Scenario: ESC password rotation re-asserts permanence

- **WHEN** an operator runs `pulumi up --replace <urn-of-humanUser>` on the dev stack with a rotated ESC password value
- **THEN** the `zitadel.HumanUser` SHALL be re-created with the new `initialPassword`
- **AND** the `ZitadelHumanUserPasswordPermanent` resource SHALL be replaced (or its `update()` handler invoked) to re-POST `SetPassword` with the new password and `noChangeRequired: true`
- **AND** after apply, the user SHALL still NOT be redirected to `/password/change` on the next sign-in

#### Scenario: Resource removal does not unset permanence

- **WHEN** the `ZitadelHumanUserPasswordPermanent` resource is removed from Pulumi state (via `pulumi destroy --target` or a code-level removal followed by `pulumi up`)
- **THEN** the resource's `delete()` handler SHALL be a no-op and SHALL NOT call any Management API endpoint
- **AND** the underlying `zitadel.HumanUser` SHALL retain its `noChangeRequired = true` state (there is no inverse Management API verb to flip permanence off, by design)
- **AND** the user SHALL continue to authenticate without a `/password/change` redirect until the HumanUser itself is replaced
