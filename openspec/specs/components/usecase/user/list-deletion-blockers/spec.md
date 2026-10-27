# components/usecase/user/list-deletion-blockers Specification

## Purpose
Tells a fan or an admin what currently stops a User from being deleted, so the withdrawal and admin screens can show it before anyone commits, and UserUseCase.Delete applies the same rule.

## Requirements

### Requirement: Four kinds of blocker

ListDeletionBlockers SHALL load the User through User.Get, failing with NotFound for an unknown User, and SHALL return one blocker for each kind below that the User has, with how many of that kind:

- **Upcoming ticket**: an Issued Ticket (Ticket.ListByUser) whose Event's local date (Event.Get) is today or later in Japan time.
- **Listed resale**: an open ResaleListing (ResaleListing.ListByUser): in status Listed and before its deadline, read from its Event (Event.Get).
- **Pending lottery entry**: a LotteryEntry in state Entered (LotteryEntry.ListByUser).
- **Payment in progress**: a Checkout that is Committed, or Held with its hold expiry not yet passed (Checkout.ListByUser), or a LotteryEntry in state Won that has no Order yet (Order.GetByLotteryEntryID), whose tickets are still being charged.

It SHALL return an empty list when the User has none. A Voided Ticket, an Issued Ticket for an Event whose local date has passed, an Order in any status, a ResaleListing in any other status or expired (Listed at or after its deadline), a Won LotteryEntry that has an Order, a Lost LotteryEntry, a Held Checkout whose hold expiry has passed and a Completed, Expired or Released Checkout SHALL NOT block. A failure of any read SHALL be returned with its own code.

#### Scenario: Ticket for a concert next week

- **WHEN** the User holds two Issued Tickets for an Event a week from today
- **THEN** ListDeletionBlockers returns one Upcoming ticket blocker with count 2

#### Scenario: Ticket for today's concert

- **WHEN** the User holds an Issued Ticket for an Event whose local date is today in Japan time
- **THEN** ListDeletionBlockers returns an Upcoming ticket blocker

#### Scenario: Ticket for a past concert

- **WHEN** the User's only Ticket is Issued for an Event whose local date was yesterday, and its Order is Paid
- **THEN** ListDeletionBlockers returns an empty list

#### Scenario: Listed resale

- **WHEN** the User has a ResaleListing in status Listed
- **THEN** ListDeletionBlockers returns a Listed resale blocker with count 1

#### Scenario: Expired listing

- **WHEN** the User's only ResaleListing is Listed and its deadline passed an hour ago, unsold
- **THEN** ListDeletionBlockers returns an empty list

#### Scenario: Entry awaiting its draw

- **WHEN** the User has a LotteryEntry in state Entered
- **THEN** ListDeletionBlockers returns a Pending lottery entry blocker with count 1

#### Scenario: Card authorized, not yet charged

- **WHEN** the User has a Committed Checkout
- **THEN** ListDeletionBlockers returns a Payment in progress blocker with count 1

#### Scenario: Win being charged

- **WHEN** the User has a LotteryEntry in state Won that has no Order yet
- **THEN** ListDeletionBlockers returns a Payment in progress blocker with count 1

#### Scenario: Win already issued

- **WHEN** the User's only LotteryEntry is Won and has an Order, and its Ticket is for an Event whose local date has passed
- **THEN** ListDeletionBlockers returns an empty list

#### Scenario: Lapsed hold

- **WHEN** the User's only Checkout is Held and its hold expiry passed 10 minutes ago
- **THEN** ListDeletionBlockers returns an empty list

#### Scenario: Finished entries and withdrawn listings

- **WHEN** the User has only a Lost LotteryEntry and a Withdrawn ResaleListing
- **THEN** ListDeletionBlockers returns an empty list

#### Scenario: Unknown user

- **WHEN** no User has the given id
- **THEN** ListDeletionBlockers fails with NotFound
