## ADDED Requirements

### Requirement: Provision Password-Based E2E Test User in Dev Zitadel

The dev self-hosted Zitadel instance SHALL provision, via Pulumi, a password-based `zitadel.HumanUser` for E2E test automation, distinct from the existing passkey-only test user. The provisioning SHALL be gated to the `dev` Pulumi stack and SHALL NOT execute in any other stack.

**Rationale**: Passkey authentication requires a biometric/PIN gesture from a registered device and cannot be replayed by headless Playwright. A separate password-based user provides a credential path that headless test automation can drive end-to-end, unblocking E2E coverage of the post-cutover self-hosted issuer.

#### Scenario: Pulumi apply on dev stack provisions the test user

- **WHEN** `pulumi up` runs on the `dev` stack
- **THEN** a `zitadel.HumanUser` resource SHALL be created in the self-hosted Zitadel instance with a recognizable display name and an email under the dev domain
- **AND** the user SHALL have `InitialPassword` set from a Pulumi config value (encrypted at rest in the stack's secrets backend)
- **AND** the user SHALL have no second-factor (TOTP / SMS / passkey) enrollment

#### Scenario: Pulumi apply on non-dev stack rejects the resource

- **WHEN** `pulumi up` runs on any stack other than `dev`
- **AND** the test-user resource definition is reachable in code
- **THEN** the Pulumi component SHALL throw at synthesis time with a clear "test user is dev-only" error message
- **AND** no test-user resource SHALL be created in Zitadel

#### Scenario: Resource replacement preserves operator awareness

- **WHEN** a Pulumi diff would replace the test user (e.g., from changing `InitialPassword` directly)
- **THEN** the operator SHALL receive a clear preview indicating the replacement
- **AND** the test user's `initialPassword` field SHALL be marked `ignoreChanges` so casual edits do not trigger silent re-provisioning that would invalidate the captured Playwright storage state

### Requirement: Test User Coexists with Passkey User

The Pulumi-provisioned password-based E2E test user SHALL coexist with the existing passkey-only test user. Neither user SHALL replace, deactivate, or alter the other.

**Rationale**: The passkey user remains the canonical UX path for device-bound manual smoke testing. The password user is added purely to unblock headless automation. Removing the passkey user would lose coverage of the passkey login flow.

#### Scenario: Both users present after provisioning

- **WHEN** the change is applied to dev
- **THEN** the existing passkey-only user SHALL still be present in Zitadel and unchanged
- **AND** the new password-based user SHALL also be present
- **AND** both users SHALL be assignable to the same OIDC Application via the same role grants
