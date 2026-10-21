# components/entity/checkout/get-or-create-held Specification

## Purpose
Returns a fan's current Checkout on a TicketType, or starts one when the stock and the fan's per-account limit allow, so a repeated or concurrent start never holds twice.

## Requirements

### Requirement: At most one holding checkout per fan and ticket type

GetOrCreateHeld SHALL take a TicketType, a User, a count and a time:
- When the User has a holding Checkout for the TicketType with the same count, it SHALL return it and change nothing.
- Otherwise it SHALL create a new Held Checkout, but only when the TicketType's remaining count at that time, counting the User's own holding Checkout for the TicketType as free, is at least the count, failing with ResourceExhausted otherwise. It also requires that the count fits the TicketType's per-account limit, counting the User's Issued Tickets for the TicketType's event and the tickets on the User's Committed Checkouts for the TicketType that are not issued yet, failing with FailedPrecondition otherwise, so a charge still being issued counts against the limit.
- When it creates one, a holding Checkout of the User for the TicketType SHALL be made Released, and a Held one that is no longer holding SHALL be made Expired, in the same step. When it fails, nothing SHALL change, so the fan keeps their current hold.

Checking and creating SHALL be one indivisible step, so two concurrent calls for the same User and TicketType create at most one Checkout, and two Users asking for the last tickets hold them at most once. It SHALL return the new Checkout. It SHALL fail with NotFound when no TicketType has the id.

#### Scenario: First start
- **WHEN** a fan starts a checkout for 2 of 44 remaining tickets
- **THEN** a Held Checkout for 2 tickets is created

#### Scenario: Double tap
- **WHEN** the same fan starts a checkout for 2 tickets twice at the same time
- **THEN** both calls return the same Checkout and 2 tickets are held

#### Scenario: Count changed
- **WHEN** a fan holding 2 tickets starts again for 3 tickets and enough remain
- **THEN** the 2-ticket Checkout is Released and a Held Checkout for 3 tickets is returned

#### Scenario: Count raised when stock is short
- **WHEN** a fan holding 2 tickets starts again for 4 tickets and only their 2 plus 1 more are free
- **THEN** GetOrCreateHeld fails with ResourceExhausted and the fan still holds 2 tickets

#### Scenario: Two fans, last ticket
- **WHEN** two fans ask for the last ticket at the same time
- **THEN** exactly one of them holds it and the other's call fails with ResourceExhausted

#### Scenario: Over the per-account limit
- **WHEN** a fan who holds 3 Issued Tickets for the event asks for 2 tickets of a TicketType limited to 4
- **THEN** GetOrCreateHeld fails with FailedPrecondition and nothing is held

#### Scenario: Presale winner in the general sale
- **WHEN** a fan who won 4 tickets for the event in a presale asks for 1 ticket of the general sale's TicketType limited to 4
- **THEN** GetOrCreateHeld fails with FailedPrecondition and nothing is held

#### Scenario: Charge still being issued
- **WHEN** a fan's Committed Checkout for 4 tickets of a TicketType with a per-account limit of 4 is not issued yet and the fan starts another checkout for 1 ticket
- **THEN** GetOrCreateHeld fails with FailedPrecondition and nothing is held

#### Scenario: Unknown ticket type
- **WHEN** no TicketType has the id
- **THEN** GetOrCreateHeld fails with NotFound

### Requirement: Hold resale listings, oldest first

When asked to hold resale listings, GetOrCreateHeld SHALL work as for stock with these differences:
- It SHALL return the User's holding resale Checkout for the TicketType with the same count unchanged.
- Otherwise it SHALL create a new Held resale Checkout only when at least the count of the TicketType's listings are free at that time, not counting the User's own listings and counting the listings of the User's own holding Checkout for the TicketType as free, failing with ResourceExhausted otherwise.
- The new Checkout SHALL hold the free listings with the oldest create times, so the listing made first is sold first.
- The per-account limit, the replacement of the User's current holding Checkout, and failing without changing anything SHALL be as for stock.

Choosing and holding the listings SHALL be one indivisible step with every other hold and withdrawal of them, so two Users never hold the same listing and a withdrawn listing is never held.

#### Scenario: Oldest listing first
- **WHEN** listings were made at 10:00, 11:00 and 12:00 and are all free, and a fan starts a resale checkout for 2 tickets
- **THEN** the Checkout holds the 10:00 and 11:00 listings

#### Scenario: Own listing skipped
- **WHEN** the oldest free listing is the fan's own
- **THEN** the Checkout holds the next oldest listing of another fan

#### Scenario: Not enough free listings
- **WHEN** one listing is free and the fan asks for 2 tickets
- **THEN** GetOrCreateHeld fails with ResourceExhausted and nothing is held

#### Scenario: Two fans, last listing
- **WHEN** two fans ask for the last free listing at the same time
- **THEN** exactly one of them holds it and the other's call fails with ResourceExhausted

#### Scenario: Hold lapsed elsewhere
- **WHEN** another fan's Checkout holding a listing expired and a fan then asks for 1 ticket
- **THEN** the fan's Checkout holds that listing
