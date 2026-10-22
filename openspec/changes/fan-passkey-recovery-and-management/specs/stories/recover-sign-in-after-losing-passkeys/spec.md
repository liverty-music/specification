## Purpose

A fan who can no longer use any of their passkeys - the device was lost, reset or replaced, or the passkey was not synced - gets back into the same account with a new passkey, using only their verified email address.

```mermaid
usecase-beta
direction LR
actor Fan("fan")
systemBoundary "Liverty Music"
  Goal("Recover sign-in after losing passkeys")
  RequestRecovery("UserUseCase.RequestPasskeyRecovery")
  SendLink("UserUseCase.SendPasskeyRecoveryLink")
  Notify("UserUseCase.NotifyPasskeyChange")
end
Fan --> Goal
Goal ..> : include RequestRecovery
Goal ..> : include SendLink
Goal ..> : include Notify
```

## ADDED Requirements

### Requirement: A fan regains the same account from an email link

A fan who cannot sign in SHALL be able to open the passkey recovery screen from the welcome page or the Settings guest hero, request a link for their account's email address, open the emailed link within 1 hour on the device in hand, create a new passkey there, and sign in to the same account with its follows, tickets and settings unchanged. The fan SHALL then receive the email that a passkey was added. A person who does not control the account's verified mailbox SHALL NOT be able to add a passkey this way, and the answers of the recovery screen SHALL NOT tell anyone whether an address has an account.

#### Scenario: Lost phone, new phone

- **WHEN** a fan whose only passkey was on a lost phone requests a link on a new phone, opens it from their mailbox there within 1 hour and creates a passkey
- **THEN** they sign in on the new phone to the same account, see their own follows, and receive the passkey-added email

#### Scenario: Someone else types the fan's address

- **WHEN** another person requests a link for the fan's address
- **THEN** the link reaches only the fan's mailbox, the other person sees the same message as for any address, and no passkey is added

#### Scenario: Link expired

- **WHEN** the fan opens the link after more than 1 hour
- **THEN** no passkey is created and the fan can request a new link from the passkey recovery screen
