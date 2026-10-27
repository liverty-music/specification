## MODIFIED Requirements

### Requirement: Delete removes the user

Delete SHALL load the User through User.Get, failing with NotFound for an unknown User. It SHALL fail with FailedPrecondition, removing nothing, while UserUseCase.ListDeletionBlockers returns any blocker for the User. Otherwise it SHALL remove the User's sign-in identity through User.DeleteIdentity and then the User through User.Delete; the User's Orders, Tickets, LotteryEntries and ResaleListings remain. A failure of either SHALL be returned as it is; because an identity that is already gone counts as removed, calling Delete again completes a deletion that failed in User.Delete. Delete serves the fan removing their own account and an admin removing a fan's account alike.

#### Scenario: Existing user

- **WHEN** Delete is called with a stored User's id and the User holds no Ticket and no Order
- **THEN** the User's identity is removed and the User no longer exists

#### Scenario: Unknown user

- **WHEN** no User has the given id
- **THEN** Delete fails with NotFound

#### Scenario: User holding a ticket

- **WHEN** the User holds an Issued Ticket for an Event whose local date is today or later in Japan time
- **THEN** Delete fails with FailedPrecondition and the User and its identity remain

#### Scenario: User whose concerts are over

- **WHEN** the User's only Ticket is Issued for an Event whose local date has passed, and its Order is Paid
- **THEN** the User is removed and the Order and Ticket remain

#### Scenario: User with a listed resale

- **WHEN** the User has a ResaleListing in status Listed
- **THEN** Delete fails with FailedPrecondition and the User remains

#### Scenario: User with an entry awaiting its draw

- **WHEN** the User has a LotteryEntry in state Entered
- **THEN** Delete fails with FailedPrecondition and the User remains

#### Scenario: User paying for tickets

- **WHEN** the User has a Committed Checkout
- **THEN** Delete fails with FailedPrecondition and the User remains

#### Scenario: User with only refunded purchases

- **WHEN** the User's only Order is Refunded and its Ticket is Voided
- **THEN** the User is removed and the Order and Ticket remain

#### Scenario: Retry after the record failed

- **WHEN** Delete removed the identity but User.Delete failed, and Delete is called again
- **THEN** the User is removed
