# stories/attribute-a-purchase-to-a-referral-link Specification

## Purpose
A fan opens an event link that carries a referral code, signs up if needed and buys tickets or enters the lottery within 7 days, and the Organizer sees the paid purchase counted under that code on the event's Sales tab.

```mermaid
usecase-beta
direction LR
actor Fan("fan")
actor Member("member")
actor Member("member")
systemBoundary "Liverty Music"
  Goal("Attribute a purchase to a referral link")
  TicketSaleUseCaseCreate("TicketSaleUseCase.Create")
  CheckoutUseCaseStart("CheckoutUseCase.Start")
  CheckoutUseCaseAuthorizeCard("CheckoutUseCase.AuthorizeCard")
  OrderUseCaseIssueFromCheckout("OrderUseCase.IssueFromCheckout")
  TicketSaleUseCaseListOwnByEvent("TicketSaleUseCase.ListOwnByEvent")
end
Fan --> Goal
Goal ..> : include TicketSaleUseCaseCreate
Goal ..> : include CheckoutUseCaseStart
Goal ..> : include CheckoutUseCaseAuthorizeCard
Goal ..> : include OrderUseCaseIssueFromCheckout
Goal ..> : include TicketSaleUseCaseListOwnByEvent
Member --> TicketSaleUseCaseCreate
Member --> TicketSaleUseCaseListOwnByEvent
```

## Requirements

### Requirement: A purchase counts for the link the fan came from

After an Organizer creates a FirstCome TicketSale for a published event of a PUBLIC Series with TicketSaleUseCase.Create, a fan who opens `/events/<id>?ref=<code>` for an event of that Series SHALL be able to sign up from the Event page and buy with CheckoutUseCase.Start, CheckoutUseCase.AuthorizeCard and OrderUseCase.IssueFromCheckout within 7 days, and the Order SHALL then be counted under that code by TicketSaleUseCase.ListOwnByEvent for the event. A lottery entry authorized the same way SHALL be counted under its code once it won and its Order was created.

#### Scenario: Guest from a member's link buys after signing up
- **WHEN** a guest opens `/events/<id>?ref=member-a`, signs up from the Event page and buys 2 tickets of 3000 yen
- **THEN** the Organizer's Sales tab for the event lists member-a with 1件 2枚 6,000円

#### Scenario: Last link wins
- **WHEN** a fan opens a link with `ref=member-a`, then a link with `ref=member-b` for the same Series, and buys
- **THEN** the purchase is counted under member-b only

#### Scenario: Another tour is not attributed
- **WHEN** a fan opens a link with `ref=member-a` for one Series and buys tickets for an event of another Series
- **THEN** the purchase is counted as 直接（コードなし）

#### Scenario: Link older than 7 days
- **WHEN** a fan opens a link with `ref=member-a` and buys 8 days later
- **THEN** the purchase is counted as 直接（コードなし）
