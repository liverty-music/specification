# components/entity/checkout/get-or-create-held Specification

## Purpose
Returns a fan's current Checkout on a TicketType, or starts one when the stock and the fan's per-account limit allow, so a repeated or concurrent start never holds twice.

## Requirements

### Requirement: At most one holding checkout per fan and ticket stock

GetOrCreateHeld SHALL take a TicketStock, a FirstCome TicketSale that names the stock's event, a User, a count, an optional ReferralCode and a time:
- When the User has a holding Checkout of the sale for the TicketStock whose Order has the same count, it SHALL return it and its Order and change nothing.
- Otherwise it SHALL create a new Held Checkout of the sale together with its Pending Order for the TicketStock, the User, the count and the ReferralCode, but only when the TicketStock's remaining count at that time, counting the User's own holding Checkout for the TicketStock as free, is at least the count, failing with ResourceExhausted otherwise. It also requires that the application fits the stock's event for the User, with the tickets the User holds for the event as Order.GetHeldForEvent counts them, leaving out the Order of the User's own holding Checkout that is replaced, failing with FailedPrecondition otherwise.
- When it creates one, a holding Checkout of the User for the TicketStock SHALL be made Released, a Held one that is no longer holding SHALL be made Expired, and the Order of each SHALL be made Void, in the same step. When it fails, nothing SHALL change, so the fan keeps their current hold.

Checking and creating SHALL be one indivisible step with every other creation of an Order by the same User, so two concurrent calls by the same User, for the same or another TicketStock of the event, never let the User hold more than the event allows, and two Users asking for the last tickets hold them at most once. It SHALL return the new Checkout and its Order. It SHALL fail with NotFound when no TicketStock has the id.

#### Scenario: First start
- **WHEN** a fan starts a checkout for 2 of 44 remaining tickets
- **THEN** a Held Checkout and its Pending Order for 2 tickets are created

#### Scenario: Double tap
- **WHEN** the same fan starts a checkout for 2 tickets twice at the same time
- **THEN** both calls return the same Checkout and 2 tickets are held

#### Scenario: Count changed
- **WHEN** a fan holding 2 tickets starts again for 3 tickets and enough remain
- **THEN** the 2-ticket Checkout is Released, its Order is Void and a Held Checkout for 3 tickets is returned

#### Scenario: Count raised when stock is short
- **WHEN** a fan holding 2 tickets starts again for 4 tickets and only their 2 plus 1 more are free
- **THEN** GetOrCreateHeld fails with ResourceExhausted and the fan still holds 2 tickets

#### Scenario: Two fans, last ticket
- **WHEN** two fans ask for the last ticket at the same time
- **THEN** exactly one of them holds it and the other's call fails with ResourceExhausted

#### Scenario: Over the per-account limit
- **WHEN** a fan who holds 3 Issued Tickets for an event with a per-account limit of 4 asks for 2 tickets
- **THEN** GetOrCreateHeld fails with FailedPrecondition and nothing is held

#### Scenario: Presale winner in the general sale
- **WHEN** a fan whose Order for 4 tickets won in the event's presale, and is not yet issued, asks for 1 ticket and the event's limit is 4
- **THEN** GetOrCreateHeld fails with FailedPrecondition and nothing is held

#### Scenario: Another seat type
- **WHEN** a fan who holds 2 S席 Tickets for the event asks for 1 A席 ticket
- **THEN** GetOrCreateHeld fails with FailedPrecondition and nothing is held

#### Scenario: Two stocks at once
- **WHEN** a fan with a per-account limit of 4 asks for 3 S席 and 3 A席 tickets of the same event at the same time
- **THEN** at most one of the calls creates a Checkout and the other fails with FailedPrecondition

#### Scenario: Unknown ticket stock
- **WHEN** no TicketStock has the id
- **THEN** GetOrCreateHeld fails with NotFound
