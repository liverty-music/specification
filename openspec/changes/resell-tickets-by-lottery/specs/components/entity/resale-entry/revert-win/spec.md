# Spec Delta

## Purpose

Makes a Won ResaleEntry Lost, and its Pending Order Void, when its Order cannot be charged, so the listings allocated to it are free for the next draw.

## ADDED Requirements

### Requirement: Revert only an uncharged resale win

RevertWin SHALL take a ResaleEntry and, in one indivisible step, make a Won entry whose Order is Pending Lost with the lost reason "card could not be charged", make its Order Void and make the listings allocated to it free for a draw again. It SHALL change nothing and succeed when the entry is already Lost. It SHALL fail with FailedPrecondition and change nothing when the entry's Order is Paid or Refunded, or when the entry is Entered, Lapsed or Withdrawn, and with NotFound when no entry has the id.

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

### Requirement: A reverted resale win is announced with the change

When RevertWin makes an entry Lost, it SHALL announce the entry, as it is after the change, together with the change: both are stored or neither is. When it changes nothing it SHALL announce nothing. When the announcement cannot be recorded, RevertWin SHALL fail with Unavailable and change nothing.

#### Scenario: Win reverted and announced
- **WHEN** RevertWin makes a Won entry Lost
- **THEN** one resale entry result is announced, carrying the entry as Lost

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement of a reverted win cannot be recorded
- **THEN** RevertWin fails with Unavailable, the entry stays Won and its Order stays Pending
