# components/entity/passkey/delete Specification

## Purpose
Removes the record of a passkey that was removed at the identity provider, so a removed passkey is never shown with a provider or registration time.

## Requirements

### Requirement: Delete by provider passkey id is idempotent

Delete SHALL remove the Passkey with the given provider passkey id and SHALL succeed without change when none exists.

#### Scenario: Recorded passkey

- **WHEN** Delete runs for the provider passkey id of a stored Passkey
- **THEN** that Passkey is no longer stored

#### Scenario: Never recorded

- **WHEN** no Passkey has the provider passkey id
- **THEN** Delete succeeds
