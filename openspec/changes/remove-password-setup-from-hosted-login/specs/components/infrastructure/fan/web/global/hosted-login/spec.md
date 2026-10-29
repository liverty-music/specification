# Spec Delta

## MODIFIED Requirements

### Requirement: Configure Login Policy

The system SHALL establish a login policy on the **`liverty-music` product
org** (the org that hosts the OIDC application and end-user accounts) that
makes passkeys the only sign-in credential for every fan other than the automated end-to-end test fans. This policy SHALL apply ONLY to the
`liverty-music` product org and MUST NOT be inherited by the `admin` role
org, which has its own admin-oriented login policy governed by separate
requirements.

Passkey-only is expressed by allowing passwordless sign-in and never issuing
a fan a password, NOT by disabling local authentication: `UserLogin` gates all
local authentication (email plus passkey or password), and with it off the
hosted login renders no usable form. The product SHALL offer fans no password
sign-up and no password reset (see "The hosted login offers no way to set a
password"). The only identities in the product org with a password are the
automated end-to-end test fans, in every environment that runs them,
production included; they sign in with that password.

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

### Requirement: The hosted login offers no way to set a password

No page of the hosted login SHALL let a person set a password on an identity:
not on sign-up, not when choosing which credential to set up, not through a
reset code, and not by changing a password after signing in. A page that
would set a password SHALL instead show the hosted login's not-found page,
whether it is reached by a link or by typing its address. A request that
reaches the hosted login's server without going through those pages SHALL be
refused in the same way, so no request to the hosted login sets a password.
An identity that already has a password SHALL still sign in with it.

#### Scenario: Sign-up offers only a passkey

- **WHEN** a person opens the hosted login's sign-up page from the fan app and fills in their name and email
- **THEN** the page offers no Password choice, and continuing takes them to passkey registration

#### Scenario: Choosing a credential to set up offers no password

- **WHEN** the hosted login asks a person which credential to set up for their identity
- **THEN** Passkey is offered and Password is not

#### Scenario: Password pages opened by address

- **WHEN** a person opens the sign-up password step, the set-password page or the change-password page by typing its address, with or without a reset code
- **THEN** the hosted login shows its not-found page and no password is set

#### Scenario: Password sent to the hosted login without its pages

- **WHEN** a request carrying a new password is sent to the hosted login's server directly, for sign-up, a reset code or a signed-in session, without opening any of its pages
- **THEN** the hosted login refuses it and no password is set

#### Scenario: No password reset on the password page

- **WHEN** a person reaches the hosted login's password page
- **THEN** it offers no way to request a password reset

#### Scenario: Existing password still signs in

- **WHEN** an automated end-to-end test fan signs in with their email and password
- **THEN** sign-in succeeds as before
