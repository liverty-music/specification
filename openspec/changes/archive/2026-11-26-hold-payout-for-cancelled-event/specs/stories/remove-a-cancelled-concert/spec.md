## ADDED Requirements

### Requirement: A cancelled concert is never paid out

After a member cancels an Event with SeriesUseCase.Cancel, a run of SettlementUseCase.ReleaseDueSettlements that starts after the cancellation SHALL pay the Organizer nothing for that Event's Orders, however long after the event's start it runs and whether or not an admin has refunded them. A Settlement of the Event that is Held stays Held until its Order is refunded, as by `Refund all`, which makes it Reversed.

#### Scenario: Release date passes before the refunds

- **WHEN** a member cancels an Event with two Paid Orders of an Organizer whose payout account is Active, and the release runs 8 days after the event's start before any refund
- **THEN** nothing is paid to the Organizer and both Settlements stay Held

#### Scenario: Refunded after the release date

- **WHEN** the release has run 8 days after the start of a cancelled Event with two Paid Orders, and an admin then uses `Refund all` on the Artist concerts screen
- **THEN** both Orders are Refunded, both Settlements are Reversed and no payout was made or reversed
