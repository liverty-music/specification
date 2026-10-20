## ADDED Requirements

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
