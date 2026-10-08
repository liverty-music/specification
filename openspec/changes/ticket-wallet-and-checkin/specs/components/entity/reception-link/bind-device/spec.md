# Spec Delta

## Purpose

Binds a ReceptionLink to the public key of the first device that opens it, and tells later callers whether they are that device.

## ADDED Requirements

### Requirement: BindDevice binds once and recognises the bound device

BindDevice SHALL take a ReceptionLink, a public key and a time. When the link is Unused, it SHALL set the bound public key and the bound time, make the link InUse and report Bound. When the link is InUse with the same public key, it SHALL change nothing and report Bound. When the link is InUse with another public key, it SHALL change nothing and report OtherDevice. When the link is Revoked, it SHALL change nothing and report Revoked. Checking and binding SHALL be one indivisible step, so that when two devices open an Unused link at the same time exactly one is bound. It SHALL fail with InvalidArgument when the public key is not a valid P-256 key, and with NotFound when no link has the id.

#### Scenario: First device

- **WHEN** an Unused link is bound with public key P1 at 14:10
- **THEN** the link is InUse with P1 and bound time 14:10, and BindDevice reports Bound

#### Scenario: Same device again

- **WHEN** a link InUse with P1 is bound with P1
- **THEN** nothing changes and BindDevice reports Bound

#### Scenario: Another device

- **WHEN** a link InUse with P1 is bound with P2
- **THEN** nothing changes and BindDevice reports OtherDevice

#### Scenario: Two devices at once

- **WHEN** an Unused link is bound with P1 and with P2 at the same time
- **THEN** exactly one of them reports Bound and the other reports OtherDevice

#### Scenario: Revoked link

- **WHEN** a Revoked link is bound
- **THEN** nothing changes and BindDevice reports Revoked
