## MODIFIED Requirements

### Requirement: Provision Password-Based E2E Test User in Dev Zitadel

The dev self-hosted Zitadel instance SHALL provision, via Pulumi, a password-based `zitadel.HumanUser` for E2E test automation. The provisioning SHALL be gated to the `dev` Pulumi stack and SHALL NOT execute in any other stack.

**Rationale**: Headless test automation cannot drive a passkey-only login flow (passkey requires a biometric / PIN gesture from a registered device). A Pulumi-managed password-based user provides a credential path the headless capture script can drive end-to-end, unblocking E2E coverage of the post-cutover self-hosted issuer. (Earlier wording referenced "distinct from the existing passkey-only test user" — that wording was inherited from the original `playwright-password-test-user` change but no passkey-only test user exists on the active self-hosted dev Zitadel; the Zitadel-Cloud-era Self-Registration user was wiped by `self-hosted-zitadel §10` and never re-provisioned. See change `remove-passkey-capture-path` for the cleanup record.)

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

## REMOVED Requirements

### Requirement: Test User Coexists with Passkey User

**Reason**: The requirement asserts "the existing passkey-only user SHALL still be present in Zitadel and unchanged", but on the active self-hosted dev Zitadel there is no passkey-only test user. The user the requirement refers to (`pepperoni9+playwright-1@gmail.com`) was a Zitadel-Cloud-era Self-Registration account that was wiped by `self-hosted-zitadel §10`'s `truncate_users_for_zitadel_migration` Atlas migration and was never re-provisioned. The requirement therefore mandates a state that does not exist; retaining it puts main specs in direct contradiction with the `Existing Passkey Capture Path Retained` removal in `e2e-auth-testing/spec.md` (this same change) and with the reality of the live dev Zitadel.

**Migration**: None required at the system level — there was nothing to coexist with. The `Provision Password-Based E2E Test User in Dev Zitadel` requirement (MODIFIED in this same delta to drop the "distinct from the existing passkey-only test user" phrasing) remains the single normative source of truth for the dev E2E test user. If a future need for a parallel passkey-based test user surfaces (e.g., for virtual-authenticator-driven WebAuthn regression testing), a new requirement should be authored in that change rather than restoring this one.
