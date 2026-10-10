# Spec Delta

## Purpose

Checks a decoded AdmissionCode against its User's WalletPublicKey and the current time.

## ADDED Requirements

### Requirement: Verify accepts only a code signed by the active key and fresh

Verify SHALL take an AdmissionCode, a WalletPublicKey and a time. It SHALL report Forged when the key is not the code's user's key or the signature does not verify with it over the code's user, event, tickets and signed time; Expired when the signature verifies but the code is not fresh at that time; and Valid otherwise. Verify SHALL not fail.

#### Scenario: Code just shown

- **WHEN** a code signed at 18:30:00 with the user's key is verified at 18:30:05
- **THEN** Verify reports Valid

#### Scenario: Screenshot shown later

- **WHEN** a code signed at 18:30:00 with the user's key is verified at 18:31:00
- **THEN** Verify reports Expired

#### Scenario: Ticket added to a genuine code

- **WHEN** a ticket is added to the content of a genuine code
- **THEN** Verify reports Forged

#### Scenario: Code from a replaced device

- **WHEN** a code was signed with a key the user has since replaced, and it is verified with the user's current key
- **THEN** Verify reports Forged
