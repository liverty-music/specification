# Spec Delta

## MODIFIED Requirements

### Requirement: A new scanner starts Unused

A new Scanner SHALL start Unused, with a fresh random link token, no bound public key, no bind time and no revoke time.

#### Scenario: New scanner

- **WHEN** a Scanner is created
- **THEN** it is Unused, has a link token and has no bound public key

### Requirement: A call is proven by the bound device

A call through an InUse Scanner SHALL be proven when it carries a signature that verifies with the Scanner's bound public key over the link token, the call's content and a sign time, and that sign time is at most 30 seconds before and at most 15 seconds after the time the call is checked. A call through an Unused or Revoked Scanner SHALL never be proven.

#### Scenario: Call from the bound device

- **WHEN** the bound device signs a call at 18:30:00 and it is checked at 18:30:01
- **THEN** the call is proven

#### Scenario: Call from another device

- **WHEN** a call is signed with a key other than the bound public key
- **THEN** the call is not proven

#### Scenario: Replayed call

- **WHEN** a call signed at 18:30:00 is sent again and checked at 18:31:00
- **THEN** the call is not proven
