## Purpose

PasskeyUseCase.RecordChange keeps the platform's Passkey records in step with the passkeys added to and removed from fans' identities, so passkey management can show each passkey's provider and registration date.

## ADDED Requirements

### Requirement: Each passkey change is recorded

RecordChange SHALL run for each announced passkey change, carrying the identity's provider user ID, the provider passkey id, the kind of change (added or removed), the AAGUID for an added passkey and the time of the change. For an added passkey it SHALL read the User with User.GetByProviderUserID and store the Passkey with Passkey.Create, using the time of the change as its create time. For a removed passkey it SHALL remove the record with Passkey.Delete. When storing or removing fails with Unavailable, RecordChange SHALL fail and run again.

#### Scenario: Passkey added

- **WHEN** a passkey is added for a fan's identity with an AAGUID of `Google Password Manager`
- **THEN** a Passkey with that provider passkey id, AAGUID and the change's time is stored for the fan

#### Scenario: Passkey removed

- **WHEN** a passkey is removed from a fan's identity
- **THEN** its Passkey is no longer stored

#### Scenario: Change announced twice

- **WHEN** the same added change is handled twice
- **THEN** one Passkey is stored

#### Scenario: Store unavailable

- **WHEN** Passkey.Create fails with Unavailable
- **THEN** RecordChange fails and the Passkey is stored when it runs again

### Requirement: A passkey added during sign-up is recorded once the account exists

A passkey is registered at sign-up before the fan's User exists. When no User has the provider user ID of an added passkey, RecordChange SHALL fail and run again, and SHALL finish without recording once the change is more than 10 minutes old.

#### Scenario: Account created after the passkey

- **WHEN** an added change is handled before the fan's User exists, and the User is created 5 seconds later
- **THEN** the Passkey is stored when RecordChange runs again

#### Scenario: Identity that never becomes an account

- **WHEN** no User has the provider user ID 10 minutes after the change
- **THEN** RecordChange finishes without storing anything
