# components/entity/user/send-passkey-registration-link Specification

## Purpose
Sends the User's verified email address a link that registers a new passkey for the User's identity on whichever device the link is opened, so a person who lost every passkey can sign in again.

## Requirements

### Requirement: SendPasskeyRegistrationLink emails a single-use link to a verified address

SendPasskeyRegistrationLink SHALL send one email to the address the User's identity has verified, in the User's preferred language (Japanese when none), with a link that opens the hosted login and registers a new passkey for that identity without signing in first. The link SHALL stop working 1 hour after it is sent, and once a registration has been started with it. The email SHALL say that it was requested from the Liverty Music sign-in help and can be ignored when the recipient did not request it. Passkeys the identity already has SHALL stay registered. It SHALL fail with FailedPrecondition and send nothing when the identity's address is not verified, with NotFound when the identity no longer exists, and with Internal on any other failure to send.

#### Scenario: Verified address

- **WHEN** SendPasskeyRegistrationLink runs for a User whose identity has the verified address `fan@example.com`
- **THEN** one email with a registration link reaches `fan@example.com`

#### Scenario: Link opened on a new device

- **WHEN** the person opens the link on a phone within 1 hour and confirms the new passkey
- **THEN** the identity has one more passkey, created on that phone, and its earlier passkeys are unchanged

#### Scenario: Link older than 1 hour

- **WHEN** the person opens the link 61 minutes after it was sent
- **THEN** no passkey is registered and the hosted login says the link is no longer valid

#### Scenario: Link used twice

- **WHEN** a registration was started with the link and the link is opened again
- **THEN** no passkey is registered with it

#### Scenario: Unverified address

- **WHEN** the identity's address is not verified
- **THEN** SendPasskeyRegistrationLink fails with FailedPrecondition and no email is sent

#### Scenario: Identity removed

- **WHEN** the User's identity no longer exists
- **THEN** SendPasskeyRegistrationLink fails with NotFound
