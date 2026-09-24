# PayoutSweeperUseCase.ReleaseDueSettlements

## Purpose

PayoutSweeperUseCase.ReleaseDueSettlements pays out every Held Settlement whose event started more than 7 days ago and whose Organizer can receive payouts, then marks it Released.

## Requirements

### Requirement: Release after the event plus 7 days

ReleaseDueSettlements SHALL run every 5 minutes over the Settlements from Settlement.ListHeld. For each, it SHALL read the Order with Order.Get and the event's current start time with Event.GetEventStartTime, and SHALL withhold the Settlement unless it is eligible for release with a dispute buffer of 7 days. Because the start time is read on every run, a 延期 (postponement) moves the release to 7 days after the new start. A Settlement whose event does not exist is skipped.

#### Scenario: Before the event plus 7 days

- **WHEN** the event started 3 days ago
- **THEN** the Settlement stays Held

#### Scenario: Event start unknown

- **WHEN** the event has no start time
- **THEN** the Settlement stays Held

#### Scenario: Event postponed

- **WHEN** the event is rescheduled to a later date before its payout is released
- **THEN** the Settlement stays Held until 7 days after the new start

### Requirement: Payout waits for the Organizer's payout account

ReleaseDueSettlements SHALL withhold the Settlement, without failing it, when the Organizer has no payout account, found with OrganizerConnectedAccount.GetByOrganizerID, or when the account is not Active. It SHALL refresh the account's status with OrganizerConnectedAccount.GetAccountStatus before deciding, and use the stored status when the refresh fails.

#### Scenario: No payout account

- **WHEN** the Organizer has no payout account
- **THEN** the Settlement stays Held and is tried again on the next run

#### Scenario: Onboarding not complete

- **WHEN** the Organizer's payout account is Pending or Restricted
- **THEN** the Settlement stays Held

### Requirement: Pay out and mark Released

For an eligible Settlement with an Active payout account, ReleaseDueSettlements SHALL fail that Settlement, leaving it Held, when its splits break the Settlement split rules against the Order's amount. Otherwise it SHALL resolve the Order's charge with Order.ResolveChargeRef, pay each split to the Organizer's payout account with Settlement.CreateTransfer in the Order's currency, and record the release with Settlement.MarkReleased. When Settlement.MarkReleased fails with FailedPrecondition because the Settlement is no longer Held, the Settlement is skipped without error.

#### Scenario: Settlement released

- **WHEN** a Held Settlement's event started 8 days ago and the Organizer's payout account is Active
- **THEN** its split is paid to the Organizer's payout account and it is Released

#### Scenario: Invalid splits

- **WHEN** a due Settlement has no split
- **THEN** nothing is paid and it stays Held

#### Scenario: Released concurrently

- **WHEN** Settlement.MarkReleased fails with FailedPrecondition
- **THEN** the Settlement is skipped and no error is raised

### Requirement: One failure does not block the others

A Settlement whose release fails SHALL NOT stop the others and stays Held for the next run. When Settlement.ListHeld fails, ReleaseDueSettlements SHALL fail with that error and release nothing.

#### Scenario: One payout fails

- **WHEN** paying one Settlement fails with Unavailable
- **THEN** the other due Settlements are still released and the failed one is tried again 5 minutes later
