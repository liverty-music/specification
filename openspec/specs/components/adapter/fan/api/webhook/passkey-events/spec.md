# components/adapter/fan/api/webhook/passkey-events Specification

## Purpose
Receives the identity provider's notices that a passkey was added to or removed from an identity of the product organization, and announces each one as a passkey change for UserUseCase.NotifyPasskeyChange and PasskeyUseCase.RecordChange.

## Requirements

### Requirement: Only authentic notices are accepted

The passkey-events webhook SHALL accept a notice only when it carries a valid signature made with the key shared with the identity provider for this webhook. A notice with a missing or invalid signature SHALL be rejected with HTTP 401 and SHALL announce nothing. The endpoint SHALL be reachable only from inside the cluster.

#### Scenario: Valid signature

- **WHEN** the identity provider sends a passkey-added notice with a valid signature
- **THEN** the notice is accepted

#### Scenario: Forged notice

- **WHEN** a request arrives with a missing or invalid signature
- **THEN** it is rejected with HTTP 401 and nothing is announced

### Requirement: Passkey notices of the product organization become passkey changes

For an accepted notice that a passkey of an identity in the product organization finished registration, the webhook SHALL announce a passkey change of kind added with the identity's provider user ID, the provider passkey id, the passkey's name, the AAGUID of its passkey provider and the notice's time; for a notice that such a passkey was removed, a change of kind removed with the provider user ID, the provider passkey id and the notice's time, without a name or AAGUID. It SHALL answer HTTP 200 after announcing. Notices of other kinds, and notices about identities of other organizations, SHALL be answered with HTTP 200 and announce nothing. When the announcement cannot be made, the webhook SHALL log the failure and answer HTTP 500; the identity provider does not deliver a notice again, so that change is not emailed.

#### Scenario: Passkey registered

- **WHEN** an accepted notice says a fan identity's passkey named `Apple iPhone, iOS, Mobile Safari` finished registration
- **THEN** a passkey change of kind added with that name, the passkey's provider passkey id and its AAGUID is announced and the webhook answers HTTP 200

#### Scenario: Passkey removed

- **WHEN** an accepted notice says a fan identity's passkey was removed
- **THEN** a passkey change of kind removed with the passkey's provider passkey id is announced

#### Scenario: Organizer identity

- **WHEN** an accepted notice is about an identity in an Organizer's Organization
- **THEN** the webhook answers HTTP 200 and nothing is announced

#### Scenario: Announcement fails

- **WHEN** the passkey change cannot be announced
- **THEN** the webhook logs the failure and answers HTTP 500, and no email is sent for that change
