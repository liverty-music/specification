## Purpose

Lets the listing's user pull back a listed ticket before it is offered to another user, returning it to ordinary ownership at no charge, while protecting an in-flight offer or a completed match from being undone by a late withdrawal.

## ADDED Requirements

### Requirement: Withdraw a listing

The system SHALL allow the listing's user to **withdraw** their listing **only while it is
in `LISTED` state** (not while an offer is in flight or after a match), returning
the ticket to normal OWNED state with no fee charged. While a seat is `OFFERED` to
a candidate the listing is locked and MUST NOT be withdrawable — this resolves the
withdraw-vs-purchase race in favor of the in-flight offer.

#### Scenario: Listing user withdraws while LISTED

- **WHEN** the listing's user withdraws a listing that is in LISTED state with no offer in flight
- **THEN** the listing moves to WITHDRAWN, the ticket returns to OWNED, and no fee is charged

#### Scenario: Withdrawal is rejected while an offer is in flight or after match

- **WHEN** the listing's user attempts to withdraw a listing that is OFFERED to a candidate or already SOLD
- **THEN** the system rejects the withdrawal (the offer/match takes precedence)
