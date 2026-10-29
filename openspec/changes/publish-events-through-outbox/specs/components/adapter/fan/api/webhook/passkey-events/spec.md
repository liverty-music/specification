## MODIFIED Requirements

### Requirement: Only authentic notices are accepted

The passkey-events webhook SHALL accept a notice only when it carries a valid signature made with the key shared with the identity provider for this webhook. A notice with a missing or invalid signature SHALL be rejected with HTTP 401 and SHALL record nothing. The endpoint SHALL be reachable only from inside the cluster.

#### Scenario: Valid signature

- **WHEN** the identity provider sends a passkey-added notice with a valid signature
- **THEN** the notice is accepted

#### Scenario: Forged notice

- **WHEN** a request arrives with a missing or invalid signature
- **THEN** it is rejected with HTTP 401 and nothing is recorded

## REMOVED Requirements

### Requirement: Passkey notices of the product organization become passkey changes
**Reason**: A passkey notice is an observation from outside and is recorded as a fact: the webhook starts PasskeyUseCase.RecordChange instead of announcing the notice, and Passkey.Create and Passkey.Delete announce the stored change ("Passkey notices of the product organization are recorded" below).
**Migration**: UserUseCase.NotifyPasskeyChange runs from the Passkey announcements; the passkey change announcement of the notice goes. A failure to start RecordChange answers HTTP 500, as a failure to announce did.

## ADDED Requirements

### Requirement: Passkey notices of the product organization are recorded

For an accepted notice that a passkey of an identity in the product organization finished registration, the webhook SHALL start PasskeyUseCase.RecordChange with a change of kind added, the identity's provider user ID, the provider passkey id, the AAGUID of its passkey provider and the notice's time; for a notice that such a passkey was removed, with a change of kind removed, the provider user ID, the provider passkey id and the notice's time, without an AAGUID. A notice without a time SHALL take the time it was received. It SHALL answer HTTP 200 once RecordChange is started, and the same for a repeated notice, which starts nothing new. Notices of other kinds, and notices about identities of other organizations, SHALL be answered with HTTP 200 and record nothing. When RecordChange cannot be started, the webhook SHALL log the failure and answer HTTP 500; the identity provider does not deliver a notice again, so that change is not recorded or emailed.

#### Scenario: Passkey registered

- **WHEN** an accepted notice says a fan identity's passkey finished registration
- **THEN** RecordChange is started with a change of kind added, the passkey's provider passkey id and its AAGUID, and the webhook answers HTTP 200

#### Scenario: Passkey removed

- **WHEN** an accepted notice says a fan identity's passkey was removed
- **THEN** RecordChange is started with a change of kind removed and the passkey's provider passkey id

#### Scenario: Same notice twice

- **WHEN** the identity provider sends the same accepted notice twice
- **THEN** the webhook answers HTTP 200 both times and the change is recorded once

#### Scenario: Organizer identity

- **WHEN** an accepted notice is about an identity in an Organizer's Organization
- **THEN** the webhook answers HTTP 200 and nothing is recorded

#### Scenario: RecordChange cannot be started

- **WHEN** RecordChange cannot be started for an accepted notice
- **THEN** the webhook logs the failure and answers HTTP 500, and the change is neither recorded nor emailed
