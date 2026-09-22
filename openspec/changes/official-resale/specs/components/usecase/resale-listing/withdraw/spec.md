## Purpose

Lets a seller pull back a listed ticket before it is offered to a buyer, returning it to ordinary ownership at no charge, while protecting an in-flight offer or a completed match from being undone by a late withdrawal.

## ADDED Requirements

### Requirement: Withdraw a listing

The system SHALL allow the seller to **withdraw** their listing **only while it is
in `LISTED` state** (not while an offer is in flight or after a match), returning
the ticket to normal OWNED state with no fee charged. While a seat is `OFFERED` to
a candidate the listing is locked and MUST NOT be withdrawable — this resolves the
withdraw-vs-purchase race in favor of the in-flight offer.

#### Scenario: Seller withdraws while LISTED

- **WHEN** the seller withdraws a listing that is in LISTED state with no offer in flight
- **THEN** the listing moves to WITHDRAWN, the ticket returns to OWNED, and no fee is charged

#### Scenario: Withdrawal is rejected while an offer is in flight or after match

- **WHEN** the seller attempts to withdraw a listing that is OFFERED to a candidate or already SOLD
- **THEN** the system rejects the withdrawal (the offer/match takes precedence)
