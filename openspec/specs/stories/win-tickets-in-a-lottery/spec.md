# Win Tickets In A Lottery

## Purpose

A fan authorizes their card for a number of tickets and confirms the entry, the draw runs after the window closes, and a winning fan is charged and receives account-bound covered tickets while a losing fan is never charged; every fan is told the result.

```mermaid
usecase-beta
direction LR
actor Fan("fan")
actor Member("member")
systemBoundary "Liverty Music"
  Goal("Win tickets in a lottery")
  SeatTypeUseCaseCreate("SeatTypeUseCase.Create")
  TicketStockUseCaseCreate("TicketStockUseCase.Create")
  TicketSaleUseCaseCreate("TicketSaleUseCase.Create")
  LotteryEntryUseCaseAuthorizeCard("LotteryEntryUseCase.AuthorizeCard")
  LotteryEntryUseCaseConfirm("LotteryEntryUseCase.Confirm")
  LotteryEntryUseCaseListByTicketType("LotteryEntryUseCase.ListByTicketType")
  LotteryEntryUseCaseDrawDueSales("LotteryEntryUseCase.DrawDueSales")
  LotteryEntryUseCaseDraw("LotteryEntryUseCase.Draw")
  OrderUseCaseIssue("OrderUseCase.Issue")
  LotteryEntryUseCaseReleaseCardAuthorization("LotteryEntryUseCase.ReleaseCardAuthorization")
  NotificationUseCaseSendLotteryLoss("NotificationUseCase.SendLotteryLoss")
  TicketUseCaseList("TicketUseCase.List")
  SettlementUseCaseReleaseDueSettlements("SettlementUseCase.ReleaseDueSettlements")
end
Fan --> Goal
Goal ..> : include SeatTypeUseCaseCreate
Goal ..> : include TicketStockUseCaseCreate
Goal ..> : include TicketSaleUseCaseCreate
Goal ..> : include LotteryEntryUseCaseAuthorizeCard
Goal ..> : include LotteryEntryUseCaseConfirm
Goal ..> : include LotteryEntryUseCaseListByTicketType
Goal ..> : include LotteryEntryUseCaseDrawDueSales
Goal ..> : include LotteryEntryUseCaseDraw
Goal ..> : include OrderUseCaseIssue
Goal ..> : include LotteryEntryUseCaseReleaseCardAuthorization
Goal ..> : include NotificationUseCaseSendLotteryLoss
Goal ..> : include TicketUseCaseList
Goal ..> : include SettlementUseCaseReleaseDueSettlements
Member --> SeatTypeUseCaseCreate
Member --> TicketStockUseCaseCreate
Member --> TicketSaleUseCaseCreate
```

## Requirements

### Requirement: The Organizer's payout readiness never blocks the sale

Fans SHALL be able to enter, win and receive tickets for an Organizer's lottery whatever the state of the Organizer's payout account; only the Organizer's payout waits until the account is Active, as SettlementUseCase.ReleaseDueSettlements states.

#### Scenario: Organizer still in identity check
- **WHEN** an Organizer whose payout account is Pending runs a lottery and a fan's entry wins
- **THEN** the fan is charged and holds Issued Tickets, while the Organizer's payout stays Held until the account is Active

### Requirement: A winning fan receives tickets

After an Organizer creates a Lottery TicketSale for a published event with TicketSaleUseCase.Create, a fan SHALL be able to authorize their card for a ticket count of the event's TicketType with LotteryEntryUseCase.AuthorizeCard, complete card authentication and confirm the entry with LotteryEntryUseCase.Confirm while the window is open, and — when their entry wins — find it Won with LotteryEntryUseCase.ListByTicketType within 2 minutes after the window closes and find its Tickets with TicketUseCase.List within 1 more minute.

#### Scenario: Demand within quantity
- **WHEN** a fan enters 2 tickets for a TicketType of 100 tickets priced 8000 yen, and the window closes with fewer than 100 tickets requested
- **THEN** within 2 minutes the fan's entry is Won and 16000 yen is charged, and within 1 more minute the fan holds 2 Issued Tickets for the event, their faces show the fan's full name and phone number, and their ticket journey for the event is Paid

### Requirement: A losing fan is never charged

A fan whose entry is not admitted SHALL find it Lost with LotteryEntryUseCase.ListByTicketType and SHALL NOT be charged.

#### Scenario: Oversubscribed sale
- **WHEN** a TicketType of 4 tickets closes with entries for 12 tickets and the fan's entry is not admitted
- **THEN** the fan's entry is Lost, its card authorization is released, and the fan holds no Ticket for the event

### Requirement: A presale and a general sale share the per-account limit

When an event has a presale and a later general sale, a fan who won tickets in the presale SHALL be able to enter the general sale only for the tickets still under the general sale's per-account limit.

#### Scenario: Presale winner at the limit
- **WHEN** a fan won 4 tickets in an event's presale and the event's general sale has a per-account limit of 4
- **THEN** the fan's entry into the general sale is refused and the fan still holds 4 Tickets

#### Scenario: Presale winner below the limit
- **WHEN** a fan won 2 tickets in the presale and enters 2 tickets in a general sale with a per-account limit of 4
- **THEN** the entry is made

### Requirement: An entry is made once the card is authenticated

A fan SHALL have an entry only after completing card authentication for it, and SHALL have it then even if the browser closes before the fan's confirmation reaches the platform. A card authorization for a count the fan left before authenticating SHALL hold nothing and make no entry. Only an entry made before the window closes takes part: an authentication whose entry would be made after the end time SHALL be released instead.

#### Scenario: Count changed before confirming
- **WHEN** a fan authorizes their card for 2 tickets, goes back, authorizes it for 3 tickets, completes card authentication and confirms
- **THEN** the fan has one Entered entry, for 3 tickets, and nothing is held on the card for 2 tickets

#### Scenario: Browser closed after card authentication
- **WHEN** a fan completes card authentication and the browser closes before the confirmation reaches the platform
- **THEN** the fan's entry is Entered and takes part in the draw

#### Scenario: Entry made only after the window closed
- **WHEN** a fan completes card authentication 10 seconds before the end time, and neither the fan's confirmation nor the payment provider's notice reaches the platform before the end time
- **THEN** the fan has no entry, the card authorization is released and the fan is never charged

#### Scenario: Card authentication abandoned
- **WHEN** a fan authorizes their card but leaves without completing card authentication, and the window closes
- **THEN** the fan has no entry and is never charged
