## ADDED Requirements

### Requirement: Provision Password-Based E2E Test User in Dev Zitadel

The dev self-hosted Zitadel instance SHALL provision, via Pulumi, a password-based `zitadel.HumanUser` for E2E test automation, distinct from the existing passkey-only test user. The provisioning SHALL be gated to the `dev` Pulumi stack and SHALL NOT execute in any other stack.

**Rationale**: Passkey authentication requires a biometric/PIN gesture from a registered device and cannot be replayed by headless Playwright. A separate password-based user provides a credential path that headless test automation can drive end-to-end, unblocking E2E coverage of the post-cutover self-hosted issuer.

#### Scenario: Pulumi apply on dev stack provisions the test user

- **WHEN** `pulumi up` runs on the `dev` stack
- **THEN** a `zitadel.HumanUser` resource SHALL be created in the self-hosted Zitadel instance with a recognizable display name and an email under the dev domain
- **AND** the user SHALL have `InitialPassword` set from the ESC value `pulumiConfig.zitadel.e2eTestUser.password` (read via `config.requireSecretObject`)
- **AND** the user SHALL have no second-factor (TOTP / SMS / passkey) enrollment

#### Scenario: Pulumi apply on non-dev stack rejects the resource

- **WHEN** `pulumi up` runs on any stack other than `dev`
- **AND** the test-user resource definition is reachable in code
- **THEN** the Pulumi component SHALL throw at synthesis time with a clear "test user is dev-only" error message
- **AND** no test-user resource SHALL be created in Zitadel

#### Scenario: `initialPassword` changes do not trigger silent replacement

- **WHEN** an operator changes the ESC value `pulumiConfig.zitadel.e2eTestUser.password`
- **AND** `pulumi preview --stack dev` is run on the next deploy
- **THEN** the preview SHALL show NO change to the e2e-test-user `zitadel.HumanUser` resource (the `ignoreChanges: ['initialPassword']` directive on the resource hides the diff)
- **AND** the captured Playwright `storageState.json` SHALL remain valid until the operator explicitly forces a replacement

#### Scenario: Intentional rotation requires an explicit replace

- **WHEN** an operator runs `pulumi up --replace <urn-of-e2e-test-user>` on the dev stack
- **THEN** the preview SHALL clearly indicate the replacement (`-/+ create replacement`)
- **AND** after apply, the new HumanUser SHALL use the latest ESC `initialPassword` value
- **AND** the operator is then responsible for re-mirroring `.auth/password.md` and re-running the headless capture script to regenerate `.auth/storageState.json`

### Requirement: Test User Coexists with Passkey User

The Pulumi-provisioned password-based E2E test user SHALL coexist with the existing passkey-only test user. Neither user SHALL replace, deactivate, or alter the other.

**Rationale**: The passkey user remains the canonical UX path for device-bound manual smoke testing. The password user is added purely to unblock headless automation. Removing the passkey user would lose coverage of the passkey login flow.

#### Scenario: Both users present after provisioning

- **WHEN** the change is applied to dev
- **THEN** the existing passkey-only user SHALL still be present in Zitadel and unchanged
- **AND** the new password-based user SHALL also be present
- **AND** both users SHALL be assignable to the same OIDC Application via the same role grants
