# Spec Delta

## Purpose

Withdraws one Entered ResaleEntry at its fan's request, so it takes part in no later draw and its Order is Void.

## ADDED Requirements

### Requirement: Withdraw an entered entry

Withdraw SHALL take a ResaleEntry and a time, and in one indivisible step make the entry Withdrawn with that withdraw time and make its Order Void, and return the entry. It SHALL fail with NotFound when the entry does not exist, and with FailedPrecondition, changing nothing, when the entry is not Entered at the moment it runs, including an entry that a draw running at the same moment has already recorded as Won, Lost or Lapsed. A draw that runs after Withdraw SHALL find the entry no longer Entered.

#### Scenario: Entry withdrawn
- **WHEN** an Entered entry is withdrawn at 10:00
- **THEN** it is Withdrawn with the withdraw time 10:00 and its Order is Void

#### Scenario: Draw recorded first
- **WHEN** the 12:00 draw records the entry as Won and Withdraw runs at the same moment
- **THEN** Withdraw fails with FailedPrecondition and the entry stays Won

#### Scenario: Withdrawn first
- **WHEN** Withdraw runs just before the 12:00 draw records its outcome
- **THEN** the entry is Withdrawn and the draw allocates it no listing

#### Scenario: Unknown entry
- **WHEN** Withdraw is called for an entry that does not exist
- **THEN** it fails with NotFound

### Requirement: A withdrawn entry is announced with the change

When Withdraw makes an entry Withdrawn, it SHALL announce the entry, as it is after the change, together with the change: both are stored or neither is. When Withdraw fails it SHALL announce nothing. When the announcement cannot be recorded, Withdraw SHALL fail with Unavailable, and the entry SHALL stay Entered and its Order Pending.

#### Scenario: Withdrawal announced
- **WHEN** an Entered entry is withdrawn
- **THEN** one withdrawal is announced, carrying the entry as Withdrawn

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement of a withdrawal cannot be recorded
- **THEN** Withdraw fails with Unavailable, the entry stays Entered and its Order stays Pending
