## MODIFIED Requirements

### Requirement: Configure Login Policy

The system SHALL establish a login policy on the **`liverty-music` product
org** (the org that hosts the OIDC application and end-user accounts) that
makes passkeys the fans' only sign-in credential. This policy SHALL apply ONLY to the
`liverty-music` product org and MUST NOT be inherited by the `admin` role
org, which has its own admin-oriented login policy governed by separate
requirements.

Passkey-only is expressed by allowing passwordless sign-in and never issuing
a fan a password, NOT by disabling local authentication: `UserLogin` gates all
local authentication (email plus passkey or password), and with it off the
hosted login renders no usable form. The product SHALL offer fans no password
sign-up, no password sign-in and no password reset; the only identity in the
product org with a password is the automated end-to-end test user of the
development environment.

#### Scenario: Apply Strict Passkeys Policy on product org

- **WHEN** Pulumi stack is applied
- **THEN** the login policy for the `liverty-music` product org SHALL be
  configured
- **AND** `PasswordlessType` SHALL be "ALLOWED"
- **AND** `UserLogin` SHALL be true, because it also gates passkey sign-in
- **AND** `HidePasswordReset` SHALL be true
- **AND** `AllowExternalIdp` SHALL be false

#### Scenario: Admin org isolation

- **WHEN** the `liverty-music` product org login policy is applied
- **THEN** the policy SHALL NOT be applied to the `admin` role org
- **AND** the `admin` role org SHALL retain a separate login policy that
  allows external IdP sign-in (see "Configure Admin Org Login Policy")

## ADDED Requirements

### Requirement: Fans have a recovery path for lost passkeys

A fan account SHALL never depend on a single passkey with no way back in. A fan SHALL be able to register more than one passkey, and a fan who can use none of them SHALL be able to register a new one through an emailed link sent to the account's verified address (see the passkey recovery screen). Synced passkeys survive the loss of one device, so a second hardware authenticator is NOT required.

#### Scenario: Fan lost every passkey

- **WHEN** a fan with a verified address can use none of their passkeys
- **THEN** they can request a link from the passkey recovery screen, register a new passkey with it and sign in to the same account

### Requirement: The hosted login registers a passkey from a registration link

When a person opens a passkey registration link within its 1-hour validity, the hosted login SHALL let them create a passkey for the identity the link was sent for without signing in first, and SHALL then send them to the fan app, where they sign in with the new passkey. A link that is expired or was already used SHALL register nothing, and the person SHALL be able to request a new link from the passkey recovery screen.

#### Scenario: Valid link

- **WHEN** a fan opens a 10-minute-old registration link on a laptop and confirms a new passkey
- **THEN** the passkey is registered for their identity, they arrive in the fan app and can sign in with that passkey

#### Scenario: Cancelled passkey prompt

- **WHEN** the fan cancels the device's passkey prompt on the link's page
- **THEN** no passkey is registered and the link cannot be used again; the fan requests a new link

### Requirement: A signed-in fan adds a passkey on the device in hand

When the fan app sends a fan who signed in within the last 5 minutes to add a passkey, the hosted login SHALL create a new passkey for that fan's identity on the device in hand, keep the fan's other passkeys, and return the fan to the fan app. A passkey already registered on the same passkey provider SHALL NOT be registered twice.

#### Scenario: Second device

- **WHEN** a fan who signed in on a Windows laptop with their phone's passkey adds a passkey there
- **THEN** the identity has a passkey on the laptop's passkey provider as well as the phone's, and the fan returns to the fan app

#### Scenario: Same provider again

- **WHEN** the fan tries to add a passkey on a provider that already holds one of theirs
- **THEN** no second passkey is created there
