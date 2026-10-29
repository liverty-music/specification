## Purpose

LotteryEntryUseCase.ReleaseCardAuthorization gives back, without charging, the card authorization of a Lost LotteryEntry's Order.

## ADDED Requirements

### Requirement: Every Lost entry's card authorization is released

ReleaseCardAuthorization SHALL run once for each entry that LotteryEntry.PersistDrawOutcome records Lost and each entry that LotteryEntry.RevertWin makes Lost. It SHALL read the entry with LotteryEntry.Get and its Order with Order.Get, and release the Order's card authorization with CardAuthorization.Release. It SHALL fail with FailedPrecondition, releasing nothing, when the entry is not Lost. When the release fails with Unavailable, it SHALL try again until 24 hours after it started; a failure of any other kind, such as FailedPrecondition for a card authorization that was charged, SHALL end it with that failure. A run that ends with a failure, or stops at its 24 hours, SHALL be reported to an admin, so no Lost entry's card authorization is left held without notice.

#### Scenario: Loser released
- **WHEN** a draw records an entry Lost
- **THEN** its Order's card authorization is Released and nothing is charged

#### Scenario: Win reverted
- **WHEN** OrderUseCase.Issue makes a Won entry Lost because its card authorization can no longer be charged
- **THEN** ReleaseCardAuthorization runs for it and the card authorization is Released

#### Scenario: Payment provider unavailable
- **WHEN** CardAuthorization.Release fails with Unavailable and succeeds 10 minutes later
- **THEN** the card authorization is Released

#### Scenario: Payment provider unavailable for a day
- **WHEN** CardAuthorization.Release fails with Unavailable for 24 hours
- **THEN** ReleaseCardAuthorization stops, the card authorization stays as it is, and an admin is told

#### Scenario: Charged card authorization
- **WHEN** CardAuthorization.Release fails with FailedPrecondition
- **THEN** ReleaseCardAuthorization ends with FailedPrecondition, nothing changes, and an admin is told
