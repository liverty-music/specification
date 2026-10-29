# Spec Delta

## ADDED Requirements

### Requirement: Issue a won resale entry

When the Order's source is a Won ResaleEntry, Issue SHALL charge the Order's card authorization once and then, in one indivisible step: make the Order Paid; void the Ticket of each listing allocated to the entry and make each listing Sold; issue a new Ticket for the fan for each listing; and record the Settlements as for a resale purchase today, so the Organizer is paid once per seat. When the card authorization can no longer be charged, Issue SHALL make the entry Lost and its Order Void with ResaleEntry.RevertWin, which announces the entry, so its listings are free again, and charge nothing. When the charge has not succeeded by the event's start time because the payment provider stayed unreachable, Issue SHALL stop charging and cancel the card authorization with CardAuthorization.Release, and make the entry Lost with ResaleEntry.RevertWin only once the payment provider confirms the card authorization was released without a charge; no fan is charged for an event that has begun. While the provider cannot confirm it, Issue SHALL keep the entry Won, try the release again, and an admin SHALL be told; it SHALL never make the entry Lost while the outcome of a charge is unknown. The entry's card authorization is then released and the fan told from that announcement, as for an entry Lost at a draw. The listing fans' refunds then follow as for any Sold listing.

#### Scenario: Won entry issued
- **WHEN** a Won entry for 2 tickets of 5000 yen, allocated two listings of two fans, is issued
- **THEN** the fan is charged 10000 yen and holds 2 new Issued Tickets, both listed Tickets are Voided and both listings Sold

#### Scenario: Card can no longer be charged
- **WHEN** the Won entry's card authorization was cancelled by the card issuer
- **THEN** the entry is Lost, its Order Void, nothing is charged and both listings are free for the next draw

#### Scenario: Provider unreachable until the show
- **WHEN** a Won entry's charge keeps failing with Unavailable until the event's start time
- **THEN** Issue stops charging, releases the card authorization, and once the payment provider confirms the release the entry is Lost, its Order Void and nothing is charged

#### Scenario: Outcome unknown at the show
- **WHEN** at the event's start time the last charge attempt ended with Unavailable and the payment provider still cannot be reached
- **THEN** the entry stays Won, Issue keeps trying the release, an admin is told, and the entry is made Lost only after the provider confirms nothing was charged

## MODIFIED Requirements

### Requirement: Every Won entry is issued

Issue SHALL run once for each entry that LotteryEntry.PersistDrawOutcome records Won, once for each entry that ResaleEntry.PersistDrawOutcome records Won, and once for each Checkout whose order OrderUseCase.Place places. When Issue stops before it ends, it SHALL resume from the step it reached, without charging the card again. When it has not ended 24 hours after it started, it SHALL stop, leaving the entry or the Checkout and its Order as they are, and an admin SHALL be told.

#### Scenario: Won entry
- **WHEN** a draw records an entry Won
- **THEN** Issue runs for it

#### Scenario: Won resale entry
- **WHEN** a resale draw records an entry Won
- **THEN** Issue runs for its Order once

#### Scenario: Stopped after the charge
- **WHEN** Issue stops after the card was charged and before the Order was made Paid
- **THEN** it resumes, the card is charged once, and the Order becomes Paid once

#### Scenario: Placed checkout
- **WHEN** a fan places the order for their Checkout twice
- **THEN** Issue runs once for the Checkout

