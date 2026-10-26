## Purpose

CardAuthorizationUseCase.Release gives back, without charging, the card authorization of a lottery entry the draw did not admit and of a Draft that took no part in the draw.

## ADDED Requirements

### Requirement: Every card authorization the draw does not charge is released

Release SHALL run for the card authorization of each entry that LotteryEntry.RecordDrawOutcome records Lost, and of each Draft with a card authorization that LotteryEntryUseCase.Draw passes over, starting within 1 minute after the draw records them. It SHALL release the card authorization with CardAuthorization.Release:
- When the release fails with Unavailable, it SHALL try again at growing intervals for up to 24 hours; when it still fails, it SHALL stop and report the card authorization for an admin.
- When the release fails with FailedPrecondition, meaning the card was charged, it SHALL stop and report the card authorization for an admin at once.
- When it fails with NotFound, it SHALL stop and report the card authorization for an admin.

#### Scenario: Loser released
- **WHEN** a draw records an entry Lost
- **THEN** within 1 minute its card authorization is Released and nothing is charged

#### Scenario: Unconfirmed draft released
- **WHEN** the draw passes over a Draft with an Authorized card authorization
- **THEN** within 1 minute that card authorization is Released

#### Scenario: Payment provider unavailable
- **WHEN** CardAuthorization.Release fails with Unavailable and succeeds 10 minutes later
- **THEN** the card authorization is Released

#### Scenario: Charged card authorization
- **WHEN** CardAuthorization.Release fails with FailedPrecondition
- **THEN** Release stops and the card authorization is reported for an admin
