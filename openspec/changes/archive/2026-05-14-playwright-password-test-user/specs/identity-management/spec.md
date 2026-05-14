## ADDED Requirements

### Requirement: Provision Password-Based E2E Test User in Dev Zitadel

The dev self-hosted Zitadel instance SHALL provision, via Pulumi, a password-based `zitadel.HumanUser` for E2E test automation, distinct from the existing passkey-only test user. The provisioning SHALL be gated to the `dev` Pulumi stack and SHALL NOT execute in any other stack.

**Rationale**: Passkey authentication requires a biometric/PIN gesture from a registered device and cannot be replayed by headless Playwright. A separate password-based user provides a credential path that headless test automation can drive end-to-end, unblocking E2E coverage of the post-cutover self-hosted issuer.

#### Scenario: Pulumi apply on dev stack provisions the test user

- **WHEN** `pulumi up` runs on the `dev` stack
- **THEN** a `zitadel.HumanUser` resource SHALL be created in the self-hosted Zitadel instance with a recognizable display name and an email under the dev domain
- **AND** the user SHALL have `InitialPassword` set from the ESC value `pulumiConfig.zitadel.e2eTestUser.password` (read via `config.requireSecretObject`)
- **AND** the user SHALL have `isEmailVerified` set to `true` — without this flag Zitadel injects an email-verification step into the OIDC flow that the headless capture script cannot handle
- **AND** the user SHALL have no second-factor (TOTP / SMS / passkey) enrollment

#### Scenario: Non-dev stacks do not provision the test user

- **WHEN** `pulumi up` runs on any stack other than `dev`
- **THEN** the Pulumi program SHALL NOT instantiate the test-user component (today via the outer `if (env === "dev")` check that gates the entire `Zitadel` composition; see Tasks §1.6/§1.8)
- **AND** no `zitadel.HumanUser` resource for `e2e-test-password` SHALL appear in the preview diff
- **AND** the component-internal synthesis guard (`if (env !== "dev") throw …`) and the parent `Zitadel` class guard remain in place as defensive depth — if the outer `if (env === "dev")` check is removed in a future refactor, either guard SHALL throw with a clear "dev-only" error message before any Zitadel API call is made

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
