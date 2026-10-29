# components/entity/order/get-held-for-event Specification

## Purpose
Reads the tickets an account holds for one event and their SeatType, so an application can be checked against the event's per-account limit and seat type rule.

## Requirements

### Requirement: Tickets an account holds for an event

GetHeldForEvent SHALL take a user, an event and optionally one Order to leave out, and return the number of tickets the user holds for the event: the Issued Tickets of the user's Paid Orders for the event plus the ticket counts of the user's Pending Orders for the event that still hold or may still receive tickets: a Pending Order whose Checkout is holding or Committed, or whose LotteryEntry is Entered or Won, and, when that number is above 0, the SeatType of the Orders counted. The Order to leave out, when given, SHALL NOT be counted; it is the Order of the user's own holding Checkout that the new application resumes or replaces. It SHALL return a count of 0 and no SeatType when nothing is counted, also when the user's only Paid Order has every Ticket Voided by a resale. Void and Refunded Orders, Pending Orders whose Checkout's hold has lapsed, and Tickets that are Voided, SHALL NOT be counted.

#### Scenario: Paid and pending orders
- **WHEN** the user has a Paid Order with 2 Issued S席 Tickets and a Pending Order for 1 S席 ticket for the event
- **THEN** GetHeldForEvent returns 3 and S席

#### Scenario: Entered lottery entry
- **WHEN** the user's only Order for the event is Pending with an Entered LotteryEntry for 2 tickets
- **THEN** GetHeldForEvent returns 2

#### Scenario: Resold ticket
- **WHEN** the user's Paid Order has 2 Tickets, one of them Voided by a resale
- **THEN** GetHeldForEvent returns 1

#### Scenario: Every ticket resold
- **WHEN** the user's only Order for the event is Paid with 2 S席 Tickets, both Voided by a resale
- **THEN** GetHeldForEvent returns 0 and no SeatType

#### Scenario: Void order
- **WHEN** the user's only Order for the event is Void
- **THEN** GetHeldForEvent returns 0 and no SeatType

#### Scenario: Another event
- **WHEN** the user's only Paid Order is for another event of the same Series
- **THEN** GetHeldForEvent returns 0 and no SeatType

#### Scenario: Holding checkout left out
- **WHEN** the user's only Order for the event is Pending with a holding Checkout for 2 tickets, and that Order is given to leave out
- **THEN** GetHeldForEvent returns 0 and no SeatType

#### Scenario: Lapsed hold
- **WHEN** the user's only Order for the event is Pending with a Held Checkout for 2 tickets whose hold expired a minute ago
- **THEN** GetHeldForEvent returns 0 and no SeatType
