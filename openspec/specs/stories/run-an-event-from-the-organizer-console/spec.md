# stories/run-an-event-from-the-organizer-console Specification

## Purpose
A member of an Organizer takes one event from draft to the door in the organizer console — adds a seat type, publishes it, stocks the seat type, opens a lottery sale, watches it, and issues the scanners venue staff use — reaching every step by navigation, on a PC or on a phone.

```mermaid
usecase-beta
direction LR
actor Member("member")
systemBoundary "Liverty Music"
  Goal("Run an event from the organizer console")
  SeatTypeUseCaseCreate("SeatTypeUseCase.Create")
  SeriesUseCasePublish("SeriesUseCase.Publish")
  TicketStockUseCaseCreate("TicketStockUseCase.Create")
  TicketSaleUseCaseCreate("TicketSaleUseCase.Create")
  TicketSaleUseCaseListOwnByEvent("TicketSaleUseCase.ListOwnByEvent")
  ScannerUseCaseCreate("ScannerUseCase.Create")
end
Member --> Goal
Goal ..> : include SeatTypeUseCaseCreate
Goal ..> : include SeriesUseCasePublish
Goal ..> : include TicketStockUseCaseCreate
Goal ..> : include TicketSaleUseCaseCreate
Goal ..> : include TicketSaleUseCaseListOwnByEvent
Goal ..> : include ScannerUseCaseCreate
```

## Requirements

### Requirement: From draft to the door by navigation

Starting from Home, a member SHALL be able to reach a draft event of their concert through Concerts and the concert page, add a seat type on the concert page (SeatTypeUseCase.Create), publish the event after confirming (SeriesUseCase.Publish for that event), stock the seat type for it on its Sales tab (TicketStockUseCase.Create), start a lottery from its Sales tab (TicketSaleUseCase.Create), see the sale on the Sales tab (TicketSaleUseCase.ListOwnByEvent), and issue a scanner from its Reception tab, without typing any address, and Home SHALL stop listing each item once it is resolved.

#### Scenario: Whole flow on a PC

- **WHEN** a member in a 1280 px window starts at Home, opens the draft item of XX 単独公演, adds the seat type S席 at 8000 yen, opens its 20 December event, publishes it, stocks 100 S席 tickets, creates a lottery named ファンクラブ先行, and issues 受付1
- **THEN** the event is published, the Sales tab shows S席 8,000円 100枚 and lists ファンクラブ先行, the Reception tab lists 受付1 as 未使用 with its link, and Home no longer lists the draft item

#### Scenario: Same flow on a phone

- **WHEN** a member does the same in a 390 px window
- **THEN** every step is reached through the bottom navigation bar, the back links and the tabs, and gives the same result

### Requirement: Nothing irreversible happens without confirmation

Along the flow, publishing the event, adding a seat type, stocking it and revoking a scanner SHALL each happen only after the member confirms a dialog that names the effect, and each result SHALL be confirmed in the snackbar.

#### Scenario: Publish declined

- **WHEN** the member presses 公開する on the event and then やめる in the dialog
- **THEN** the event stays draft and no follower is notified

#### Scenario: Seat type confirmed as fixed

- **WHEN** the member adds S席 at 8000 yen
- **THEN** the dialog says the name and price cannot be changed afterwards, and after confirming the snackbar confirms it

#### Scenario: Scanner revoked

- **WHEN** the member revokes 受付1 and confirms
- **THEN** 受付1 is 取り消し済み, the snackbar confirms it, and the device that opened 受付1 can no longer admit anyone
