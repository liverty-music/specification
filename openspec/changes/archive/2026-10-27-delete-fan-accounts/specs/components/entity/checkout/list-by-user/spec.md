## Purpose

Lists every Checkout one User has started, so a caller can tell whether a purchase of theirs is still in progress.

## ADDED Requirements

### Requirement: Checkouts of one user

ListByUser SHALL return every Checkout whose user is the given User, in every status and for every TicketType, newest first, and no Checkout of another User. It SHALL return an empty list when there is none.

#### Scenario: Two checkouts

- **WHEN** the User has a Completed Checkout from last month and a Held Checkout started a minute ago, and another User has a Checkout
- **THEN** both of the User's Checkouts are returned, the Held one first, and the other User's is not

#### Scenario: Never checked out

- **WHEN** the User has no Checkout
- **THEN** an empty list is returned
