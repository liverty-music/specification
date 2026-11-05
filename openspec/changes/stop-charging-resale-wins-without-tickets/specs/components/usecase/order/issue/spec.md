# Spec Delta

## MODIFIED Requirements

### Requirement: Issue a won resale entry

When the Order's source is a Won ResaleEntry, Issue SHALL first check that the entry's event is still PUBLISHED; when it is not, as for a 中止 (cancelled) concert, Issue SHALL charge nothing and make the entry Lost and its Order Void with ResaleEntry.RevertWin, with the lost reason "concert cancelled", and the card authorization is then released and the fan told from that announcement. Otherwise Issue SHALL charge the Order's card authorization once and then, in one indivisible step: make the Order Paid; void the Ticket of each listing allocated to the entry and make each listing Sold; issue a new Ticket for the fan for each listing; and record the Settlements as for a resale purchase today, so the Organizer is paid once per seat. The listing fans' refunds then follow as for any Sold listing. When the card authorization can no longer be charged, Issue SHALL make the entry Lost and its Order Void with ResaleEntry.RevertWin, with the lost reason "card could not be charged", which announces the entry, so its listings are free again, and charge nothing; the card authorization is then released and the fan told from that announcement, as for an entry Lost at a draw. When the charge has not succeeded by the event's start time because the payment provider stayed unreachable, Issue SHALL stop charging and cancel the card authorization with CardAuthorization.Release:
- when the release succeeds, nothing was charged, and Issue SHALL make the entry Lost with ResaleEntry.RevertWin, with the lost reason "payment not completed before the show"; the fan is told from that announcement, and the card authorization is not released a second time;
- when the release fails with FailedPrecondition because the card authorization was charged, an earlier attempt did charge the card, and Issue SHALL read the captured payment and issue the Order as after a successful charge;
- while the payment provider cannot be reached, Issue SHALL keep the entry Won, try the release again, and an admin SHALL be told.
When that indivisible step finds a listing allocated to the entry Cancelled, because the Order of the fan who listed it was refunded after the draw (an admin's refund for a cancelled concert, or a dispute), it SHALL change nothing, and Issue SHALL refund the whole charge with Order.CreateRefund for the Order's own refund and then make the entry Lost and its Order Void with ResaleEntry.RevertWin, with the lost reason "listing cancelled"; the fan is told from that announcement, and no card authorization is released for it. When the refund fails with Unavailable, Issue SHALL try it again, keeping the entry Won, and an admin SHALL be told when it has not succeeded in 24 hours. Issue SHALL never make the entry Lost while the outcome of a charge is unknown, or while a charge it made is not refunded, so no fan is charged without tickets.

#### Scenario: Won entry issued
- **WHEN** a Won entry for 2 tickets of 5000 yen, allocated two listings of two fans, is issued
- **THEN** the fan is charged 10000 yen and holds 2 new Issued Tickets, both listed Tickets are Voided and both listings Sold

#### Scenario: Card can no longer be charged
- **WHEN** the Won entry's card authorization was cancelled by the card issuer
- **THEN** the entry is Lost, its Order Void, nothing is charged and both listings are free for the next draw

#### Scenario: Provider unreachable until the show
- **WHEN** a Won entry's charge keeps failing with Unavailable until the event's start time
- **THEN** Issue stops charging, releases the card authorization, and once the payment provider confirms the release the entry is Lost with the lost reason "payment not completed before the show", its Order Void and nothing is charged

#### Scenario: Outcome unknown at the show
- **WHEN** at the event's start time the last charge attempt ended with Unavailable and the payment provider still cannot be reached
- **THEN** the entry stays Won, Issue keeps trying the release, an admin is told, and the entry is made Lost only after the provider confirms nothing was charged

#### Scenario: Charged before the show after all
- **WHEN** at the event's start time the release fails with FailedPrecondition because a capture that ended with Unavailable did charge the card
- **THEN** Issue reads the captured payment and issues the Order, and the fan holds the tickets they paid for

#### Scenario: Concert cancelled before the charge
- **WHEN** a Won entry is issued after its concert was cancelled
- **THEN** nothing is charged, the entry is Lost with the lost reason "concert cancelled", its Order Void, and its card authorization is released

#### Scenario: Listing cancelled after the charge
- **WHEN** a Won entry for 1 ticket of 5000 yen was charged and, before its tickets were issued, the Order of the fan who listed its ticket was refunded
- **THEN** 5000 yen is refunded to the fan, the entry is Lost with the lost reason "listing cancelled", its Order Void, no Ticket is issued and the listed Ticket stays Voided
