## ADDED Requirements

### Requirement: Test User Coexists with Passkey User

The Pulumi-provisioned password-based E2E test user SHALL coexist with the existing passkey-only test user. Neither user SHALL replace, deactivate, or alter the other.

**Rationale**: The passkey user remains the canonical UX path for device-bound manual smoke testing. The password user is added purely to unblock headless automation. Removing the passkey user would lose coverage of the passkey login flow.

#### Scenario: Both users present after provisioning

- **WHEN** the change is applied to dev
- **THEN** the existing passkey-only user SHALL still be present in Zitadel and unchanged
- **AND** the new password-based user SHALL also be present
- **AND** both users SHALL be assignable to the same OIDC Application via the same role grants
