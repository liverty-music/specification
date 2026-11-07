# components/usecase/notification/send-order-refunded Specification

## Purpose
NotificationUseCase.SendOrderRefunded tells the fan of an Order refunded for 中止 (cancellation) how much was refunded and to which card: an email, and a push notification that opens the Order.

## Requirements

### Requirement: The refund notice once per refunded order

SendOrderRefunded SHALL run for each Order announced as refunded by Order.CommitRefund, once per Order: a run again for the same Order, after a stop or a repeated announcement, sends no second email and no second push. It SHALL read the Order with Order.Get and SHALL send nothing when its refund reason is Dispute. For the reason Cancellation it SHALL read:
- the Order's user with User.Get and its event with Order.GetEventID;
- the event's concert with Concert.ListByIDs.

The number of tickets refunded SHALL be derived from the Order alone: its refund amount divided by its price per ticket (its amount divided by its ticket count). The rest of its ticket count were resold through official resale (公式リセール) before the refund. The Tickets are not read, because the refund Voided them all.

It SHALL send, with Order.SendRefundEmail to the user's email address and in the user's preferred language (Japanese when none), a message stating:
- the concert's title, date and venue, and that it was 中止 (cancelled);
- the refund amount, 税込 (tax-inclusive), and the number of tickets refunded;
- that the refund went to the card with the Order's card brand and last four digits, and that when it appears on the statement depends on the card issuer;
- when fewer tickets were refunded than the Order's ticket count, that the resold tickets were already refunded at their sale;
- that the refunded tickets are no longer valid for entry.

When every Ticket of the Order was resold, so the refund amount is 0, it SHALL send nothing.

After the email is sent, it SHALL start NotificationUseCase.Deliver for the user with a notification of type order_refunded, named after the type and the Order, saying in the user's language that the price was refunded, with the amount, and opening the Order when tapped. A user with no registered browser receives the email only. When Order.Get fails with NotFound, SendOrderRefunded SHALL send nothing and finish. When reading or sending fails otherwise, it SHALL fail and run again.

#### Scenario: Refund email
- **WHEN** a 6000 yen Order of 2 tickets paid with a VISA card ending in 1234 is announced refunded with the reason Cancellation and the amount 6000 yen
- **THEN** the fan receives one email with the concert, 2 tickets, 6000 yen 税込, the card VISA ending in 1234 and that the tickets are no longer valid

#### Scenario: One ticket resold
- **WHEN** an Order of 2 tickets, one resold, is announced refunded for Cancellation with the amount 3000 yen
- **THEN** the email states 1 ticket and 3000 yen, and that the resold ticket was already refunded

#### Scenario: Every ticket resold
- **WHEN** an Order is announced refunded for Cancellation with the amount 0 because every ticket was resold
- **THEN** nothing is sent

#### Scenario: Dispute
- **WHEN** an Order is announced refunded with the reason Dispute
- **THEN** nothing is sent

#### Scenario: Fan allowed notifications
- **WHEN** the Order's user has a registered browser
- **THEN** an order_refunded notification is pushed and opens the Order

#### Scenario: Refund announced twice
- **WHEN** the same announcement is delivered twice
- **THEN** the fan receives one email and one push

#### Scenario: Event deleted before the notice
- **WHEN** Order.Get fails with NotFound because the Event was deleted with its Orders
- **THEN** nothing is sent and the notice is finished

#### Scenario: Mail unavailable
- **WHEN** Order.SendRefundEmail fails with Unavailable
- **THEN** SendOrderRefunded fails and the email is sent when it runs again
