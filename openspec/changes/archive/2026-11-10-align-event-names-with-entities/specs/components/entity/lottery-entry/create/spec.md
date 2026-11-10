## MODIFIED Requirements

### Requirement: A new entry is announced with it

When Create stores a new entry, it SHALL announce the entry as entered (LotteryEntry.Entered) together with it: the entry, its Pending Order and the announcement are stored or none of them is. The announcement SHALL carry the Pending Order, which names the entry, the user and the TicketStock. When Create returns an existing entry for a card authorization an Order already holds, or fails, it SHALL announce nothing. When the announcement cannot be recorded, Create SHALL fail with Unavailable and store nothing.

#### Scenario: Entry stored

- **WHEN** Create stores an entry for a user with no entry for the sale for the event
- **THEN** one new entry is announced, carrying its Pending Order with the user and the TicketStock

#### Scenario: Same card authorization again

- **WHEN** Create is called with a card authorization an Order already holds
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** Create would store an entry and the announcement cannot be recorded
- **THEN** Create fails with Unavailable and no entry or Order is stored
