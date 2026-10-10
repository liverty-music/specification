# Spec Delta

## Purpose

Binds a Scanner to the public key of the first device that opens its link, and tells later callers whether they are that device.

## ADDED Requirements

### Requirement: BindDevice binds once and recognises the bound device

BindDevice SHALL take a Scanner, a public key and a time. When the Scanner is Unused, it SHALL set the bound public key and the bound time, make the Scanner InUse and report Bound. When the Scanner is InUse with the same public key, it SHALL change nothing and report Bound. When the Scanner is InUse with another public key, it SHALL change nothing and report OtherDevice. When the Scanner is Revoked, it SHALL change nothing and report Revoked. Checking and binding SHALL be one indivisible step, so that when two devices open an Unused Scanner's link at the same time exactly one is bound. It SHALL fail with InvalidArgument when the public key is not a valid P-256 key, and with NotFound when no Scanner has the id.

#### Scenario: First device

- **WHEN** an Unused Scanner is bound with public key P1 at 14:10
- **THEN** the Scanner is InUse with P1 and bound time 14:10, and BindDevice reports Bound

#### Scenario: Same device again

- **WHEN** a Scanner InUse with P1 is bound with P1
- **THEN** nothing changes and BindDevice reports Bound

#### Scenario: Another device

- **WHEN** a Scanner InUse with P1 is bound with P2
- **THEN** nothing changes and BindDevice reports OtherDevice

#### Scenario: Two devices at once

- **WHEN** an Unused Scanner is bound with P1 and with P2 at the same time
- **THEN** exactly one of them reports Bound and the other reports OtherDevice

#### Scenario: Revoked scanner

- **WHEN** a Revoked Scanner is bound
- **THEN** nothing changes and BindDevice reports Revoked
