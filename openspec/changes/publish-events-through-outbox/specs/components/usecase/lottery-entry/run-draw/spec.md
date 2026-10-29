## MODIFIED Requirements

### Requirement: Capture failure

When a winner's capture fails, RunDraw SHALL release that entry's card authorization, record it Lost with its draw position and the lost reason "card could not be charged" so it joins the losers, and leave its tickets unallocated; no loser is promoted (no 繰上げ, promotion of a loser). Every other loser's lost reason is "not drawn".

#### Scenario: Winner's card was closed
- **WHEN** CardAuthorization.Capture fails for a winner
- **THEN** its card authorization is released, it is Lost with its draw position and the lost reason "card could not be charged", and its tickets stay unallocated

## REMOVED Requirements

### Requirement: Each entry's result is reported
**Reason**: LotteryEntry.PersistDrawOutcome announces each drawn entry together with the outcome (components/entity/lottery-entry/persist-draw-outcome), so RunDraw sends no signal and a lost signal can no longer be missed.
**Migration**: Product analytics records the "lottery result" signal from that announcement: the entry with its TicketSale, TicketType, state and lost reason, at the time of the draw (the TicketSale's draw time).
