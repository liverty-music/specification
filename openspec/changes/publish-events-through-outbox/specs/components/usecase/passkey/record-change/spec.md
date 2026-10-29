## MODIFIED Requirements

### Requirement: Each passkey change is recorded

RecordChange SHALL run when the passkey-events webhook starts it for an accepted passkey notice, carrying the identity's provider user ID, the provider passkey id, the kind of change (added or removed), the AAGUID for an added passkey and the time of the change. The business key of the run SHALL be the provider passkey id and the kind of change, so a notice the identity provider repeats starts nothing new. For an added passkey it SHALL read the User with User.GetByProviderUserID and store the Passkey with Passkey.Create, using the time of the change as its create time and the all-zero AAGUID when none was given. For a removed passkey it SHALL first wait until the run for the same provider passkey id's added change, when one exists, has ended, and then remove the record with Passkey.Delete, so a passkey removed while its addition still waits for the User is not stored afterwards. Passkey.Create and Passkey.Delete announce the change they make; RecordChange itself SHALL announce nothing. When Passkey.Create fails with NotFound because the User was deleted after it was read, RecordChange SHALL finish without recording. When storing or removing fails with Unavailable, the step SHALL be tried again.

#### Scenario: Passkey added

- **WHEN** a passkey is added for a fan's identity with an AAGUID of `Google Password Manager`
- **THEN** a Passkey with that provider passkey id, AAGUID and the change's time is stored for the fan

#### Scenario: Passkey removed

- **WHEN** a passkey is removed from a fan's identity
- **THEN** its Passkey is no longer stored

#### Scenario: Change announced twice

- **WHEN** the same added change is handled twice
- **THEN** one Passkey is stored and one added Passkey is announced

#### Scenario: Store unavailable

- **WHEN** Passkey.Create fails with Unavailable
- **THEN** the step is tried again and the Passkey is stored once the store answers

### Requirement: A passkey added during sign-up is recorded once the account exists

A passkey is registered at sign-up before the fan's User exists. When no User has the provider user ID of an added passkey, RecordChange SHALL wait and look for the User again, every 30 seconds, also across a stop of the process, and SHALL finish without recording once 10 minutes have passed since it first ran for the change.

#### Scenario: Account created after the passkey

- **WHEN** an added change is handled before the fan's User exists, and the User is created 5 seconds later
- **THEN** the Passkey is stored when RecordChange looks again

#### Scenario: Identity that never becomes an account

- **WHEN** no User has the provider user ID 10 minutes after RecordChange first ran for the change
- **THEN** RecordChange finishes without storing anything

#### Scenario: Removed while its addition waits

- **WHEN** a passkey is added at sign-up, removed 2 minutes later, and the fan's User is created 3 minutes after the addition
- **THEN** the removed run waits until the added run has stored the Passkey, then removes it, and no Passkey remains
