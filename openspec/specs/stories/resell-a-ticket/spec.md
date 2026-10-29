# stories/resell-a-ticket Specification

## Purpose
A fan who holds tickets of a seat type and cannot attend lists one through official resale (公式リセール) after that seat type sold out for the event, whether the tickets were bought first come or won in a lottery. Another fan applies for resale tickets of the seat type; a daily draw at 12:00 allocates the listed tickets to applications, the winning fan is charged face value and receives new tickets in their own name, and the listing fan is refunded the face value minus the 10% resale fee, while the Organizer is paid once per seat.

```mermaid
usecase-beta
direction LR
actor Fan("listing fan")
actor EnteringFan("fan who applies")
systemBoundary "Liverty Music"
  Goal("Resell a ticket")
  ResaleListingUseCaseCreate("ResaleListingUseCase.Create")
  ResaleListingUseCaseList("ResaleListingUseCase.List")
  ResaleEntryUseCaseAuthorizeCard("ResaleEntryUseCase.AuthorizeCard")
  ResaleEntryUseCaseConfirm("ResaleEntryUseCase.Confirm")
  ResaleEntryUseCaseWithdraw("ResaleEntryUseCase.Withdraw")
  ResaleEntryUseCaseDraw("ResaleEntryUseCase.Draw")
  OrderUseCaseIssue("OrderUseCase.Issue")
  TicketUseCaseList("TicketUseCase.List")
  CheckoutUseCaseStart("CheckoutUseCase.Start")
  CheckoutUseCaseAuthorizeCard("CheckoutUseCase.AuthorizeCard")
  OrderUseCaseIssueFromCheckout("OrderUseCase.IssueFromCheckout")
end
Fan --> Goal
Goal ..> : include ResaleListingUseCaseCreate
Goal ..> : include ResaleListingUseCaseList
Goal ..> : include ResaleEntryUseCaseAuthorizeCard
Goal ..> : include ResaleEntryUseCaseConfirm
Goal ..> : include ResaleEntryUseCaseWithdraw
Goal ..> : include ResaleEntryUseCaseDraw
Goal ..> : include OrderUseCaseIssue
Goal ..> : include TicketUseCaseList
Goal ..> : include CheckoutUseCaseStart
Goal ..> : include CheckoutUseCaseAuthorizeCard
Goal ..> : include OrderUseCaseIssueFromCheckout
EnteringFan --> ResaleEntryUseCaseAuthorizeCard
EnteringFan --> ResaleEntryUseCaseConfirm
EnteringFan --> ResaleEntryUseCaseWithdraw
```

## Requirements

### Requirement: Resale closes when admission opens

No ticket SHALL be listed or bought through official resale once the event's admission window has opened, and a listing that has not sold by then SHALL leave its Ticket valid for entry.

#### Scenario: Unsold at the deadline
- **WHEN** a fan's listing has not sold when the admission window opens
- **THEN** the event page offers no resale and the fan's Ticket is admitted at the venue

### Requirement: A ticket of a sold-out seat type is listed

After a TicketStock sold out, a signed-in fan holding Issued Tickets of it, bought first come or won in a lottery, SHALL be able to list one with ResaleListingUseCase.Create and see it Listed with ResaleListingUseCase.List; the Ticket stays valid for entry while it is listed and not sold. Buying a listed ticket arrives with the change resell-tickets-by-lottery.

#### Scenario: One of two tickets listed
- **WHEN** a fan holding 2 S席 tickets of 5000 yen for an event whose S席 sold out lists one
- **THEN** ResaleListingUseCase.List shows the listing Listed at 5000 yen and both of the fan's Tickets stay 未入場 and valid for entry

#### Scenario: Lottery-won ticket listed
- **WHEN** a fan who won 2 S席 tickets in the event's lottery presale lists one after S席 sold out
- **THEN** the listing is Listed
