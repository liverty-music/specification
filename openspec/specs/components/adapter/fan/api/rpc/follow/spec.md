# Follow RPC

## Purpose

The fan-facing follow service boundary: who may follow, unfollow, list follows and set a hype level, and what the boundary itself decides before FollowUseCase runs.

## Requirements

### Requirement: Every follow call acts for the signed-in caller

Follow, Unfollow, ListFollowed and SetHype SHALL act only for the signed-in caller, resolved to their stored User (User.GetByExternalID) before the usecase runs; no call accepts another fan. They SHALL fail with Unauthenticated when the caller is not signed in, and with NotFound when the caller has no account (the fan must finish registration first).

#### Scenario: Signed-in fan follows

- **WHEN** a signed-in fan with an account calls Follow for an artist
- **THEN** FollowUseCase.Follow runs for that fan

#### Scenario: Not signed in

- **WHEN** the caller is not authenticated
- **THEN** the call fails with Unauthenticated and no usecase runs

#### Scenario: Caller has no account

- **WHEN** the signed-in caller has no stored account
- **THEN** the call fails with NotFound and no usecase runs

### Requirement: Follow requests are validated at the boundary

Follow, Unfollow and SetHype SHALL fail with InvalidArgument when no artist is given. SetHype SHALL fail with InvalidArgument when no hype level, or an undefined one, is given.

#### Scenario: Missing artist

- **WHEN** SetHype is called without an artist
- **THEN** it fails with InvalidArgument

#### Scenario: Missing hype level

- **WHEN** SetHype is called without a hype level
- **THEN** it fails with InvalidArgument and the Follow is unchanged
