# Spec Delta

## ADDED Requirements

### Requirement: Issue a won resale entry

When the Order's source is a Won ResaleEntry, Issue SHALL charge the Order's card authorization once and then, in one indivisible step: make the Order Paid; void the Ticket of each listing allocated to the entry and make each listing Sold; issue a new Ticket for the fan for each listing; and record the Settlements as for a resale purchase today, so the Organizer is paid once per seat. When the card authorization can no longer be charged, or the charge has not succeeded by the event's start time (the payment provider stayed unreachable), Issue SHALL make the entry Lost and its Order Void, so its listings are free again, and charge nothing; no fan is charged for an event that has begun. The entry's card authorization is then released and the fan told, as for an entry Lost at a draw. The listing fans' refunds then follow as for any Sold listing.

#### Scenario: Won entry issued
- **WHEN** a Won entry for 2 tickets of 5000 yen, allocated two listings of two fans, is issued
- **THEN** the fan is charged 10000 yen and holds 2 new Issued Tickets, both listed Tickets are Voided and both listings Sold

#### Scenario: Card can no longer be charged
- **WHEN** the Won entry's card authorization was cancelled by the card issuer
- **THEN** the entry is Lost, its Order Void, nothing is charged and both listings are free for the next draw

#### Scenario: Provider unreachable until the show
- **WHEN** a Won entry's charge keeps failing with Unavailable until the event's start time
- **THEN** Issue stops trying, the entry is Lost, its Order Void, nothing is charged and the card authorization is released
