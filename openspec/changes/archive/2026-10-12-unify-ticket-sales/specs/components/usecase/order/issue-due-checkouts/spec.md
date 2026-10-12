# Spec Delta

## Purpose

OrderUseCase.IssueDueCheckouts finishes Checkouts whose tickets were committed but whose charge or issuance did not complete, and reports charged Checkouts that stay unissued.

## ADDED Requirements

### Requirement: Stalled checkouts finished within one minute

IssueDueCheckouts SHALL run every 1 minute. For each Committed Checkout returned by Checkout.ListDue, it SHALL run OrderUseCase.IssueFromCheckout without a calling fan. A Checkout whose issuance fails SHALL NOT stop the others and is tried again on the next run, until it is Completed or, if it was never charged, Released. When the listing fails, IssueDueCheckouts SHALL fail with that error and issue nothing.

#### Scenario: Capture interrupted
- **WHEN** a Checkout's tickets were committed at 18:20 and the charge did not complete
- **THEN** by 18:22 the card is charged once and the Order and Tickets are issued

#### Scenario: Charged but not issued
- **WHEN** a Checkout was charged at 18:20 and its Order was not stored
- **THEN** by 18:22 the Order and Tickets are issued and the card is not charged again

#### Scenario: One checkout fails
- **WHEN** issuance of one Checkout fails
- **THEN** the other Checkouts are still issued and the failed one is tried again 1 minute later

### Requirement: A charged checkout left unissued is reported

When a Committed Checkout has a capture time more than 10 minutes before the run and is still not Completed, IssueDueCheckouts SHALL report it, with its id and provider payment ID, as needing an operator on every run, while still trying to issue it.

#### Scenario: Organizer record broken
- **WHEN** a Checkout was charged at 18:20 and its issuance keeps failing
- **THEN** from 18:31 every run reports it as needing an operator and tries again
