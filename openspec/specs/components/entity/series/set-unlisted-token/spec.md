# Series.SetUnlistedToken

## Purpose

Sets or replaces the share token of a Series; the previous token stops opening it.

## Requirements

### Requirement: Token set or replaced

SetUnlistedToken SHALL make the given token the Series' only share token. It SHALL fail with NotFound when no Series has the id and with AlreadyExists when another Series holds the same token.

#### Scenario: Token rotated
- **WHEN** a Series with token T1 is given T2
- **THEN** T2 opens the Series and T1 does not

#### Scenario: Unknown series
- **WHEN** no Series has the id
- **THEN** SetUnlistedToken fails with NotFound
