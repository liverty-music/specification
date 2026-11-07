## Purpose
LotteryEntryUseCase.EndForCancelledEvent ends the lottery entries of an Event that a member has made 中止 (cancelled), soon after the cancellation and whether or not the sale's window is still open.

## ADDED Requirements

### Requirement: Runs for each cancelled event

EndForCancelledEvent SHALL run for each Event that Series.CancelEvents announces as cancelled, and SHALL call LotteryEntry.EndEnteredByEvent for it. It starts no other work itself: the entity operation announces each entry it ends, and the card authorization is released and the fan told from that announcement. When the operation fails, EndForCancelledEvent SHALL fail with that error and run again. The cancellation SHALL stand whatever happens here: a failure here SHALL NOT undo or delay it.

#### Scenario: Concert cancelled during the window
- **WHEN** a member cancels an Event whose lottery window is open and which has Entered entries
- **THEN** every one of those entries is Lost with the lost reason "concert cancelled", and the window of the sale is unchanged

#### Scenario: Announcement delivered twice
- **WHEN** the same cancellation is delivered twice
- **THEN** the second run changes nothing and announces nothing

#### Scenario: Store unavailable
- **WHEN** LotteryEntry.EndEnteredByEvent fails with Unavailable
- **THEN** EndForCancelledEvent fails, the Event stays CANCELLED and the entries are ended when it runs again
