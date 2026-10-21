## MODIFIED Requirements

### Requirement: A new checkout holds for 15 minutes

A new Checkout SHALL start Held, with a hold expiry 15 minutes after its create time and an amount equal to the ticket type's price times its ticket count. A resale Checkout's hold expiry SHALL instead be the earlier of 15 minutes after its create time and the resale deadline of its TicketType's event, so that no resale hold lasts into admission.

#### Scenario: New checkout
- **WHEN** a fan starts a checkout for 2 tickets of a TicketType priced 3000 yen at 18:00
- **THEN** the Checkout is Held, its amount is 6000 yen and its hold expires at 18:15

#### Scenario: Resale checkout long before the deadline
- **WHEN** a fan starts a resale checkout for 1 ticket priced 5000 yen at 12:00 and the resale deadline is 15:00
- **THEN** the Checkout is Held, its amount is 5000 yen and its hold expires at 12:15

#### Scenario: Resale checkout just before the deadline
- **WHEN** a fan starts a resale checkout at 14:50 and the resale deadline is 15:00
- **THEN** its hold expires at 15:00

## ADDED Requirements

### Requirement: A resale checkout holds listings

A Checkout SHALL be a resale Checkout when it holds ResaleListings instead of its TicketType's stock. A resale Checkout SHALL hold exactly as many listings as its ticket count, all of its TicketType, and none whose user is the Checkout's user. A Checkout that holds stock SHALL hold no listing.

#### Scenario: Two listings of two fans
- **WHEN** a resale Checkout for 2 tickets holds one listing of each of two other fans
- **THEN** it is valid

#### Scenario: The fan's own listing
- **WHEN** a resale Checkout holds a listing whose user is the Checkout's user
- **THEN** it is invalid
