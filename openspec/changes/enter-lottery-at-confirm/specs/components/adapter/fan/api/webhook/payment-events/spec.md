## MODIFIED Requirements

### Requirement: Other notices are acknowledged

Notices that a refund was applied, that a payout was reversed, or that the platform's own bank payout succeeded or failed, and notices of any other kind than a dispute, a completed charge or a completed card authentication, SHALL be acknowledged without effect.

#### Scenario: Refund confirmation

- **WHEN** a notice confirms a refund the platform issued
- **THEN** it is acknowledged and nothing changes

## ADDED Requirements

### Requirement: A completed card authentication confirms the lottery entry

On a notice that a card authorization became Authorized, the endpoint SHALL call LotteryEntryUseCase.Confirm with the notice's card authorization and no calling fan. A rejection by Confirm (PermissionDenied, FailedPrecondition, InvalidArgument) SHALL be acknowledged, since Confirm has already released what it rejected; any other failure SHALL be answered with Internal, so the provider delivers the notice again.

#### Scenario: Fan closed the browser

- **WHEN** a notice reports a fan's lottery card authorization Authorized and the fan never called Confirm
- **THEN** LotteryEntryUseCase.Confirm runs and the entry is made

#### Scenario: Entry already made

- **WHEN** the notice arrives after the fan's Confirm made the entry
- **THEN** it is acknowledged and nothing changes

#### Scenario: Payment provider unreachable

- **WHEN** Confirm fails with Unavailable
- **THEN** the endpoint answers with Internal and a redelivery handles the notice again
