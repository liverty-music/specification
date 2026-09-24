# Win Tickets In A Lottery

## Purpose

A fan applies to an Organizer's lottery with a card hold, the draw runs after the window closes, and a winning fan is charged and receives account-bound covered tickets while a losing fan is never charged.

## Requirements

### Requirement: Winning fan receives tickets

After an Organizer configures a LotterySalesPhase for a published event with LotteryUseCase.ConfigureLotteryPhase, a fan SHALL be able to open a hold with LotteryUseCase.CreateAuthorization, complete card authentication, apply with LotteryUseCase.Apply while the window is open, and — when their application wins — find it Won with LotteryUseCase.GetResult within 1 minute after the window closes and find its Tickets with TicketUseCase.GetMyTickets within 1 more minute.

#### Scenario: Demand within capacity

- **WHEN** a fan applies for 2 tickets to a phase with capacity 100 priced 8000 yen, and the window closes with fewer than 100 tickets requested
- **THEN** within 1 minute the fan's application is Won and 16000 yen is charged, and within 1 more minute the fan holds 2 Issued Tickets for the event and their ticket journey for the event is Paid

### Requirement: Losing fan is never charged

A fan whose application is not admitted SHALL find it Lost with LotteryUseCase.GetResult and SHALL NOT be charged.

#### Scenario: Oversubscribed phase

- **WHEN** a phase with capacity 4 closes with applications for 12 tickets and the fan's application is not admitted
- **THEN** the fan's application is Lost, its hold is released, and the fan holds no Ticket for the event

### Requirement: Withdrawing before the draw

A fan SHALL be able to withdraw with LotteryUseCase.WithdrawApplication before the draw and apply again while the window is open.

#### Scenario: Withdraw and re-apply

- **WHEN** a fan withdraws their application while the window is open and applies again with a new hold
- **THEN** the first hold is released and only the new application takes part in the draw
