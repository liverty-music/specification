# Spec Delta

## MODIFIED Requirements

### Requirement: Start a checkout for a ticket stock

Start SHALL take the calling fan, a TicketStock, a ticket count, an optional ReferralCode and the current time:
- It SHALL read the TicketStock with TicketStock.Get, failing with NotFound when it does not exist.
- It SHALL fail with FailedPrecondition when Event.IsEventPublished reports false for the stock's event, as for a 中止 (cancelled) concert.
- It SHALL read the event's sales with TicketSale.ListByEvent. The Checkout belongs to the FirstCome sale of the event whose window is open at the current time; when there is none, Start SHALL fail with FailedPrecondition.
- It SHALL fail with FailedPrecondition while a Lottery sale of the event has closed and still has Entered entries for the stock, read with LotteryEntry.ListEnteredByTicketSaleAndTicketStock, because that draw has not yet taken its winners' tickets from the stock.
- It SHALL fail with InvalidArgument when the count is below 1 or above the event's per-account limit.
- It SHALL apply the verification gate.
- It SHALL read what the fan holds for the event with Order.GetHeldForEvent, not counting the Order of the fan's own holding Checkout, which is resumed or replaced, and fail with FailedPrecondition when the application does not fit the event.
- It SHALL then call Checkout.GetOrCreateHeld with the sale, the stock, the count and the ReferralCode, and return the Checkout it gives; its failures are returned unchanged.

Starting again with the same count while the hold lasts SHALL resume the same Checkout.

#### Scenario: Fan starts a checkout
- **WHEN** a signed-in fan starts a checkout for 2 S席 tickets of an Available stock while a FirstCome sale of the event is open
- **THEN** a Pending Order and a Checkout holding 2 tickets for 15 minutes are created and the Checkout is returned

#### Scenario: Presale lottery not drawn yet
- **WHEN** a general first-come sale opens at the instant its event's presale lottery closes and a fan starts a checkout before that lottery's entries for the stock are drawn
- **THEN** Start fails with FailedPrecondition and holds nothing

#### Scenario: Fan reloads mid-checkout
- **WHEN** the fan reloads the page and starts again with the same count within the hold
- **THEN** the same Checkout is returned with its original hold expiry

#### Scenario: Sale not open yet
- **WHEN** no FirstCome sale of the event has opened
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Concert cancelled
- **WHEN** the event's concert was cancelled after the sale opened
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Last tickets in other checkouts
- **WHEN** the stock is AllHeld while a FirstCome sale is open
- **THEN** Start fails with ResourceExhausted and nothing is held

#### Scenario: Only a lottery is open
- **WHEN** the only open sale of the event is a Lottery sale
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Count over the limit
- **WHEN** the fan asks for 5 tickets and the event's per-account limit is 4
- **THEN** Start fails with InvalidArgument and nothing is held

#### Scenario: Presale winner over the limit
- **WHEN** the event's per-account limit is 4, the fan won 4 S席 tickets in the presale and starts a checkout for 1 S席
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Another seat type
- **WHEN** the fan holds 2 S席 tickets for the event and starts a checkout for 1 A席
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Changing the count of a holding checkout
- **WHEN** the event's limit is 4, the fan's holding Checkout holds 4 tickets and the fan starts again for 3
- **THEN** the application fits, the holding Checkout is replaced and its Order becomes Void

#### Scenario: Every sale ended
- **WHEN** every sale of the event has ended
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Checkout from a referral link
- **WHEN** a fan starts a checkout for 2 tickets with the code `member-a`
- **THEN** the Checkout's Order has the referral code `member-a`

#### Scenario: Another link before confirming
- **WHEN** the fan's holding Checkout's Order has the code `member-a` and the fan starts again with the same count and the code `member-b`
- **THEN** the same Checkout is returned and its Order keeps `member-a`

#### Scenario: No code
- **WHEN** a fan starts a checkout without a code
- **THEN** the Checkout's Order has no referral code

#### Scenario: Sale not open with a code
- **WHEN** a fan starts a checkout with the code `member-a` while no FirstCome sale is open
- **THEN** Start fails with FailedPrecondition and nothing is stored
