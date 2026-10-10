# Spec Delta

## Purpose

An organizer operator takes one event from draft to the door in the organizer console — publishes it, opens a lottery sale, watches it, and issues the scanners venue staff use — reaching every step by navigation, on a PC or on a phone.

## ADDED Requirements

### Requirement: From draft to the door by navigation

Starting from Home, an operator SHALL be able to reach a draft event of their concert through Concerts and the concert page, publish it after confirming (ConcertAuthoringUseCase.Publish for that event), start a lottery from its Sales tab (TicketSaleUseCase.Create), see the sale on the Sales tab (TicketSaleUseCase.ListOwnByEvent), and issue a scanner from its Reception tab, without typing any address, and Home SHALL stop listing each item once it is resolved.

#### Scenario: Whole flow on a PC

- **WHEN** an operator in a 1280 px window starts at Home, opens the draft item of XX 単独公演, opens its 20 December event, publishes it, creates a lottery named ファンクラブ先行 for 100 tickets at 8000 yen, and issues 受付1
- **THEN** the event is published, the Sales tab lists ファンクラブ先行 with 100 tickets at 8,000円, the Reception tab lists 受付1 as 未使用 with its link, and Home no longer lists the draft item

#### Scenario: Same flow on a phone

- **WHEN** an operator does the same in a 390 px window
- **THEN** every step is reached through the bottom navigation bar, the back links and the tabs, and gives the same result

### Requirement: Nothing irreversible happens without confirmation

Along the flow, publishing the event and revoking a scanner SHALL each happen only after the operator confirms a dialog that names the effect, and each result SHALL be confirmed in the snackbar.

#### Scenario: Publish declined

- **WHEN** the operator presses 公開する on the event and then やめる in the dialog
- **THEN** the event stays draft and no follower is notified

#### Scenario: Scanner revoked

- **WHEN** the operator revokes 受付1 and confirms
- **THEN** 受付1 is 取り消し済み, the snackbar confirms it, and the device that opened 受付1 can no longer admit anyone
