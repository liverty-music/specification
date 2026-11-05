# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Revert only an uncharged resale win`
- TO: `### Requirement: Revert a resale win that issued no tickets`

## MODIFIED Requirements

### Requirement: Revert a resale win that issued no tickets

RevertWin SHALL take a ResaleEntry and a lost reason, "card could not be charged", "payment not completed before the show", "concert cancelled" or "listing cancelled" (a win whose charge was refunded because a listing allocated to it was cancelled), and, in one indivisible step, make a Won entry whose Order is Pending Lost with that lost reason, make its Order Void and make the listings allocated to it that are still Listed free for a draw again. It SHALL change nothing and succeed when the entry is already Lost. It SHALL fail with FailedPrecondition and change nothing when the entry's Order is Paid or Refunded, or when the entry is Entered, Lapsed or Withdrawn, and with NotFound when no entry has the id.

#### Scenario: Win reverted
- **WHEN** RevertWin is called for a Won entry allocated two listings whose Order is Pending
- **THEN** the entry is Lost with the lost reason "card could not be charged", its Order is Void and both listings are free for the next draw

#### Scenario: Already reverted
- **WHEN** RevertWin is called again for the same entry
- **THEN** it succeeds and nothing changes

#### Scenario: Win already issued
- **WHEN** the Won entry's Order is Paid
- **THEN** RevertWin fails with FailedPrecondition and nothing changes

#### Scenario: Unknown entry
- **WHEN** no entry has the id
- **THEN** RevertWin fails with NotFound

#### Scenario: Listing cancelled
- **WHEN** RevertWin is called with the lost reason "listing cancelled" for a Won entry allocated two listings, one of them Cancelled, whose Order is Pending
- **THEN** the entry is Lost with the lost reason "listing cancelled", its Order is Void, the Listed listing is free for the next draw and the Cancelled one stays Cancelled
