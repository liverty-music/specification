# components/entity/lottery-entry/create Specification

## Purpose
LotteryEntry.Create stores a fan's new Entered entry with its card authorization and referral code: at most one per account, sale and event, and only before the sale's end time.

## Requirements

### Requirement: One entry per account, sale and event, before the end time

Create SHALL take a Lottery TicketSale, a TicketStock of an event the sale names, a user, a ticket count, a card authorization and an optional ReferralCode, store a new Entered entry together with its Pending Order for the TicketStock, the user, the count, the card authorization and the ReferralCode, and return them. It SHALL fail, storing nothing:
- with AlreadyExists when the user already has an entry for the sale for the TicketStock's event, of any TicketStock of that event;
- with FailedPrecondition when the application does not fit the stock's event for the user, with the tickets the user holds for the event as Order.GetHeldForEvent counts them;
- with FailedPrecondition when the sale or the TicketStock does not exist, or the sale's end time has passed at the moment the entry is stored.

When an Order already holds the given card authorization, Create SHALL return that Order and its entry and store nothing, also after the end time. Checking and storing SHALL be one indivisible step with every other creation of an Order by the same user, so two concurrent calls for the same user, sale and event, or for the same card authorization, store one entry, the user never holds more than the event allows, and no entry is stored after the end time.

#### Scenario: Entry stored
- **WHEN** Create is called for a user with no entry for the sale for the event, 2 tickets, a card authorization and the code `member-a`
- **THEN** an Entered entry and its Pending Order for 2 tickets with that card authorization and the code `member-a` are stored and returned

#### Scenario: Second entry
- **WHEN** the user already has an Entered, Won or Lost entry for the sale for the same event, of any TicketStock
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Double tap
- **WHEN** Create is called twice at the same time for the same user, sale and event
- **THEN** one entry is stored and the other call fails with AlreadyExists

#### Scenario: Another date of a tour presale
- **WHEN** the user has an entry in a sale for one event and enters the same sale for another event it names
- **THEN** a second entry and its Pending Order are stored

#### Scenario: Same card authorization again
- **WHEN** Create is called with a card authorization an Order already holds, before or after the end time, or twice at the same time
- **THEN** that one Order and its entry are returned and nothing else is stored

#### Scenario: Presale winner in a general lottery
- **WHEN** the user's Order for 4 tickets of the event won in a presale and the event's per-account limit is 4
- **THEN** Create fails with FailedPrecondition and stores nothing

#### Scenario: Another seat type
- **WHEN** the user holds 2 S席 tickets for the event and enters for A席
- **THEN** Create fails with FailedPrecondition and stores nothing

#### Scenario: After the end time
- **WHEN** Create is called after the sale's end time
- **THEN** it fails with FailedPrecondition and stores nothing

#### Scenario: Unknown ticket stock
- **WHEN** the TicketStock does not exist
- **THEN** Create fails with FailedPrecondition and stores nothing
