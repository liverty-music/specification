# Spec Delta

## Purpose

Returns a fan's current checkout on a TicketSale, or starts one when the stock and the fan's limit allow, so a repeated or concurrent start never holds twice.

## ADDED Requirements

### Requirement: At most one holding reservation per fan and sale

GetOrCreateHeld SHALL take a TicketSale, a User, a count and a time:
- When the User has a holding Reservation for the sale with the same count, it SHALL return it and change nothing.
- Otherwise it SHALL create a new Held Reservation, but only when the sale's remaining count at that time, counting the User's own holding Reservation for the sale as free, is at least the count, failing with ResourceExhausted otherwise. It also requires that the User's tickets on the sale's Committed and Completed Reservations plus the count do not exceed the per-account limit, failing with FailedPrecondition otherwise.
- When it creates one, a holding Reservation of the User for the sale SHALL be made Released, and a Held one that is no longer holding SHALL be made Expired, in the same step. When it fails, nothing SHALL change, so the fan keeps their current hold.

Checking and creating SHALL be one indivisible step, so two concurrent calls for the same User and sale create at most one Reservation, and two Users asking for the last tickets hold them at most once. It SHALL return the new Reservation. It SHALL fail with NotFound when no TicketSale has the id.

#### Scenario: First start

- **WHEN** a fan starts a checkout for 2 of 44 remaining tickets
- **THEN** a Held Reservation for 2 tickets is created

#### Scenario: Double tap

- **WHEN** the same fan starts a checkout for 2 tickets twice at the same time
- **THEN** both calls return the same Reservation and 2 tickets are held

#### Scenario: Count changed

- **WHEN** a fan holding 2 tickets starts again for 3 tickets and enough remain
- **THEN** the 2-ticket Reservation is Released and a Held Reservation for 3 tickets is returned

#### Scenario: Count raised when stock is short

- **WHEN** a fan holding 2 tickets starts again for 4 tickets and only their 2 plus 1 more are free
- **THEN** GetOrCreateHeld fails with ResourceExhausted and the fan still holds 2 tickets

#### Scenario: Two fans, last ticket

- **WHEN** two fans ask for the last ticket at the same time
- **THEN** exactly one of them holds it and the other's call fails with ResourceExhausted

#### Scenario: Over the per-account limit

- **WHEN** a fan who bought 3 tickets of a sale limited to 4 asks for 2 more
- **THEN** GetOrCreateHeld fails with FailedPrecondition and nothing is held
