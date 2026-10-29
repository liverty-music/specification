# components/entity/lottery-entry Specification

## Purpose

A LotteryEntry is how one fan's Order takes part in a Lottery TicketSale: a request for a companion group of tickets of the Order's TicketStock, allocated all-or-nothing, paid by the card authorization placed on the fan's card for the Order's amount until the draw. It is made when the fan confirms after authorizing their card, and takes part in the draw from then on. A fan enters a sale at most once for each event it names. The fan's 本人確認 (identity check) details are the User's full name and phone number.

| attribute | meaning | constraint |
|-----------|---------|------------|
| id | the entry's identity | required, assigned on creation |
| order | the Order it enters | required; one LotteryEntry per Order |
| sale | the Lottery TicketSale entered | required; one entry per sale, event and user |
| state | lifecycle | Entered, Won or Lost |
| draw position | the entry's position in its sale's random draw order for its TicketStock | absent before the draw; set only by the draw |
| loss email send time | when the email telling the fan the entry lost was sent | absent until sent; set once |

```mermaid
erDiagram
  Order ||--o| LotteryEntry : "is entered as"
  TicketSale ||--o{ LotteryEntry : "receives"
```

```mermaid
stateDiagram-v2
  [*] --> Entered
  Entered --> Won
  Entered --> Lost
  Won --> Lost
  Won --> [*]
  Lost --> [*]
```

## Requirements

### Requirement: A new entry is Entered

A LotteryEntry SHALL be created in state Entered, without a draw position, for an Order that has its card authorization.

#### Scenario: New entry
- **WHEN** a LotteryEntry is created
- **THEN** its state is Entered, its Order has its card authorization and it has no draw position

### Requirement: Sale of an entry

A LotteryEntry SHALL belong to a Lottery sale that names its Order's event.

#### Scenario: Lottery sale of the event
- **WHEN** a LotteryEntry belongs to a Lottery sale that names the event of its Order's TicketStock
- **THEN** it is valid

#### Scenario: First-come sale
- **WHEN** a LotteryEntry belongs to a FirstCome sale
- **THEN** it is invalid
